from PySide6.QtWidgets import (
  QLabel,
  QVBoxLayout,
  QHBoxLayout,
  QWidget
)
from PySide6.QtCore import (Qt)
from PySide6.QtGui import QPixmap

from lib.utils import resource_path

class UIHeader(QWidget):
  def __init__(self, parent=None):
    super(UIHeader, self).__init__(parent)
    # header_wrapper = QWidget()
    
    # wrapper = QWidget()
    # self.addWidget(wrapper, 0)
    # self.setStyleSheet("background-color: #000;")

    header = QHBoxLayout()
    self.setLayout(header)

    icon = QLabel()
    pixmap = QPixmap(resource_path('images/ogs-icon.png')) 
    icon.setPixmap(pixmap.scaled(32, 32, Qt.KeepAspectRatio, Qt.SmoothTransformation))

    icon.setAlignment(Qt.AlignHCenter | Qt.AlignVCenter)
    
    title_label = QLabel("OpenGolfSim Meshery")
    title_label.setStyleSheet("font-size: 16px;font-weight: bold;")
    title_label.setAlignment(Qt.AlignVCenter)

    subtitle_label = QLabel("SVG to mesh converter - v1.0.3")
    subtitle_label.setStyleSheet("font-size: 11px;")
    subtitle_label.setAlignment(Qt.AlignVCenter | Qt.AlignRight)

    header.addWidget(icon)
    header.addWidget(title_label)
    header.addStretch()
    header.addWidget(subtitle_label)
