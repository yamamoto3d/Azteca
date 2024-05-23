try:
    from PySide2.QtCore import *
    from PySide2.QtGui import *
    from PySide2.QtWidgets import *
except:
    from PySide6.QtCore import *
    from PySide6.QtGui import *
    from PySide6.QtWidgets import *
import maya.cmds as cmds

GAME_PATH_OPTION_VAR_NAME = "bae_game_path"
def get_game_path():
    path = ""
    if cmds.optionVar(exists=GAME_PATH_OPTION_VAR_NAME):
        path = cmds.optionVar(q=GAME_PATH_OPTION_VAR_NAME)
    return path

class GamePathPanel(QWidget):
    def __init__(self, parent=None, *args, **kwargs):
        super(GamePathPanel, self).__init__(parent, *args, **kwargs)
        self.initUI()

    def initUI(self):
        path_select_layout = QHBoxLayout()

        path =get_game_path()

        self.path_line_edit = QLineEdit(path)
        self.path_line_edit.setReadOnly(True)

        path_select_layout.addWidget(self.path_line_edit)

        pick_path_button = QPushButton("SetPath")
        pick_path_button.clicked.connect(self._openGamePathDialog)

        path_select_layout.addWidget(pick_path_button)

        group = QGroupBox("Game Base Path")
        group.setLayout(path_select_layout)

        root_layout =QVBoxLayout()
        root_layout.addWidget(group)
        self.setLayout(root_layout)

    def _openGamePathDialog(self):
        response = QFileDialog.getExistingDirectory(None, "Select Directory")
        if response:
            path = response
            self.path_line_edit.setText(path)
            cmds.optionVar(stringValue=(GAME_PATH_OPTION_VAR_NAME, path))
