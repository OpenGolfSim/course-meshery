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

class UIForm(QVBoxLayout):
  
  submitted = Signal(str, str, str, float)

  def __init__(self, parent=None):
    super(UIForm, self).__init__(parent)

    
    self.parent = parent
    
    
    # main layout
    # layout = QVBoxLayout()

    # svg file
    # --------
    svg_group = QHBoxLayout()

    svg_path_label = QLabel("SVG File")
    svg_path_label.setFixedWidth(100)
    # self.svg_path_label.setStyleSheet("min-width: 150px;color: #FFFFFF;")
    svg_path_label.setAlignment(Qt.AlignVCenter | Qt.AlignRight)
    svg_group.addWidget(svg_path_label)

    self.svg_path_edit = QLineEdit()
    self.svg_path_edit.setReadOnly(True)
    self.svg_path_edit.setPlaceholderText("No file selected")
    svg_group.addWidget(self.svg_path_edit)

    select_svg_button = QPushButton("Select SVG File", autoDefault=False)
    select_svg_button.setFixedWidth(150)
    select_svg_button.clicked.connect(self.select_svg_file)
    svg_group.addWidget(select_svg_button)

    self.addLayout(svg_group)
    
    # terrain file
    # --------
    raw_group = QHBoxLayout()
    raw_path_label = QLabel("Raw Terrain File")
    raw_path_label.setFixedWidth(100)
    raw_path_label.setAlignment(Qt.AlignVCenter | Qt.AlignRight)
    raw_group.addWidget(raw_path_label)

    self.raw_path_edit = QLineEdit()
    self.raw_path_edit.setReadOnly(True)
    self.raw_path_edit.setPlaceholderText("No file selected")
    raw_group.addWidget(self.raw_path_edit)

    select_raw_button = QPushButton("Select Raw Terrain", autoDefault=False)
    select_raw_button.setFixedWidth(150)
    select_raw_button.clicked.connect(self.select_raw_file)
    raw_group.addWidget(select_raw_button)
    
    self.addLayout(raw_group)

    # height scale
    # --------
    height_group = QHBoxLayout()
    height_scale_label = QLabel("Height Scale")
    height_scale_label.setFixedWidth(100)
    height_scale_label.setAlignment(Qt.AlignVCenter | Qt.AlignRight)
    height_group.addWidget(height_scale_label)

    self.height_scale_edit = QLineEdit()
    self.height_scale_edit.setPlaceholderText("e.g. 10.52")
    self.height_scale_edit.textChanged.connect(self.height_scale_changed)
    height_group.addWidget(self.height_scale_edit)

    self.addLayout(height_group)

    # output folder
    # --------
    output_group = QHBoxLayout()
    output_path_label = QLabel("Output Folder")
    output_path_label.setFixedWidth(100)
    # self.output_path_label.setStyleSheet("min-width: 150px;color: #FFFFFF;")
    output_path_label.setAlignment(Qt.AlignVCenter | Qt.AlignRight)
    output_group.addWidget(output_path_label)

    self.output_path_edit = QLineEdit()
    self.output_path_edit.setReadOnly(True)
    self.output_path_edit.setPlaceholderText("No file selected")
    output_group.addWidget(self.output_path_edit)

    select_output_button = QPushButton("Set Output Folder", autoDefault=False)
    select_output_button.setFixedWidth(150)
    select_output_button.clicked.connect(self.select_output_file)
    output_group.addWidget(select_output_button)
    
    self.addStretch()

    self.addLayout(output_group)

    # submit button
    # --------
    self.submit_button = QPushButton("Create Meshes")
    self.submit_button.clicked.connect(self.submit)

    self.addWidget(self.submit_button)
    self.validate_form()
  
  
  def register_listener(self, listener_callback):
    self._listeners.append(listener_callback)

  def trigger_event(self, event_data):
    print(f"Emitter triggering event with data: {event_data}")
    for listener_callback in self._listeners:
      listener_callback(event_data)
  
  def validate_form(self):
    disabled = len(self.svg_path_edit.text()) == 0 \
      or len(self.raw_path_edit.text()) == 0 \
      or len(self.height_scale_edit.text()) == 0 \
      or len(self.output_path_edit.text()) == 0
    self.submit_button.setDisabled(disabled)
    # self.submit_button.setDisabled(False)

  def display_error(self, message):
    print(message)
    msg = QMessageBox()
    msg.setText(message)
    msg.setWindowTitle("Error")
    msg.setStandardButtons(QMessageBox.StandardButton.Ok)
    msg.exec()

  def submit(self):
    svg_path = self.svg_path_edit.text()
    raw_path = self.raw_path_edit.text()
    output_path = self.output_path_edit.text()
    
    if (len(svg_path) == 0):
      self.display_error("Error: SVG path must be set!")
      return None
    if (len(raw_path) == 0):
      self.display_error("Error: RAW terrain path must be set!")
      return None
    if (len(output_path) == 0):
      self.display_error("Error: An output folder must be set!")
      return None
    
    height_value = 0
    try:
      height_value = float(self.height_scale_edit.text())
    except ValueError:
      self.display_error(f"Error: height scale could not be converted to a float!")
      return None
    
    if height_value <= 0:
      self.display_error(f"Error: height scale cannot be zero!")

    self.submitted.emit(svg_path, raw_path, output_path, height_value)

  @Slot()
  def height_scale_changed(self):
    # number = float(self.height_scale_edit.text())
    # self.height_scale_edit.setText(f"{number}")
    replaced = re.sub("[^0-9\\.-]", "", self.height_scale_edit.text())
    self.height_scale_edit.setText(replaced)
    self.validate_form()

  @Slot()
  def select_svg_file(self):
    # Open a file dialog to select a file
    # getOpenFileName returns a tuple: (filename, selected_filter)
    svg_file_name, _ = QFileDialog.getOpenFileName(
      self.parent,
      "Open SVG File",  # Dialog title
      "",           # Initial directory (empty string for current directory)
      "SVG Files (*.svg)" # File filters
    )

    if svg_file_name:
      self.svg_path_edit.setText(svg_file_name)
      self.validate_form()

  @Slot()
  def select_raw_file(self):
    # Open a file dialog to select a file
    # getOpenFileName returns a tuple: (filename, selected_filter)
    raw_file_name, _ = QFileDialog.getOpenFileName(
      self.parent,
      "Open Raw Terrain File",  # Dialog title
      "",           # Initial directory (empty string for current directory)
      "RAW Files (*.raw)" # File filters
    )

    if raw_file_name:
      self.raw_path_edit.setText(raw_file_name)
      self.validate_form()

  @Slot()
  def select_output_file(self):
    # Open a file dialog to select a file
    # getOpenFileName returns a tuple: (filename, selected_filter)
    output_file_name = QFileDialog.getExistingDirectory(
      self.parent,
      "Select Output Folder",  # Dialog title
      ""
    )
    print(output_file_name)
    if output_file_name:
      self.output_path_edit.setText(output_file_name)
      self.validate_form()
      

