#!python
"""
mididings controls
"""

import mididings.event
from mididings import CTRL
from itertools import chain


def map_range(arg, arg_lower, arg_upper, val_lower=0, val_upper=127):
    """
    map arg, between arg_lower, arg_upper onto range val_lower=0, val_upper=127
    >
    > assert map_range(127, 0, 127, 0, 11) == 11
    """
    if (arg <= arg_lower):
        return val_lower
    elif (arg >= arg_upper):
        return val_upper
    else:
        dx = arg_upper - arg_lower * 1.0
        dy = val_upper - val_lower * 1.0
        return int((dy / dx) * (arg - arg_lower) + val_lower)

def execute_guard(func):

    def wrapper(*arg, **kwarg):
        # print('wrapped', arg, kwarg)
        ev = arg[1]
        self = arg[0]
        if not isinstance(ev, mididings.event.MidiEvent):
            return []
        elif not (ev.type == CTRL and ev.ctrl == self._ccin):
            return []   
        else:
            self._sl2_port = self._ports[0] if self._ports[0] else ev.port
            return func(*arg, **kwarg)
    
    return wrapper 


class BaseControl(object):

    def __init__(self, name, ccin, ccout=None, ports=None, inst_channel=None):
        self._name = name
        self._ccin = ccin
        self._ccout = ccout or ccin
        self._value = 0
        self._ports = ports or (None, None)
        self._chan = inst_channel
        self._sl2_port = None 

    def display(self):
        return self._name #, str(self._value))

    @execute_guard
    def execute(self, ev, **kwargs):
        self._value = ev.value
        ins_port = self._ports[1] if self._ports[1] else ev.port
        ins_chan = self._chan if self._chan else ev.channel

        #the mapped CC
        return chain(
            (e for e in [mididings.event.CtrlEvent(ins_port, ins_chan, 
                self._ccout, self._value)]), 
            self._update_controller(ev))

class NullControl(BaseControl):

    def __init__(self):
        pass

    def display(self):
        return "" 

    def execute(self, ev, **kwargs):
        yield

class RotaryControl(BaseControl):

    def _update_controller(self, e):
        return (n for n in [])    

class RotaryRingControl(BaseControl):
    
    def __init__(self, name, ccin, ccout=None, ports=None, inst_channel=None):
        super(RotaryRingControl, self).__init__(name, ccin, ccout, ports, inst_channel)
        assert self._ccin in range(56, 72)
        self._ring_value = 0
          
    def _update_controller(self, ev): 
        #the led ring CC    
        mapped_value = map_range(ev.value, 0, 127, 0, 11)
        if not self._ring_value == mapped_value:
            self._ring_value = mapped_value
            yield mididings.event.CtrlEvent(self._sl2_port, ev.channel, 
                self._ccin + 56, mapped_value) 

class ButtonControl(BaseControl):
    """
    assume we can receive either 1 or 127 as ON value
    """
    _non_zero = 127

    def __init__(self, name, ccin, ccout=None, latching=True, ports=None, inst_channel=None):
        super(ButtonControl, self).__init__(name, ccin, ccout, ports, inst_channel)
        # assert self._ccin in range(56, 72)
        self._latching = latching
        self._latched = False

    @execute_guard
    def execute(self, ev, **kwargs):
        assert ev.value in [0, 1, 127]
        
        if not self._latching:
            return super(ButtonControl, self).execute(ev, **kwargs)

        if ev.value > 0:
            #ON event, switch latch 
            self._latched = (not self._latched)
            
            newev = mididings.event.CtrlEvent(
                ev.port, ev.channel, 
                ev.ctrl, 
                value = self._latched * self._non_zero)
            return super(ButtonControl, self).execute(newev, **kwargs)
        else:
            return (n for n in []) #empty generator

    def _update_controller(self, ev):
        yield mididings.event.CtrlEvent(self._sl2_port, ev.channel, 
                self._ccin, ev.value) 
