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

import maya.cmds as cmds
import azteca.game_path_panel as game_path_panel

START_TEXT ="Start"
STOP_TEXT ="Stop"
BASE_PATH =["Maya","Game"]
class FolderSync(QWidget):
    dataChanged = Signal(dict)

    def __init__(self, parent=None, *args, **kwargs):
        super(FolderSync, self).__init__(parent, *args, **kwargs)
        self.data ={}
        self.source_path =""
        self.dest_path = ""
        self.source_base ="Maya"
        self.dest_base ="Maya"
        self.thread =None
        self.check_span =3
        self.stop_flag = False
        self.initUI()

    def initUI(self):
        main_layout = QVBoxLayout()

        #ソース選択
        source_layout = QHBoxLayout()

        self.source_base_select = QComboBox()
        self.source_base_select.addItems(BASE_PATH)
        self.source_base_select.currentIndexChanged.connect(self._source_base_changed)
        source_layout.addWidget(self.source_base_select)

        self.source_line = QLineEdit()
        self.source_line.setReadOnly(True)
        source_layout.addWidget(self.source_line)
        source_select_button =QPushButton("Set Path")
        source_select_button.clicked.connect(self._source_pick)
        source_layout.addWidget(source_select_button)

        #ディスト選択
        dest_layout =QHBoxLayout()
        self.dest_base_select = QComboBox()
        self.dest_base_select.addItems(BASE_PATH)
        self.dest_base_select.currentIndexChanged.connect(self._dest_base_changed)
        dest_layout.addWidget(self.dest_base_select)

        self.dest_line =QLineEdit()
        self.dest_line.setReadOnly(True)

        dest_layout.addWidget(self.dest_line)
        dest_select_buttion = QPushButton("Set Path")
        dest_select_buttion.clicked.connect(self._dest_pick)
        dest_layout.addWidget(dest_select_buttion)

        #レイアウトに追加
        main_layout.addWidget(QLabel("Source"))
        main_layout.addLayout(source_layout)
        main_layout.addWidget(QLabel("Destination"))
        main_layout.addLayout(dest_layout)

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

        self.source_base = data["source_base"]
        self.dest_base = data["dest_base"]
        self.source_base_select.setCurrentText(self.source_base)
        self.dest_base_select.setCurrentText(self.dest_base)

    def _source_base_changed(self):
        self.source_base = self.source_base_select.currentText()
        self.dataChanged.emit(self.get_data())

    def _dest_base_changed(self):
        self.dest_base = self.dest_base_select.currentText()
        self.dataChanged.emit(self.get_data())

    def _get_base_path(self,base):
        path =""
        if base =="Maya":
            path = cmds.workspace(listFullWorkspaces=True)[0]
        else:
            path = game_path_panel.get_game_path()
        return path

    def _source_pick(self):
        base_path = self._get_base_path(self.source_base)

        path = QFileDialog.getExistingDirectory(None, "Select source directory",base_path)
        if path and base_path in path:
            relative_path = path.replace(base_path,"")
            self.source_path =relative_path
            self.source_line.setText(relative_path)
            self.dataChanged.emit(self.get_data())

    def _dest_pick(self):
        base_path = self._get_base_path(self.dest_base)
        path = QFileDialog.getExistingDirectory(None, "Select destination directory",base_path)
        if path and base_path in path:
            relative_path = path.replace(base_path,"")
            self.dest_path = relative_path
            self.dest_line.setText(relative_path)
            self.dataChanged.emit(self.get_data())

    def start_sync(self):

        #スレッドが実行されている場合、スレッドを停止
        if self.stop_flag is False and self.thread is not None:
            print("stop sync")
            self.stop_flag = True
            self.thread = None
            self.start_button.setText(START_TEXT)
        else:
            print("start sync")
            source_path = self._get_base_path(self.source_base)+self.source_path
            dest_path = self._get_base_path(self.dest_base)+self.dest_path
            print(source_path)
            print(dest_path)
            if os.path.exists(source_path) and os.path.exists(dest_path):
                #スレッドが作成されていない場合、スレッドを作成
                if self.thread is None:
                    self.stop_flag = False
                    self.thread = threading.Thread(target=self._check_updatedfiles)
                    self.thread.start()
                    self.start_button.setText(STOP_TEXT)

            else:
                print("source or dest path does not exist")


    def _check_updatedfiles(self):
        source_path = self._get_base_path(self.source_base) + self.source_path
        dest_path = self._get_base_path(self.dest_base) + self.dest_path

        while self.stop_flag is False:
            #source_pathとdest_pathにあるファイルのリストとタイムスタンプを取得
            source_files = self._get_files_and_timestamps(source_path)
            dest_files = self._get_files_and_timestamps(dest_path)

            #souce_pathにファイルでdest_filesにないファイルとdest_pathより新しいファイルをdest_pathにコピー

            for filename, timestamp in source_files.items():
                if filename not in dest_files or timestamp > dest_files[filename]:
                    source_filepath = os.path.join(source_path, filename)
                    dest_filepath = os.path.join(dest_path, filename)
                    shutil.copy2(source_filepath, dest_filepath)
                    print(f"copied {source_filepath} to {dest_filepath}")
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
            "source_base":self.source_base,
            "dest_base":self.dest_base
        }
        return data

