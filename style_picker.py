from flowlayout import FlowLayout

from PyQt5.QtGui import QPixmap, QIcon
from PyQt5.QtWidgets import *
from PyQt5.QtCore import Qt, pyqtSignal

from style import Style
from style_button import StyleButton

def set_button_color(button,color):
    pal = button.palette()
    pal.setColor(QPalette.Button,color)
    pal.setPalette(pal)

class StylePicker(QWidget):
    style_picked = pyqtSignal(int)
    def pick_style(self,style):
        # Revert old buttons.
        for button in self.style_buttons:
            button.unhighlight()
        self.style_buttons[style].highlight()
        self.style_picked.emit(style)

    def __init__(self,styles):
        super().__init__()
        layout = FlowLayout()
        self.style_buttons = []
        for i, style in enumerate(styles):
            style_button = StyleButton(style)
            style_button.clicked.connect(lambda i=i: self.pick_style(i))
            self.style_buttons.append(style_button)
            layout.addWidget(style_button)
        self.setLayout(layout) 
            
