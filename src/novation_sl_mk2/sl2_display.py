from enum import Enum

SYSEX_HEADER = "F0 00 20 29 03 03 12 00 04 00 "
SYSEX_AUTOMAP_ON = SYSEX_HEADER + "01 01 F7";
SYSEX_AUTOMAP_OFF = SYSEX_HEADER + "01 00 F7";

def writeString(row, text):
    
    def paddedInt(n):
        return "%02d" % n
    
    def str2HexList(s):
        res = [] 
        for i in s:
            res.append(i.encode('hex'))
        return res
    return SYSEX_HEADER + " ".join(["02", "01", "00"] + [paddedInt(row), "04"] + str2HexList(text) + ["00", "F7"])


def left_align(value, width):
    value = value.strip() + " " * width
    return value[:width]

def right_align(value, width):
    value = " " * width + value.strip()
    return value[(-1 * width):]

def mid_align(value, width):
    value = value.strip()
    if len(value) == width:
        return value
    elif len(value) > width:
        return left_align(value, width)
    
    pad = " " * int(width/2)
    #padding
    value = pad + value.strip() + pad

    #no long values!
    # middle = (width, len(value))/2 
    middle = len(value)/2 + 1
    if (width % 2):
        middle -= 1
    # if not len(value) %2:
    #   middle -=1
    
    oddpad = '' if (width % 2 == 0) else ' '
    evenpad = ' ' if (width % 2 == 0) else ''

    # value =  
    value = value[int(middle - width/2):int(middle + width/2)]
    value = evenpad + value + oddpad
    return value[:width]

class DisplayCell():
    '''
    contain display data for a cell of fixed width
    restrict output to available, width, 
    set alignment
    '''

    def __init__(self, width, align, value=""):
        if not align in 'CRL':
            raise ValueError("Expecting align to be one of 'C', 'R', 'L'.")
        self._width = width
        self._align = align 
        self.set_value(value)

    def display(self, value=None):
        if value:
            self.set_value(value)
        if 'L' in self._align.upper():
            return left_align(self._value, self._width)
        elif 'C' in self._align.upper():
            return mid_align(self._value.strip(), self._width)
        else:
            return right_align(self._value, self._width)

    def set_value(self, value):
        self._value = value

    @property
    def width(self):
        return self._width


class DisplayRow():
    ''' 
    container for DisplayCells
    pad output if Display cells width < 128
    error if sium of widths > 128
    ''' 
    def __init__(self):
        self._cells = []

    def add_cell(self, width, align,  value=""):
        self._cells.append(DisplayCell(width, align, value))
        # print('DisplayRow.add_cell', width, align, value)
        if sum([cell.width for cell in self._cells]) > 72:
            raise ValueError('total cell width exceeds limit 72.')

    def set_cell(self, cell, value):
        # print('DisplayRow.set_cell', cell, value)
        self._cells[cell].set_value(value)
        assert self._cells[cell]._value == value 

    def display(self):
        # print('DisplayRow.display()', [(x.display(), x._value) for x in self._cells])
        return ''.join([x.display() for x in self._cells])


class DisplayMode(Enum):
    scene_panel = 0
    scene_ctrl = 1
    panel_ctrl = 2

class Display():
    
    def __init__(self):
        pass
        self.scene_row = DisplayRow()
        self.panel_row = DisplayRow()
        self.ctrl_row = DisplayRow()

        self.mode = DisplayMode.scene_panel

        for n in range(8):
            self.ctrl_row.add_cell(9, 'L', str(n) + ('.' * 6))
 
    def ensure_ctrls_visible(self):
        if self.mode == DisplayMode.scene_panel:
            self.mode = DisplayMode.scene_ctrl

    def scroll_down(self):
        if self.mode in [DisplayMode.scene_panel, DisplayMode.scene_ctrl]:
            self.mode = DisplayMode.panel_ctrl

    def scroll_up(self):
        if self.mode == DisplayMode.panel_ctrl:
            self.mode = DisplayMode.scene_panel

    def set_mode(self, mode):
        assert isinstance(mode, DisplayMode)
        self.mode = mode

    def _display_rows(self):
        mode = self.mode
        if mode == DisplayMode.scene_ctrl:
            row0, row1 = self.scene_row, self.ctrl_row
        elif mode == DisplayMode.scene_panel:
            row0, row1 = self.scene_row, self.panel_row
        elif mode == DisplayMode.panel_ctrl:
            row0, row1 = self.panel_row, self.ctrl_row
        return row0, row1 


    def display(self):
        row0, row1 = self._display_rows()
        return row0.display(), row1.display()


    def update(self):
        # print('display.update', self.mode)
        row0, row1 = self._display_rows()
        res1 = writeString(1, row0.display() + " " * 72 )
        res2 = writeString(2, " " * 72 + row1.display() + " " * (72 - len(row1.display())))
        return (res1, res2)

    
    def display_row(self, row):
        if row == 1:
            return self._row1
        elif row == 2:
            return self._row2
        else:
            raise ValueError(row)
 
