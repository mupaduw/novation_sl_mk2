#!python

"""
tests for sl2 display manager
"""
import unittest
from novation_sl_mk2 import sl2_display as sl2

class TestDisplay(unittest.TestCase):

    def setUp(self):
        self.display = sl2.Display()

    def notest_reset(self):
        self.assertEqual(self.display.reset_display(), None)

    def test_display(self):
        row1 = sl2.DisplayRow()
        row2 = sl2.DisplayRow()
        row1.add_cell(72, 'L', 'ROW1')
        for n in range(8):
            row2.add_cell(9, 'L', str(n))
        # self.display.set_display_mode(row1, row2)
        self.display.scene_row = row1
        self.display.ctrl_row = row2
        self.display.set_mode(sl2.DisplayMode.scene_ctrl)
        assert self.display.display()[0] == "ROW1" + " " * 68
        assert self.display.display()[1][:10] == "0" + " " * 8 + "1"
        assert self.display.display()[1][-9:] == "7" + " " * 8


class TestDisplayCell(unittest.TestCase):
    
    def test_left_odd_odd(self):
        cell = sl2.DisplayCell(5, 'L', '123')
        assert cell.display() == '123  '

    def test_left_odd_even(self):
        cell = sl2.DisplayCell(5, 'L', '1234')
        assert cell.display() == '1234 '

    def test_mid_odd_odd(self):
        cell = sl2.DisplayCell(5, 'C', '123')
        assert cell.display() == ' 123 '

    def test_mid_odd_even(self):
        cell = sl2.DisplayCell(5, 'C', '1234')
        print('[' + cell.display() + ']')
        assert cell.display() == ' 1234'

    def test_mid_even_odd(self):
        cell = sl2.DisplayCell(6, 'C', '123')
        assert cell.display() == '  123 '


    def test_mid_even_even(self):
        cell = sl2.DisplayCell(6, 'C', '1234')
        assert cell.display() == ' 1234 '


    def test_long_mid_odd_even(self):
        cell = sl2.DisplayCell(5, 'C', '123456')
        assert cell.display() == '12345'

    def test_long_mid_odd_odd(self):
        cell = sl2.DisplayCell(5, 'C', '1234567')
        assert cell.display() == '12345'


class TestDisplayRow(unittest.TestCase):
    
    def setUp(self):
        self.display_row  = sl2.DisplayRow()

    def test_add_single_cell(self):
        self.display_row.add_cell(64, 'L')
        self.display_row.set_cell(0, '*' * 60)
        assert self.display_row.display() == '*' * 60 + ' ' * 4

    def test_add_overlarge_cell(self):
        with self.assertRaises(ValueError) as context:
            self.display_row.add_cell(73, 'L')           
        self.assertTrue('72'in str(context.exception)) #, 'total cell width exceeds limit 72.')

    def test_add_multi_cells_left(self):
        for n in range(2):
            self.display_row.add_cell(8, 'L')
            self.display_row.set_cell(n, '*' * 4)
        assert self.display_row.display() == '****    ' * 2

    def test_add_multi_cells_mid(self):
        for n in range(2):
            self.display_row.add_cell(8, 'C')
            self.display_row.set_cell(n, '1234')
        assert self.display_row.display() == '  1234  ' * 2

    def test_add_multi_cells_mid_odd(self):
        for n in range(2):
            self.display_row.add_cell(8, 'C')
            self.display_row.set_cell(n, '12345')
        assert self.display_row.display() == '  12345 ' * 2

    def test_add_multi_cells_right(self):
        for n in range(2):
            self.display_row.add_cell(8, 'R')
            self.display_row.set_cell(n, '*' * 4)
        assert self.display_row.display() == '    ****' * 2
