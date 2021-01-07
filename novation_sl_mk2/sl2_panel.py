
from mididings import *
import collections
from enum import Enum
# from novation import sl2_display
from mididings.extra import Panic

from .control import BaseControl, NullControl, ButtonControl, RotaryControl, RotaryRingControl

class ControlSet(Enum):
    row1_buttons = 0
    row2_dials = 1
    row3_buttons = 2
    row4_dials = 3

class Point:

    def __init__(self, xcoord=0, ycoord=0):
        self.x = xcoord
        self.y = ycoord

    def __repr__(self):
        return "Point(x: %s, y: %s)" % (self.x, self.y) 

class Panel(object):

    def __init__(self, column_count, row_count, column_start=0, row_start=0):

        self._column_count = column_count
        self._column_start = column_start
        self._row_start = row_start
        self._row_count = row_count

        self.bottom_left = Point(self._column_start, row_start + row_count)
        self.top_right = Point(self._column_start + column_count, row_start)

        # super(SL2Controls, self).__init__()
        self._controls = collections.OrderedDict()
        self._controls[ControlSet.row1_buttons.value] = [NullControl() for x in range(self._column_count)]
        self._controls[ControlSet.row2_dials.value] = [NullControl() for x in range(self._column_count)]
        self._controls[ControlSet.row3_buttons.value] = [NullControl() for x in range(self._column_count)]
        self._controls[ControlSet.row4_dials.value] = [NullControl() for x in range(self._column_count)]
   
        #Dials by default
        self._active = ControlSet.row2_dials.value


    def __repr__(self):
        return "Panel(bot-left: %s, top-right: %s)" % (
            self.bottom_left, 
            self.top_right)

    def add_control(self, control, column, row):
        # print(column, self._column_start, self._column_count, self._column_start + self._column_count)
        assert column in range(self._column_start, self._column_start + self._column_count)
        self._controls[row][column - self._column_start] = control

    def overlap(self, other):
        # print ( self, other) #", row_overlap(self, other), col_overlap(self, other))   
        return not (self.top_right.x <= other.bottom_left.x or \
            self.bottom_left.x >= other.top_right.x or \
            self.top_right.y >= other.bottom_left.y or \
            self.bottom_left.y <= other.top_right.y) 

    @property
    def active_control_names(self):
        return [ctrl.display() for ctrl in self._controls[self._active]]
    
    def set_active_row(self, row):
        # print("Set active row:", row)
        self._active = list(self._controls.keys())[row]

    @property
    def active_controls(self):
        for control in self._controls[self._active]:
            # if not isinstance(control, NullControl):
            yield control
            
    @property
    def all_controls(self):
        for control in self._controls[ControlSet.row1_buttons.value] +\
             self._controls[ControlSet.row2_dials.value] +\
             self._controls[ControlSet.row3_buttons.value]  +\
             self._controls[ControlSet.row4_dials.value]:
            # if not isinstance(control, NullControl):
            yield control


class DevicePanel(Panel):
    """
    Provide control panel for an associated midi device
    """

    def __init__(self, name, sl2_out, output, column_count, row_count, column_start=0, row_start=0):
        
        super(DevicePanel, self).__init__(column_count, row_count, column_start, row_start)
        
        self._name = name     

        #mididings OutputTemplate returns a list/chain of channel/port 
        assert isinstance(output, list) 
        assert isinstance(sl2_out, list) 

        output_str = str(output[-1]) #.pop())
        self._port = int(output_str.split('port=')[1].split(') >>')[0])
        self._channel = int(output_str.split('channel=')[1].split(')]')[0])
        self._sl2_port = int(str(sl2_out[-1]).split('port=')[1].split(') >>')[0])

    @property
    def name(self):
        return self._name

    @property
    def channel(self):
        return self._channel

    @property
    def port(self):
        return self._port

    @property
    def column_count(self):
        return self._column_count

    def add_row2_control(self, name, column, ccout=None):
        ctrl_column = column #+ self._column_start
        if not ccout:
            ccout = 8 + ctrl_column
        # print('add row2', 56 + ctrl_column, ccout, column)
        self.add_control(
            RotaryRingControl(name, 
                56 + ctrl_column, ccout, 
                ports = (self._sl2_port, self._port), 
                inst_channel = self._channel),
            column = column,
            row = ControlSet.row2_dials.value)

    def add_row4_control(self, name, column, ccout=None):
        ctrl_column = column# + self._column_start
        if not ccout:
            ccout = 8 + ctrl_column 
        self.add_control(
            RotaryControl(
                name, 
                8 + ctrl_column, ccout, 
                ports = (self._sl2_port, self._port), 
                inst_channel = self._channel),
            column = column,
            row = ControlSet.row4_dials.value)        
    
    def add_row3_control(self, name, column, ccout=None, latching=True):
        ctrl_column = column #+ self._column_start
        if not ccout:
            ccout = 32 + ctrl_column
        self.add_control(       
            ButtonControl(
                name, 
                32 + ctrl_column, ccout, 
                latching=latching,
                ports = (self._sl2_port, self._port), 
                inst_channel = self._channel),
            column = column,
            row = ControlSet.row3_buttons.value) 

class PanelLayout(object):
    """
    manage setout of panels, no overlaps, act as a generator for all the panels
    1) do not allow overlapping panels
    2) a panel covers min/max region, regardless if all controls in the region are used
    """

    def __init__(self):
        self.panels = []

    def __iter__(self):
        for panel in self.panels:
            # value, self.a, self.b = self.a, self.b, self.a+self.b
            yield panel

    def append(self, panel):
        for p in self.panels:
            if panel.overlap(p):
                raise ValueError("overlapping panels")
        self.panels.append(panel)



