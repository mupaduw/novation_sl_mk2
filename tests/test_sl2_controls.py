#!python

"""
tests for control panel
"""
import unittest
from mididings.event import *
from mididings import *
from novation_sl_mk2.sl2_controls import SL2Controls
from novation_sl_mk2.sl2_panel import Panel, DevicePanel
# from novation import sl2_display as sl2

from novation_sl_mk2.control import BaseControl, RotaryControl, RotaryRingControl, map_range, ButtonControl

class TestSL2Controls(unittest.TestCase):


    def setUp(self):
        self.sl2_port = OutputTemplate(1, 1)
        self.inst_port = OutputTemplate(12, 1)
        self.inst2_port = OutputTemplate(13, 2)

    def test_SL2Controls_display(self):
        sl2control = SL2Controls("test", sl2_out=self.sl2_port(), instrument_out=self.inst_port()) 
        b3panel = DevicePanel("Kontakt B3 Organ",  self.sl2_port(), output=self.inst_port(), 
            column_count=8, row_count=3)
        sl2control.add_device_panel(b3panel)  
        assert [n for n in sl2control.active_control_names] == ["" for x in range(8)]

    def test_control_panel_display(self):
        sl2control = SL2Controls("SL2Controls", sl2_out=self.sl2_port(), instrument_out=self.inst_port()) 
        b3panel = DevicePanel("Kontakt B3 Organ",  self.sl2_port(), output=self.inst_port(), 
            column_count=3, row_count=3)
        b3panel.add_row2_control("LesRate", 0, 23)
        sl2control.add_device_panel(b3panel)  
        # B3panel.device_panel.set_active_row(1)
        assert [n for n in sl2control.active_control_names] == ["LesRate","", ""] #+ ["" for x in range(7)]

    def test_control_panel_execute(self):
        sl2control = SL2Controls("B3Panel", sl2_out=self.sl2_port(), instrument_out=self.inst_port()) 
        b3panel = DevicePanel(
            "B3 Panel",  self.sl2_port(), output=self.inst_port(), 
            column_count=3, row_count=3, column_start=0, row_start=0)
        b3panel.add_row2_control("LesRate", 0, 22)
        sl2control.add_device_panel(b3panel)  
        
        # assert B3panel.device_panel.active_control_names == ["LesRate",] + ["" for x in range(7)]
        assert [x for x in sl2control.execute(CtrlEvent(1, 1, 56, 63))][:2] == [
            CtrlEvent(12, 1, 22, 63), CtrlEvent(1, 1, 112, 5)]

    def test_control_panel_dual_device(self):
        sl2control = SL2Controls("SL2Controls", sl2_out=self.sl2_port(), instrument_out=None) 
        dev_panel_0 = DevicePanel(
            "B3 Panel",  self.sl2_port(), output=self.inst_port(), 
            column_count=3, row_count=3, column_start=0, row_start=0)
        dev_panel_0.add_row2_control("LesRate", 0, 22)
        dev_panel_1 = DevicePanel(
            "WeirdFishesPanel",  self.sl2_port(), output=self.inst2_port(), 
            column_count=3, row_count=3, column_start=4, row_start=0)  
        dev_panel_1.add_row2_control("SwimRate", 4, 99)

        sl2control.add_device_panel(dev_panel_0) 
        sl2control.add_device_panel(dev_panel_1) 
        
        #Display
        assert [n for n in sl2control.active_control_names] == ["LesRate","", "", "SwimRate", "", ""]
        
        #events handling
        leslie_twist = CtrlEvent(1, 1, 56, 93)
        swim_twist = CtrlEvent(1, 1, 60, 40)

        assert [x for x in sl2control.execute(leslie_twist)] == [
            CtrlEvent(12, 1, 22, 93), 
            CtrlEvent(1, 1, 112, 8)]

        assert [x for x in sl2control.execute(swim_twist)] == [
            CtrlEvent(13, 2, 99, 40), 
            CtrlEvent(1, 1, 116, 3)]

