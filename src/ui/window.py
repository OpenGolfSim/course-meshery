from PySide6.QtWidgets import (
  QApplication,
  QStackedLayout,
  QDialog,
  QLineEdit,
  QPushButton,
  QVBoxLayout,
  QWidget,
  QMessageBox
)
from PySide6.QtCore import (QObject, Signal, Slot, Qt, QThread)

from ui.header import UIHeader
from ui.form import UIForm
from ui.progress import UIProgress
from ui.completed import UICompleted
from lib.svg import svg_parse
from lib.process import MeshWorker

class UIWindow(QDialog):
  def __init__(self, parent=None):
    super(UIWindow, self).__init__(parent)
    
    self.setWindowTitle("OpenGolfSim - Meshery (Beta)")
    self.resize(720, 400) # Sets the initial size to 800x600 pixels

    self.stacked_layout = QStackedLayout()

    main_layout = QVBoxLayout()
    main_layout.setContentsMargins(0, 0, 0, 0) 

    header = UIHeader()

    main_layout.addWidget(header, 0)
    main_layout.addLayout(self.stacked_layout)

    # form_layout = self.create_form_layout()
    form_layout = UIForm(self)
    form_layout.submitted.connect(self.on_form_submit)
    form_widget = QWidget()
    form_widget.setLayout(form_layout)
    self.stacked_layout.addWidget(form_widget)

    self.progress_screen = UIProgress()

    job_widget = QWidget()
    job_widget.setLayout(self.progress_screen)
    self.stacked_layout.addWidget(job_widget)
    
    self.completed_screen = UICompleted()
    completed_widget = QWidget()
    self.completed_screen.restart.connect(self.on_restart_form)
    completed_widget.setLayout(self.completed_screen)
    self.stacked_layout.addWidget(completed_widget)

    self.stacked_layout.setCurrentIndex(0)
    self.setLayout(main_layout)
  

  def on_restart_form(self):
    print("on_restart_form")
    self.stacked_layout.setCurrentIndex(0)


  def on_form_submit(self, svg_path, raw_path, output_path, height_value):

    print(f"SVG {svg_path}")
    print(f"RAW {raw_path}")
    print(f"HEIGHT {height_value}")
    print(f"DIR {output_path}")
    self.stacked_layout.setCurrentIndex(1)
    
    print("Parsing SVG file...")
    svg_info = svg_parse(svg_path, "course")
    print(f"Layers: {len(svg_info['layers'])}")
    total_layers = len(svg_info['layers'])
    self.progress_screen.setup_progress(total_layers)
    
    # self.progress_screen.update_progress(0)

    self.thread = QThread()
    self.worker = MeshWorker(svg_info, raw_path, output_path, height_value)
    self.worker.moveToThread(self.thread)

    # connect
    self.thread.started.connect(self.worker.run)
    self.worker.progress.connect(self.progress_screen.update_progress)
    self.worker.debug_log.connect(self.progress_screen.debug_log)
    self.worker.finished.connect(self.on_finished)
    self.worker.error.connect(self.display_error)

    # cleanup
    self.worker.finished.connect(self.thread.quit)
    self.worker.finished.connect(self.worker.deleteLater)
    self.thread.finished.connect(self.thread.deleteLater)
    self.thread.finished.connect(self.cleanup_refs)

    # start
    self.thread.start()
  
  def on_finished(self, result):
    self.stacked_layout.setCurrentIndex(2)
    self.progress_screen.on_finished(result)

  def set_progress(self, value: int):
    self.progress_screen.update_progress(0)
  
  def display_error(self, message):
    msg = QMessageBox()
    msg.setText(message)
    msg.setWindowTitle("Error")
    msg.setStandardButtons(QMessageBox.StandardButton.Ok)
    msg.exec()
  
  def cleanup_refs(self):
    print("cleanup_refs")
    self.worker = None
    self.thread = None  