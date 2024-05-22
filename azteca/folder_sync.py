import time
import threading

try:
    from PySide2.QtCore import *
    from PySide2.QtGui import *
    from PySide2.QtWidgets import *
except:
    from PySide6.QtCore import *
    from PySide6.QtGui import *
    from PySide6.QtWidgets import *

START_TEXT ="Start"
STOP_TEXT ="Stop"

class FolderSync(QWidget):
    dataChanged = Signal(dict)

    def __init__(self, parent=None, *args, **kwargs):
        super(FolderSync, self).__init__(parent, *args, **kwargs)
        self.data ={}
        self.source_path =""
        self.dest_path = ""
        self.ignore_list =[".mayaSwatches","3dPaintTextures"]

        self.initUI()

    def initUI(self):
        main_layout = QVBoxLayout()

        #ソース選択
        source_layout = QHBoxLayout()
        source_layout.addWidget(QLabel("Source Folder"))
        self.source_line = QLineEdit()
        self.source_line.setReadOnly(True)
        source_layout.addWidget(self.source_line)
        source_select_button =QPushButton("Set Path")
        source_select_button.clicked.connect(self._source_pick)
        source_layout.addWidget(source_select_button)

        #ディスト選択
        dest_layout =QHBoxLayout()
        dest_layout.addWidget(QLabel("Dest Folder"))
        self.dest_line =QLineEdit()
        self.dest_line.setReadOnly(True)

        dest_layout.addWidget(self.dest_line)
        dest_select_buttion = QPushButton("Set Path")
        dest_select_buttion.clicked.connect(self._dest_pick)
        dest_layout.addWidget(dest_select_buttion)

        #排除リスト
        ignore_lyaout =QHBoxLayout()
        ignore_lyaout.addWidget(QLabel("Ignore List"))
        self.ignore_text_box = QTextEdit()
        self.ignore_text_box.setMaximumHeight(60)
        self.ignore_text_box.textChanged.connect(self._ignore_changed)
        text =""
        for i in self.ignore_list:
            text = text+i+"\n"
        self.ignore_text_box.setText(text)
        ignore_lyaout.addWidget(self.ignore_text_box)

        main_layout.addLayout(source_layout)
        main_layout.addLayout(dest_layout)
        main_layout.addLayout(ignore_lyaout)

        #スタートボタン
        self.start_button = QPushButton(START_TEXT)
        main_layout.addWidget(self.start_button)

        #グループ
        group = QGroupBox("Sync Folder")
        group.setLayout(main_layout)
        #group.setMaximumHeight(200)

        root_layout = QVBoxLayout()
        root_layout.addWidget(group)

        self.setLayout(root_layout)

    def set_data(self,data:dict):
        self.source_path =data["source"]
        self.source_line.setText(self.source_path)

        self.dest_path = data["dest"]
        self.dest_line.setText(self.dest_path)

        self.ignore_list=data["ignore"]
        text =""
        for i in self.ignore_list:
            text = text+i+"\n"
        self.ignore_text_box.setText(text)


    def _source_pick(self):
        path = QFileDialog.getExistingDirectory(None, "Select source directory")
        if path:
            self.source_path =path
            self.source_line.setText(path)
            self.dataChanged.emit(self.get_data())


    def _dest_pick(self):
        path = QFileDialog.getExistingDirectory(None, "Select destination directory")
        if path:
            self.dest_path = path
            self.dest_line.setText(path)
            self.dataChanged.emit(self.get_data())

    def _ignore_changed(self):
        self.ignore_list=self.ignore_text_box.toPlainText().split("\n")
        self.dataChanged.emit(self.get_data())

    def get_data(self):
        data = {
            "source":self.source_path,
            "dest":self.dest_path,
            "ignore":self.ignore_list
        }
        return data

