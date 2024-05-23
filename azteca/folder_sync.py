import os.path
import time
import os
import threading
from datetime import datetime
import shutil

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
        self.thread =None
        self.check_span =3
        self.stop_flag = False
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
        self.start_button.clicked.connect(self.start_sync)
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

    def start_sync(self):
        print("start sync")
        #スレッドが実行されている場合、スレッドを停止
        if self.stop_flag is False and self.thread is not None:
            self.stop_flag = True
            self.thread = None
            self.start_button.setText(START_TEXT)
            print("Stop flag"+str(self.stop_flag))
        else:
            if os.path.exists(self.source_path) and os.path.exists(self.dest_path):
                #スレッドが作成されていない場合、スレッドを作成
                if self.thread is None:
                    self.stop_flag = False
                    self.thread = threading.Thread(target=self._check_updatedfiles)
                    self.thread.start()
                    self.start_button.setText(STOP_TEXT)

            else:
                print("source or dest path does not exist")


    def _check_updatedfiles(self):
        while self.stop_flag is False:
            #source_pathとdest_pathにあるファイルのリストとタイムスタンプを取得
            source_files = self._get_files_and_timestamps(self.source_path)
            dest_files = self._get_files_and_timestamps(self.dest_path)

            #souce_pathにファイルでdest_filesにないファイルとdest_pathより新しいファイルをdest_pathにコピー

            for filename, timestamp in source_files.items():
                if filename not in dest_files or timestamp > dest_files[filename]:
                    source_filepath = os.path.join(self.source_path, filename)
                    dest_filepath = os.path.join(self.dest_path, filename)
                    shutil.copy2(source_filepath, dest_filepath)
                    print(f"copied {source_filepath} to {dest_filepath}")
            print(self.stop_flag)
            time.sleep(self.check_span)


    def _get_files_and_timestamps(self, directory):
        files_and_timestamps = {}

        for filename in os.listdir(directory):
            filepath = os.path.join(directory, filename)
            if os.path.isfile(filepath):
                timestamp = os.path.getmtime(filepath)
                readable_timestamp = datetime.fromtimestamp(timestamp).strftime('%Y-%m-%d %H:%M:%S')
                files_and_timestamps[filename] = readable_timestamp

        return files_and_timestamps
    def get_data(self):
        data = {
            "source":self.source_path,
            "dest":self.dest_path,
            "ignore":self.ignore_list
        }
        return data

