import os

from PyQt5.QtWidgets import *
from PyQt5.QtGui import QPixmap, QIcon

from PyQt5.QtCore import Qt, pyqtSignal

from PyQt5.QtGui import QBrush, QPalette

from style import Style

class StyleButton(QWidget):
    default_size = (400,400)
    default_icon = os.path.join(os.path.dirname(os.path.realpath(__file__)),"images/default_thumb.png")
    picked_color = Qt.blue
    clicked = pyqtSignal()
    def __init__(self,style):
        super().__init__()
        layout = QVBoxLayout()
        if style.thumb:
            thumb_pix = QPixmap(style.thumb).scaled(*type(self).default_size)
        else:
            thumb_pix = QPixmap(type(self).default_icon).scaled(*type(self).default_size)
        thumb_icon = QIcon(thumb_pix)
        self.thumb_button = QPushButton()
        self.thumb_button.setIcon(thumb_icon)
        self.thumb_button.setIconSize(thumb_pix.rect().size())
        title_label = QLabel(style.title)
        title_label.setStyleSheet("font-weight: bold; font-style: italic; font-size: 20px")
        if style.artist:
            artist_label = QLabel(style.artist)
        else:
            artist_label = QLabel("")
        layout.addWidget(self.thumb_button)
        layout.addWidget(title_label)
        layout.addWidget(artist_label)
        layout.setAlignment(self.thumb_button,Qt.AlignHCenter)
        layout.setAlignment(title_label,Qt.AlignHCenter)
        layout.setAlignment(artist_label,Qt.AlignHCenter)
        self.setLayout(layout)
        self.thumb_button.clicked.connect(lambda: self.clicked.emit())

    def highlight(self):
        palette = QPalette()
        palette.setColor(self.thumb_button.backgroundRole(), type(self).picked_color)
        self.thumb_button.setPalette(palette)

    def unhighlight(self):
        palette = QPalette()
        self.thumb_button.setPalette(palette)
        
