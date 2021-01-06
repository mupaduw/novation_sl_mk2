#!python

"""
tests for control panel
"""
import unittest
from mididings.event import *
from mididings import *
from novation_sl_mk2.sl2_panel import Panel, DevicePanel
# from novation import sl2_display as sl2

from novation_sl_mk2.control import BaseControl, RotaryControl, RotaryRingControl, map_range, ButtonControl


class TestDevicePanel(unittest.TestCase):

    def setUp(self):
        self.sl2_port = OutputTemplate(1, 1)
        self.inst_port = OutputTemplate(port=12, channel=10)

    def test_init(self):
        ics = DevicePanel("Kontakt B3 Organ", self.sl2_port(), output=self.inst_port(), 
            column_count=8, row_count=3)  
        assert ics.channel == 10
        assert ics.port == 12
        assert ics.name == "Kontakt B3 Organ"
        assert ics.column_count == 8

class TestPanelLayout(unittest.TestCase):

    def test_col_overlap(self):
        p1 = Panel(column_count=2, row_count=1, column_start=0, row_start=0)
        p2 = Panel(column_count=2, row_count=1, column_start=1, row_start=0)
        print( 'bl', p1.bottom_left, 'tr', p1.top_right)
        assert p1.overlap(p2) == True

    def test_no_overlap_both(self):
        p1 = Panel(column_count=2, row_count=1, column_start=0, row_start=0)
        p2 = Panel(column_count=2, row_count=1, column_start=2, row_start=1)
        assert p1.overlap(p2) == False

    def test_overlap_both_axis(self):
        p1 = Panel(column_count=2, row_count=2, column_start=0, row_start=0)
        p2 = Panel(column_count=1, row_count=1, column_start=1, row_start=1)
        assert p1.overlap(p2) == True

    def test_row_no_overlap(self):
        p1 = Panel(column_count=2, row_count=2, column_start=0, row_start=0)
        p2 = Panel(column_count=2, row_count=1, column_start=0, row_start=3)
        assert p1.overlap(p2) == False


    def test_row_overlap(self):
        p1 = Panel(column_count=2, row_count=2, column_start=0, row_start=0)
        p2 = Panel(column_count=2, row_count=2, column_start=4, row_start=0)
        assert p1.overlap(p2) == False
        p3 = Panel(column_count=8, row_count=1, column_start=0, row_start=3)
        assert p3.overlap(p2) == False


