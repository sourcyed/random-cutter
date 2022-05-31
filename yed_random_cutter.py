import sys
import os
import threading
import cv2
from PyQt5.QtWidgets import QWidget,QApplication,QMainWindow,QLabel,QPushButton,QVBoxLayout,QHBoxLayout,QFileDialog,QProgressBar,QDoubleSpinBox,QMessageBox
from PyQt5.QtGui import QImage,QPixmap,QPalette,QColor
from PyQt5.QtCore import Qt
from random_cutter import RandomCutter

class YEDRandomCutter(QWidget):
    def __init__(self):
        super().__init__()
        self.init_ui()

    def init_ui(self):
        self.vid_path = ""
        self.mus_path = ""
        self.save_path = ""

        self.input_frame1 = QLabel()
        self.input_frame1.setMinimumSize(600,400)

        self.input_vid_path = QPushButton("Select Video File")
        self.input_vid_path.clicked.connect(self.get_vid_path)
        self.input_mus_path = QPushButton("Select Music File")
        self.input_mus_path.clicked.connect(self.get_mus_path)
        self.input_save_path = QPushButton("Select Save Location")
        self.input_save_path.clicked.connect(self.get_save_path)
        self.input_vid_length = QDoubleSpinBox()
        self.input_vid_length.setMaximum(86400)
        self.input_vid_length.valueChanged.connect(self.check_cut_length_value)
        self.input_cut_length = QDoubleSpinBox()
        self.input_cut_length.setMaximum(86400)
        self.input_cut_length.valueChanged.connect(self.check_cut_length_value)
        self.input_progress = QProgressBar()
        self.input_progress.setMaximum(100)
        self.input_cut = QPushButton("Cut")
        self.input_cut.clicked.connect(self.cut)

        v_box = QVBoxLayout()
        v_box.addStretch()
        v_box.addWidget(QLabel("Video file:"))
        v_box.addWidget(self.input_vid_path)
        v_box.addStretch()
        v_box.addWidget(QLabel("Music file:"))
        v_box.addWidget(self.input_mus_path)
        v_box.addStretch()
        v_box.addWidget(QLabel("Save location:"))
        v_box.addWidget(self.input_save_path)
        v_box.addStretch()
        v_box.addWidget(QLabel("Video length:"))
        v_box.addWidget(self.input_vid_length)
        v_box.addStretch()
        v_box.addWidget(QLabel("Cut length:"))
        v_box.addWidget(self.input_cut_length)
        v_box.addStretch()
        v_box.addWidget(self.input_progress)
        v_box.addStretch()
        v_box.addWidget(self.input_cut)
        v_box.addStretch()
        
        h_box = QHBoxLayout()
        h_box.addStretch()
        h_box.addWidget(self.input_frame1)
        h_box.addStretch()
        h_box.addLayout(v_box)
        h_box.addStretch()
        self.setLayout(h_box)
        
    def check_cut_length_value(self):
        if self.input_cut_length.value() > self.input_vid_length.value():
            self.input_cut_length.setValue(self.input_vid_length.value())

    def get_vid_path(self):
        self.vid_path = QFileDialog.getOpenFileName(self,"Select Video File",os.getenv("HOME"),"Video files (*.mp4 *.avi *.wmv *.mov *.mkv)")[0]
        if self.vid_path != "":
            self.input_vid_path.setText(self.vid_path.split("/")[-1])

    def get_mus_path(self):
        self.mus_path = QFileDialog.getOpenFileName(self,"Select Video File",os.getenv("HOME"),"Audio files (*.mp3 *.wav *.ogg *.m4a)")[0]
        if self.mus_path != "":
            self.input_mus_path.setText(self.mus_path.split("/")[-1])
        
    def get_save_path(self):
        self.save_path = QFileDialog.getSaveFileName(self,"Select Save File Path",os.getenv("HOME"),"Video files (*.mp4)")[0]
        if self.save_path != "":
            self.input_save_path.setText(self.save_path.split("/")[-1])

    def cut(self):
        if self.vid_path != "" and self.mus_path != "" and self.save_path != "" and self.input_vid_length.value() > 0 and self.input_cut_length.value() > 0:
            if self.save_path.split(".")[-1].lower() != "mp4":
                self.save_path = self.save_path + ".mp4"
            self.cutter = threading.Thread(target=RandomCutter, args=(self.vid_path, self.mus_path, self.save_path, self.input_vid_length.value(), self.input_cut_length.value()))
            self.cutter.start()
            self.input_cut.setEnabled(False)
            self.input_progress.setValue(0)
            self.input_progress.resetFormat()
            

    def open_video_box(self):
        buttonReply = QMessageBox.question(self, "Operation Complete", "Do you want to open the cutted video?", QMessageBox.Yes | QMessageBox.No, QMessageBox.Yes)
        if buttonReply == QMessageBox.Yes:
            os.startfile(self.save_path)

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.window = YEDRandomCutter()
        self.setCentralWidget(self.window)
        self.setWindowTitle("YED Random Cutter")
        self.show()

class RandomCutter(RandomCutter):
    def display_progress(self):
        super().display_progress()
        main_window.window.input_progress.setValue(self.progress)
        frame = self.frame
        frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        img = QImage(frame, frame.shape[1], frame.shape[0], QImage.Format_RGB888)
        pix = QPixmap.fromImage(img)
        pix = pix.scaled(600, 400, Qt.KeepAspectRatio, Qt.SmoothTransformation)
        main_window.window.input_frame1.setPixmap(pix)

    def add_music(self):
        main_window.window.input_progress.setFormat("Adding music...")
        super().add_music()
        
    def run_operations(self):
        super().run_operations()
        # main_window.window.input_progress.setValue(main_window.window.input_progress.maximum())
        main_window.window.input_progress.setFormat("Operation completed!")
        main_window.window.open_video_box()
        main_window.window.input_cut.setEnabled(True)

app = QApplication(sys.argv)

app.setStyle("Fusion")
def createPalette():
    palette = QPalette()
    palette.setColor(QPalette.Window, QColor(53, 53, 53))
    palette.setColor(QPalette.WindowText, Qt.white)
    palette.setColor(QPalette.Base, QColor(25, 25, 25))
    palette.setColor(QPalette.AlternateBase, QColor(53, 53, 53))
    palette.setColor(QPalette.ToolTipBase, Qt.white)
    palette.setColor(QPalette.ToolTipText, Qt.white)
    palette.setColor(QPalette.Text, Qt.white)
    palette.setColor(QPalette.Button, QColor(53, 53, 53))
    palette.setColor(QPalette.ButtonText, Qt.white)
    palette.setColor(QPalette.BrightText, Qt.red)
    palette.setColor(QPalette.Link, QColor(42, 130, 218))
    palette.setColor(QPalette.Highlight, QColor(42, 130, 218))
    palette.setColor(QPalette.HighlightedText, Qt.black)
    return palette
app.setPalette(createPalette())
main_window = MainWindow()
sys.exit(app.exec_())