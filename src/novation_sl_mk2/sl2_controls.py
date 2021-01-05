
from mididings.event import CtrlEvent
import mididings.event
from mididings import *
import collections
from enum import Enum
from . import sl2_display
from mididings.extra import Panic

from .control import BaseControl, NullControl, ButtonControl, RotaryControl, RotaryRingControl
from .sl2_panel import DevicePanel, PanelLayout, ControlSet


class SL2Controls(object):

    def __init__(self, name, sl2_out=None, instrument_out=None):
               
        self._sl2_out = sl2_out
        self._sl2_port = int(str(sl2_out[-1]).split('port=')[1].split(') >>')[0])

        # self._instrument = instrument_out
        self.name = name
        self.scene_name = name

        self.panel_layout = PanelLayout()

        #Dials by default
        self._active = ControlSet.row2_dials
   
        #configure the LCD
        self._display = sl2_display.Display()
        row1  = sl2_display.DisplayRow()
        row1.add_cell(72, 'L', name)
        self._display.scene_row = row1

    def add_device_panel(self, panel):

        self.panel_layout.append(panel)
        # print('panel.top_right.x', panel.top_right.x)
        self._display.panel_row.add_cell(9 * panel.column_count, 'L', panel.name)
        return panel

    @property
    def device_panels(self):
        return self.panel_layout 

    @property
    def active_control_names(self):
        for panel in self.device_panels:
            for ctrl in panel.active_controls:
                yield ctrl.display()

    @property
    def active_controls(self):
        for panel in self.device_panels:
            for ctrl in panel.active_controls:
                yield ctrl
   
    @property
    def display(self):
        return self._display

    def execute(self, ev, **kwargs):
        '''
        event handler
        '''
        #manage display
        # print('execute', ev)
        if ev.ctrl == 84 and ev.value == 1:
            print('Panic!')
            Panic()
            return        

        #scroll display
        if ev.ctrl == 88 and ev.value == 1:
            self.display.scroll_up()
            for event in self._update_display(ev, **kwargs):
                yield event
            # yield CtrlEvent(self._sl2_port, channel=1, ctrl=89, value=127)
            return

        if ev.ctrl == 89 and ev.value == 1:
            self.display.scroll_down()
            for event in self._update_display(ev, **kwargs):
                yield event
            # yield CtrlEvent(self._sl2_port, channel=1, ctrl=89, value=127)
            return
            
        if ev.ctrl in range(80, 84) and ev.value == 1:
            self.display.ensure_ctrls_visible()
            for panel in self.device_panels:  
                panel.set_active_row(ev.ctrl-80)
            for event in self._update_display(ev, **kwargs):
                yield event

            # udpate button
            for ctrl in range(80, 84):
                yield CtrlEvent(self._sl2_port, channel=1, ctrl=ctrl, value=0)
            yield CtrlEvent(self._sl2_port, channel=1, ctrl=ev.ctrl, value=127)
            return

        #perform any CC work
        for panel in self.device_panels:
            for control in panel.all_controls:        
                # for control in self._device_panel.all_controls:
                for event in control.execute(ev, **kwargs):
                    if event:
                        yield event

    def initialise_display(self):
        # print("SL2Controls.initialise_display")
        self._display.scene_row.set_cell(0, self.scene_name)
        idx = 0
        for panel in self.device_panels:
            # print(panel, panel.name)         
            self._display.panel_row.set_cell(idx, panel.name)
            idx += 1
            
    def _update_display(self, ev, **kwargs):    
        #update display
        # print('_update_display')
        idx = 0
        for panel in self.device_panels:
            for ctrl in panel.active_controls:
                self._display.ctrl_row.set_cell(idx, ctrl.display())
                idx += 1
        
        for sysex in self._display.update():
           yield mididings.event.SysExEvent(self._sl2_port, sysex)

