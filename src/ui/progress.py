import sys
import re
import time
from PySide6.QtWidgets import (
  QLineEdit,
  QLabel,
  QMessageBox,
  QPushButton,
  QApplication,
  QVBoxLayout,
  QDialog,
  QHBoxLayout,
  QFileDialog,
  QStackedLayout,
  QWidget,
  QProgressBar,
  QScrollArea
)
from PySide6.QtCore import (QObject, Signal, Slot, Qt, QThread)
from PySide6.QtGui import QPixmap

class UIProgress(QVBoxLayout):
  def __init__(self, parent=None):
    super(UIProgress, self).__init__(parent)

    self.progress_bar = QProgressBar()
    self.progress_bar.setMinimum(0)
    self.progress_bar.setMaximum(0)
    self.progress_bar.setValue(0)
    self.progress_bar.setFormat("%p% Generating Meshes %v of %m")
    self.progress_bar.setDisabled(True)
    self.addWidget(self.progress_bar)

    self.title_label = QLabel(self.progress_bar.text())
    self.title_label.setStyleSheet("font-size: 12px;font-weight: bold;margin-bottom: 20px;")
    # self.title_label.setAlignment(Qt.AlignVCenter)
    self.addWidget(self.title_label)

    self.scroll_area = QScrollArea()
    self.scroll_area.setWidgetResizable(True) # Allows the widget inside to resize with the scroll area

    self.debug_log_label = QLabel("Parsing svg...")
    self.debug_log_label.setStyleSheet("padding: 4px;background-color: #121212;color: #ffffff;font-family: Monaco;")
    self.debug_log_label.setAlignment(Qt.AlignBottom)
    # self.debug_log_label.setFixedHeight(200)
    self.debug_log_label.setWordWrap(True)
    self.scroll_area.setWidget(self.debug_log_label)
    self.scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
    self.scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)

    self.addWidget(self.scroll_area)


    # submit button
    # --------
    self.cancel_button = QPushButton("Cancel Job")
    self.cancel_button.setDisabled(False)
    self.cancel_button.clicked.connect(self.cancel_work)

    # layout.addStretch()
    self.addWidget(self.cancel_button)    

  def cancel_work(self):
    if self.worker:
      self.worker.stop()
    self.switch_layout(0)

  def setup_progress(self, steps = 0):
    self.progress_bar.setMaximum(steps)
    self.progress_bar.setValue(0)

  def update_progress(self, step = 0):
    self.progress_bar.setValue(step)
    self.title_label.setText(self.progress_bar.text())

  def on_finished(self, result):
    # handle result (None if cancelled)
    self.debug_log("Export completed successfully!")
    self.progress_bar.setValue(0)
    print("Finished!, result:", result)

  def debug_log(self, message):
    print(message)
    existing = self.debug_log_label.text()
    self.debug_log_label.setText(f"{existing}{message}\n")
    
    vbar = self.scroll_area.verticalScrollBar()
    vbar.setValue(vbar.maximum())
