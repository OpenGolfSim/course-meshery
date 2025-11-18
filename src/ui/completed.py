from PySide6.QtWidgets import (
  QApplication,
  QLabel,
  QPushButton,
  QVBoxLayout,
  QHBoxLayout,
  QWidget
)
from PySide6.QtCore import (Qt, Slot, Signal)
from PySide6.QtGui import QPixmap

from lib.utils import resource_path

class UICompleted(QVBoxLayout):
  restart = Signal()        # emit progress percent
  
  def __init__(self, parent=None):
    super(UICompleted, self).__init__(parent)
    

    icon = QLabel()
    pixmap = QPixmap(resource_path('images/green-check.png')) 
    icon.setPixmap(pixmap.scaled(128, 128, Qt.KeepAspectRatio, Qt.SmoothTransformation))

    icon.setAlignment(Qt.AlignHCenter | Qt.AlignBottom)
    
    title_label = QLabel("Job Completed")
    title_label.setStyleSheet("font-size: 24px;font-weight: bold;")
    title_label.setAlignment(Qt.AlignHCenter | Qt.AlignTop)

    button_wrapper = QWidget()
    button_layout = QHBoxLayout()
    button_wrapper.setLayout(button_layout)

    exit_button = QPushButton("Quit")
    exit_button.setFixedWidth(150)
    exit_button.clicked.connect(self.exit_button_clicked)
    button_layout.addWidget(exit_button)

    start_button = QPushButton("Start Over")
    start_button.setFixedWidth(150)
    start_button.clicked.connect(self.restart_clicked)
    button_layout.addWidget(start_button)

    self.addStretch()
    self.addWidget(icon)
    self.addWidget(title_label)
    self.addWidget(button_wrapper)
    self.addStretch()

  @Slot()
  def restart_clicked(self):
    self.restart.emit()

  @Slot()
  def exit_button_clicked(self):
    print("Exit app")
    QApplication.instance().quit()
    # sys.exit