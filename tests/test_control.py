#!python

"""
tests for control panel
"""
import unittest
from mididings.event import *
from mididings import *
from novation_sl_mk2.control import BaseControl, RotaryControl, RotaryRingControl, map_range, ButtonControl

    
class TestControl(unittest.TestCase):

    def test_BaseControl_display(self):
        ctrl = BaseControl("Ctrl1", 62)
        assert ctrl.display() == "Ctrl1"

    def test_RotaryControl_execute(self):
        ctrl = RotaryControl("Ctrl1", 62)
        assert [x for x in ctrl.execute(CtrlEvent(1, 1, 62, 123))] == [CtrlEvent(1, 1, 62, 123)]
        assert [x for x in ctrl.execute(CtrlEvent(1, 1, 1, 123))] == []


    def test_RotaryControl_mapping_execute(self):
        ctrl = RotaryControl("Ctrl1", 62, 23, ports =(1,1))
        assert [x for x in ctrl.execute(CtrlEvent(1, 1, 62, 123))] == [CtrlEvent(1, 1, 23, 123)]
        assert [x for x in ctrl.execute(CtrlEvent(1, 1, 1, 123))] == []
        assert [x for x in ctrl.execute(CtrlEvent(1, 2, 62, 123))] == [CtrlEvent(1, 2, 23, 123)]
        # assert [x for x in ctrl.execute(CtrlEvent(1, 1, 62, 123))] == [CtrlEvent(12, 1, 23, 123)]

    def test_RotaryRingControl_mapping_execute(self):
        ctrl = RotaryRingControl("Ctrl1", 56, 23, ports=(1,1))
        assert [x for x in ctrl.execute(CtrlEvent(1, 1, 56, 0))] == [CtrlEvent(1, 1, 23, 0)]
        assert [x for x in ctrl.execute(CtrlEvent(1, 1, 56, 120))] == [
            CtrlEvent(1, 1, 23, 120), CtrlEvent(1, 1, 112, 10)]

    def test_ButtonControl_latching_execute(self):
        ctrl = ButtonControl("Ctrl1", 62, ports =(1,2))
        assert [x for x in ctrl.execute(CtrlEvent(1, 1, 62, 0))] == []
        events = ctrl.execute(CtrlEvent(1, 1, 62, 1))
        print(dir(events))
        assert next(events) == CtrlEvent(2, 1, 62, 127)
        assert next(events) == CtrlEvent(1, 1, 62, 127)
        
    def test_ButtonControl_non_latching_execute(self):
        ctrl = ButtonControl("Ctrl1", 62, latching=False, ports=(1,2))
        # assert [x for x in ctrl.execute(CtrlEvent(1, 1, 62, 0))] == []
        assert next(ctrl.execute(CtrlEvent(1, 1, 62, 127))) == CtrlEvent(2, 1, 62, 127)
        events = ctrl.execute(CtrlEvent(1, 1, 62, 0))
        assert next(events) == CtrlEvent(2, 1, 62, 0)
        assert next(events) == CtrlEvent(1, 1, 62, 0)
        

def test_map_range():
    assert map_range(127, 0, 127, 0, 11) == 11
    assert map_range(63, 0, 127, 0, 11) == 5
    assert map_range(72, 0, 127, 0, 11) == 6
    assert map_range(0, 0, 127, 0, 11) == 0

