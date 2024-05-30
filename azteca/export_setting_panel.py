try:
    from PySide2.QtCore import *
    from PySide2.QtGui import *
    from PySide2.QtWidgets import *
except:
    from PySide6.QtCore import *
    from PySide6.QtGui import *
    from PySide6.QtWidgets import *
import maya.cmds as cmds

FILE_FORMAT =["FBX export", "mayaAscii", "OBJexport"]
FBX_DEFAULT_SETTING = {
    "smoothing_group":True,
    "smooth_mesh":False,
    "split_vertex":False,
    "triangulate":False,
    "tangent":True,
    "skinning":True,
    "blendshape":True,
    "animation":False,
    "up_axis":"Y",
    "embedded_textures":False,
    "file_type":"ascii",
    "file_version":"2020"
}
USD_DEFAULT_SETTING = {
    "defaultUSDFormat": "usda",

    "defaultMeshScheme": "catmullClark",

    "exportComponentTags":True,
    "exportColorSets":True,
    "exportUVs":True,
    "exportSkels":"auto",
    "exportSkin":"auto",
    "exportBlendShapes":True,
    "exportDisplayColor":False,

    "exportInstances":True,
    "referenceObjectModels":"none",
    "exportRelativeTextures":"auto",
    "convertMaterialsTo": "UsdPreviewSurface",
}
class FbxExportSettingPanel(QWidget):
    dataChanged = Signal(dict)
    def __init__(self, parent=None, *args, **kwargs):
        super(FbxExportSettingPanel, self).__init__(parent, *args, **kwargs)

        self.smoothing_group_check = QCheckBox("Smoothing Group")
        self.smooth_mesh_check = QCheckBox("Smooth Mesh")
        self.up_axis_combobox = QComboBox()
        self.tangent_check = QCheckBox("Tangent")
        self.split_vertex_check = QCheckBox("Split per-vertex Normals")
        self.triangulate_check = QCheckBox("Triangulate")
        self.skinning_check = QCheckBox("Skinning")
        self.file_type_combobox = QComboBox()
        self.blendshape_check = QCheckBox("Blendshape")
        self.animation_check = QCheckBox("Animation")

        self.embedded_textures = QCheckBox("Embedded Textures")
        self.file_version_combobox = QComboBox()

        self.initUI()
        self.setData(FBX_DEFAULT_SETTING)

        self.stop_emit=False

    def initUI(self):
        self.smoothing_group_check.clicked.connect(self.ui_changed)
        self.smooth_mesh_check.clicked.connect(self.ui_changed)
        self.split_vertex_check.clicked.connect(self.ui_changed)
        self.triangulate_check.clicked.connect(self.ui_changed)
        self.tangent_check.clicked.connect(self.ui_changed)
        self.skinning_check.clicked.connect(self.ui_changed)
        self.blendshape_check.clicked.connect(self.ui_changed)

        self.skinning_check.clicked.connect(self.ui_changed)
        self.animation_check.clicked.connect(self.ui_changed)

        self.up_axis_combobox.currentIndexChanged.connect(self.ui_changed)
        self.up_axis_combobox.addItems(["Y","Z"])
        self.up_axis_combobox.currentIndexChanged.connect(self.ui_changed)
        self.embedded_textures.clicked.connect(self.ui_changed)

        self.file_type_combobox.currentIndexChanged.connect(self.ui_changed)
        self.file_type_combobox.addItems(["ascii","binary"])
        self.file_type_combobox.currentIndexChanged.connect(self.ui_changed)

        self.file_version_combobox.currentIndexChanged.connect(self.ui_changed)
        self.file_version_combobox.addItems(["FBX202000","FBX201900","FBX201800","FBX201600","FBX201400","FBX201300","FBX201200","FBX201100","FBX201000","FBX200900","FBX200611"])
        self.file_version_combobox.currentIndexChanged.connect(self.ui_changed)

        main_layout = QVBoxLayout()
        grid_layout = QGridLayout()
        grid_layout.addWidget(self.smoothing_group_check,0,0)
        grid_layout.addWidget(self.smooth_mesh_check,1,0)
        grid_layout.addWidget(self.split_vertex_check,2,0)
        grid_layout.addWidget(self.skinning_check,3,0)
        grid_layout.addWidget(self.animation_check,4,0)

        grid_layout.addWidget(self.triangulate_check,0,1)
        grid_layout.addWidget(self.tangent_check,1,1)
        grid_layout.addWidget(self.blendshape_check,3,1)

        up_axis_layout = QHBoxLayout()
        up_axis_layout.addWidget(QLabel("Up Axis"))
        up_axis_layout.addWidget(self.up_axis_combobox)
        grid_layout.addLayout(up_axis_layout,5,0)

        grid_layout.addWidget(self.embedded_textures,5,1)

        file_type_layout = QHBoxLayout()
        file_type_layout.addWidget(QLabel("File Type"))
        file_type_layout.addWidget(self.file_type_combobox)

        file_version_layout = QHBoxLayout()
        file_version_layout.addWidget(QLabel("File Version"))
        file_version_layout.addWidget(self.file_version_combobox)

        main_layout.addLayout(grid_layout)
        main_layout.addLayout(file_type_layout)
        main_layout.addLayout(file_version_layout)

        self.setLayout(main_layout)

    def setData(self, dict):
        self.stop_emit=True
        self.smoothing_group_check.setChecked(dict["smoothing_group"])
        self.smooth_mesh_check.setChecked(dict["smooth_mesh"])
        self.split_vertex_check.setChecked(dict["split_vertex"])
        self.triangulate_check.setChecked(dict["triangulate"])
        self.tangent_check.setChecked(dict["tangent"])
        self.skinning_check.setChecked(dict["skinning"])
        self.blendshape_check.setChecked(dict["blendshape"])
        self.animation_check.setChecked(dict["animation"])
        self.up_axis_combobox.setCurrentText(dict["up_axis"])
        self.embedded_textures.setChecked(dict["embedded_textures"])
        self.file_type_combobox.setCurrentText(dict["file_type"])
        self.file_version_combobox.setCurrentText(dict["file_version"])
        self.stop_emit=False

    def data(self):
        return {
            "smoothing_group":self.smoothing_group_check.isChecked(),
            "smooth_mesh":self.smooth_mesh_check.isChecked(),
            "split_vertex":self.split_vertex_check.isChecked(),
            "triangulate":self.triangulate_check.isChecked(),
            "tangent":self.tangent_check.isChecked(),
            "skinning":self.skinning_check.isChecked(),
            "blendshape":self.blendshape_check.isChecked(),
            "animation":self.animation_check.isChecked(),
            "up_axis":self.up_axis_combobox.currentText(),
            "embedded_textures":self.embedded_textures.isChecked(),
            "file_type":self.file_type_combobox.currentText(),
            "file_version":self.file_version_combobox.currentText()}
    def ui_changed(self):
        if self.stop_emit:
            return
        self.dataChanged.emit(self.data())


class ExportSettingPanel(QWidget):
    formatComboBox: QComboBox
    dataChanged =  Signal(dict)
    def __init__(self, parent=None, *args, **kwargs):
        super(ExportSettingPanel, self).__init__(parent, *args, **kwargs)

        self.currentData = None
        self.targetLine = QLineEdit()
        self.targetLine.setReadOnly(True)
        self.pathLine = QLineEdit()
        self.pathLine.setReadOnly(True)
        self.gameBaseButton = QRadioButton("Game")
        self.mayaBaseButton = QRadioButton("Maya")
        self.formatComboBox = QComboBox()
        self.group = QGroupBox("Export Settings")

        self.initUI()


    def initUI(self):

        #target
        target_layout = QHBoxLayout()

        target_label = QLabel("Target")
        target_pick_button: QPushButton = QPushButton("Pick Selection")
        target_pick_button.clicked.connect(self._pick_selection)

        target_layout.addWidget(target_label)
        target_layout.addWidget(self.targetLine)
        target_layout.addWidget(target_pick_button)

        #Base Path Selection
        base_path_layout = QHBoxLayout()
        base_path_layout.addWidget(QLabel("Base Path"))

        base_path_selection = QButtonGroup()
        self.mayaBaseButton.clicked.connect(self._maya_radio_clicked)
        base_path_selection.addButton(self.mayaBaseButton)
        base_path_layout.addWidget(self.mayaBaseButton)

        self.gameBaseButton.clicked.connect(self._game_radio_clicked)
        base_path_selection.addButton(self.gameBaseButton)
        base_path_layout.addWidget(self.gameBaseButton)

        self.mayaBaseButton.setChecked(True)

        #FileFormat
        file_format_layout = QHBoxLayout()
        file_format_layout.addWidget(QLabel("File Format"))

        self.formatComboBox.addItems(FILE_FORMAT)
        self.formatComboBox.currentIndexChanged.connect(self._change_file_format)
        file_format_layout.addWidget(self.formatComboBox)

        #Panels
        self.fbx_panel = FbxExportSettingPanel()
        self.fbx_panel.dataChanged.connect(self._export_setting_changed)


        #path
        path_layout = QHBoxLayout()

        edit_button = QPushButton("Set Path")
        edit_button.clicked.connect(self._open_file_path_dialog)

        path_layout.addWidget(self.pathLine)
        path_layout.addWidget(edit_button)

        #mainLayout
        main_layout = QVBoxLayout()

        main_layout.addLayout(target_layout)
        main_layout.addLayout(base_path_layout)
        main_layout.addLayout(file_format_layout)
        main_layout.addWidget(self.fbx_panel)
        main_layout.addLayout(path_layout)

        self.group.setLayout(main_layout)
        root_layout = QVBoxLayout()
        root_layout.addWidget(self.group)
        self.setLayout(root_layout)

        self.group.setEnabled(False)

    def setData(self, dict):
        self.currentData = dict
        if dict:
            self.group.setEnabled(True)
            self.pathLine.setText(dict["path"])
            self.targetLine.setText(dict["target"])

            if dict["base"]=="game":
                self.gameBaseButton.setChecked(True)
            else:
                self.mayaBaseButton.setChecked(True)

            index =0
            for t in FILE_FORMAT:
                if dict["format"] == t:
                    break
                else:
                    index +=1

            self.formatComboBox.setCurrentIndex(index)
            self.fbx_panel.setData(dict["exportSettings"])
        else:
            self.group.setEnabled(False)
            self.pathLine.setText("")
            self.targetLine.setText("")
    def _extension_check(self,path):
        base = path.split(".")[0]
        fm = self.currentData["format"]
        if fm == FILE_FORMAT[0]:
            base = base+".fbx"
        elif fm == FILE_FORMAT[1]:
            base = base+".ma"
        elif fm == FILE_FORMAT[2]:
            base = base+".obj"
        return base

    def _open_file_path_dialog(self):
        base_path = cmds.workspace(listFullWorkspaces=True)[0]
        if(self.currentData["base"]=="game"):
            base_path = cmds.optionVar(q=azteca.game_path_panel.GAME_PATH_OPTION_VAR_NAME)

        response = QFileDialog.getSaveFileName (None, "Select File",base_path)
        path = response[0]


        if base_path in path:
            path = path.replace(base_path,"")
            path = self._extension_check(path)
            self.pathLine.setText(path)
            self.currentData["path"]=path
            self.dataChanged.emit(self.currentData)
        else:
            print("It`s not correct path")
    def _export_setting_changed(self):
        self.currentData["exportSettings"] = self.fbx_panel.data()
        self.dataChanged.emit(self.currentData)

    def _change_file_format(self):
        self.currentData["format"] =FILE_FORMAT[self.formatComboBox.currentIndex()]
        self.currentData["path"] =self._extension_check(self.currentData["path"])
        self.pathLine.setText(self.currentData["path"])
        if self.currentData["format"] == "FBX export":
            self.fbx_panel.setVisible(True)
            self.currentData["exportSettings"] = FBX_DEFAULT_SETTING
        else:
            self.fbx_panel.setVisible(False)
        self.dataChanged.emit(self.currentData)

    def data(self):
        return self.currentData

    def _pick_selection(self):
        if self.currentData:
            selection = cmds.ls(sl=True,long=True)
            if len(selection):
                self.targetLine.setText(selection[0])
                self.currentData["target"]=selection[0]
                self.dataChanged.emit(self.currentData)
    def _maya_radio_clicked(self):
        self.currentData["base"]="maya"
        self.dataChanged.emit(self.currentData)
    def _game_radio_clicked(self):
        self.currentData["base"]="game"
        self.dataChanged.emit(self.currentData)
