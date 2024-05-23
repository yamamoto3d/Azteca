import os.path
from builtins import int
from typing import List, Any

from PySide2.QtWidgets import QHBoxLayout, QTreeWidgetItem, QPushButton, QComboBox
from maya.app.general.mayaMixin import MayaQWidgetDockableMixin
from maya import OpenMayaUI as omui

try:
    from PySide2.QtCore import *
    from PySide2.QtGui import *
    from PySide2.QtWidgets import *
except:
    from PySide6.QtCore import *
    from PySide6.QtGui import *
    from PySide6.QtWidgets import *

import json
import copy
import maya.cmds as cmds
import azteca.build
import azteca.folder_sync
import azteca.game_path_panel

#Global変数
Window = None
FILE_FORMAT =["FBX export", "mayaAscii", "OBJexport"]
COMBINE_MODE =["None", "all", "first children"]
DEF_EXPORT_NODE_DATA ={"enable":True, "target": "", "base": "maya", "path": "", "format": "FBX export"}
DEF_BUILD_NODE_DATA ={"enable":True,
                   "source":"",
                   "target":"",
                   "combineMode":"None",
                   "copySkin":False,
                   "surfaceAssociation":"closestPoint",
                   "influenceAssociation":"closestJoint",
                   "sub2poly":False}
SURFACE_ASSOCIATION =["closestPoint","closestComponent","rayCast"]
INFLUENCE_ASSOCIATION =["closestJoint","closestBone","label","name","oneToOne"]





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

        #path
        path_layout = QHBoxLayout()

        edit_button = QPushButton("Set Path")
        edit_button.clicked.connect(self._open_file_path_dialog)

        self.formatComboBox.addItems(FILE_FORMAT)
        self.formatComboBox.currentIndexChanged.connect(self._change_file_format)

        path_layout.addWidget(edit_button)
        path_layout.addWidget(self.pathLine)
        path_layout.addWidget(self.formatComboBox)

        #mainLayout
        main_layout = QVBoxLayout()

        main_layout.addLayout(target_layout)
        main_layout.addLayout(base_path_layout)
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

    def _change_file_format(self):
        self.currentData["format"] =FILE_FORMAT[self.formatComboBox.currentIndex()]
        self.currentData["path"] =self._extension_check(self.currentData["path"])
        self.pathLine.setText(self.currentData["path"])
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


class BuildSettingPanel(QWidget):
    dataChanged =  Signal(dict)

    def __init__(self, parent=None, *args, **kwargs):
        super(BuildSettingPanel, self).__init__(parent, *args, **kwargs)

        self.currentData = None
        self.initUI()

    def initUI(self):
        main_layout = QVBoxLayout()

        #ソース
        source_layout = QHBoxLayout()
        source_layout.addWidget(QLabel("Source"))
        self.souceLineEdit = QLineEdit()
        self.souceLineEdit.setReadOnly(True)
        source_layout.addWidget(self.souceLineEdit)
        source_pick_button = QPushButton("Pick Selection")
        source_pick_button.clicked.connect(self._source_button_pushed)
        source_layout.addWidget(source_pick_button)

        main_layout.addLayout(source_layout)

        #ターゲット
        target_Layout = QHBoxLayout()
        target_Layout.addWidget(QLabel("Target"))
        self.targetLineEdit = QLineEdit()
        self.targetLineEdit.setReadOnly(True)
        target_Layout.addWidget(self.targetLineEdit)
        target_pick_button = QPushButton("Pick Selection")
        target_pick_button.clicked.connect(self._target_button_pushed)
        target_Layout.addWidget(target_pick_button)

        main_layout.addLayout(target_Layout)

        #Suvdiv
        self.subDivCheckBox = QCheckBox("SubDiv to Polygon")
        self.subDivCheckBox.clicked.connect(self._sub_div_checked)
        main_layout.addWidget(self.subDivCheckBox)

        #コンバイン
        combine_layout = QHBoxLayout()
        combine_layout.addWidget(QLabel("Combine"))
        self.combineComboBox = QComboBox()
        self.combineComboBox.addItems(COMBINE_MODE)
        self.combineComboBox.currentIndexChanged.connect(self._combine_mode_changed)
        combine_layout.addWidget(self.combineComboBox)

        main_layout.addLayout(combine_layout)

        #スキン
        self.skinCheckBox = QCheckBox("Copy target skin weight")
        self.skinCheckBox.clicked.connect(self._copy_skin_checked)
        main_layout.addWidget(self.skinCheckBox)

        self.skin_settinng_group= QGroupBox("Skin Copy Settings")
        skin_group_layout = QVBoxLayout()

        ss_layout=QHBoxLayout()
        ss_layout.addWidget(QLabel("Surface association"))
        self.surface_association_combo_box=QComboBox()
        self.surface_association_combo_box.currentIndexChanged.connect(self._surface_association_changed)
        self.surface_association_combo_box.addItems(SURFACE_ASSOCIATION)
        ss_layout.addWidget(self.surface_association_combo_box)

        ia_layout=QHBoxLayout()
        ia_layout.addWidget(QLabel("Influence Association"))
        self.influence_association_combo_box=QComboBox()
        self.influence_association_combo_box.currentIndexChanged.connect(self._influence_association_changed)
        self.influence_association_combo_box.addItems(INFLUENCE_ASSOCIATION)
        ia_layout.addWidget(self.influence_association_combo_box)

        skin_group_layout.addLayout(ss_layout)
        skin_group_layout.addLayout(ia_layout)
        self.skin_settinng_group.setLayout(skin_group_layout)
        main_layout.addWidget(self.skin_settinng_group)

        #グループ
        self.group = QGroupBox("Build Setting")
        self.group.setLayout(main_layout)

        root_layout = QVBoxLayout()
        root_layout.addWidget(self.group)
        self.setLayout(root_layout)

    def setData(self,data):
        self.souceLineEdit.setText(data["source"])
        self.targetLineEdit.setText(data["target"])
        index = 0
        for t in COMBINE_MODE:
            if data["combineMode"] == t:
                break
            else:
                index += 1

        self.combineComboBox.setCurrentIndex(index)

        copy_skin = Qt.Unchecked
        if data["copySkin"]:
            copy_skin = Qt.Checked
            self.skin_settinng_group.setVisible(True)
        else:
            self.skin_settinng_group.setVisible(False)

        self.skinCheckBox.setChecked(copy_skin)

        sa_id =string_array_to_id(SURFACE_ASSOCIATION,data["surfaceAssociation"])
        self.surface_association_combo_box.setCurrentIndex(sa_id)
        ia_id = string_array_to_id(INFLUENCE_ASSOCIATION,data["influenceAssociation"])
        self.influence_association_combo_box.setCurrentIndex(ia_id)

        sub2_poly = Qt.Unchecked
        if data["sub2poly"]:
            sub2_poly =Qt.Checked

        self.subDivCheckBox.setChecked(sub2_poly)
        self.currentData = data

    def _source_button_pushed(self):
        if self.currentData :
            selection = cmds.ls(sl=True,long=True)
            if len(selection):
                self.souceLineEdit.setText(selection[0])
                self.currentData["source"]=selection[0]
                self.dataChanged.emit(self.currentData)

    def _target_button_pushed(self):
        if self.currentData :
            selection = cmds.ls(sl=True,long=True)
            if len(selection):
                self.targetLineEdit.setText(selection[0])
                self.currentData["target"]=selection[0]
                self.dataChanged.emit(self.currentData)

    def _combine_mode_changed(self):
        if self.currentData:
            self.currentData["combineMode"]=COMBINE_MODE[self.combineComboBox.currentIndex()]
            self.dataChanged.emit(self.currentData)

    def _copy_skin_checked(self):
        if self.currentData:
            checked=self.skinCheckBox.checkState() == Qt.Checked
            self.currentData["copySkin"]=checked
            self.skin_settinng_group.setVisible(checked)
            self.dataChanged.emit(self.currentData)

    def _surface_association_changed(self):
        if self.currentData:
            self.currentData["surfaceAssociation"]=SURFACE_ASSOCIATION[self.surface_association_combo_box.currentIndex()]
            self.dataChanged.emit(self.currentData)

    def _influence_association_changed(self):
        if self.currentData:
            self.currentData["influenceAssociation"]=INFLUENCE_ASSOCIATION[self.influence_association_combo_box.currentIndex()]
            self.dataChanged.emit(self.currentData)

    def _sub_div_checked(self):
        if self.currentData:
            self.currentData["sub2poly"] = self.subDivCheckBox.checkState() == Qt.Checked
            self.dataChanged.emit(self.currentData)

class NodeTreeWidget(QTreeWidget):
    dataStructureChanged = Signal()

    def __init__(self, *args, **kwargs):
        super(NodeTreeWidget, self).__init__(*args, **kwargs)

        self.setContextMenuPolicy(Qt.CustomContextMenu)
        self.customContextMenuRequested.connect(self.contextMenu)
        self.setDragDropMode(QAbstractItemView.InternalMove)

        self.rootBuildNode = QTreeWidgetItem()
        self.rootExportNode = QTreeWidgetItem()


        self.initUI()

    def initUI(self):
        self.setHeaderLabels(["c", "Name"])
        self.setHeaderHidden(True)

        #ビルドルート
        self.rootBuildNode.setText(1,"Build")
        self.rootBuildNode.setCheckState(0,Qt.Checked)
        self.addTopLevelItem(self.rootBuildNode)

        #エクスポートルート
        self.rootExportNode.setText(1,"Export")
        self.rootExportNode.setCheckState(0,Qt.Checked)
        self.addTopLevelItem(self.rootExportNode)

    def dropEvent(self, event):
        source = event.source()

        current_parent=source.currentItem().parent()
        pos = event.pos()
        destination_item = source.itemAt(pos)
        dip = self.dropIndicatorPosition()

        if current_parent is None:
            return

        if destination_item.parent() is None and dip != QAbstractItemView.DropIndicatorPosition.OnItem:
            return

        if destination_item.parent() is not None and dip == QAbstractItemView.DropIndicatorPosition.OnItem:
            return

        if destination_item.parent() is not current_parent:
            if destination_item is not current_parent:
                return

        super(NodeTreeWidget, self).dropEvent(event)
        self.dataStructureChanged.emit()

    def contextMenu(self, point):

        if len( self.selectedItems()) == 0:
            return
        menu = QMenu(self)


        add_action = QAction("Add",self)
        add_action.triggered.connect(self.add_node)
        menu.addAction(add_action)


        delete_action = QAction("Delete",self)
        delete_action.triggered.connect(self.delete_node)
        menu.addAction(delete_action)


        sel = self.selectedItems()
        if self.rootExportNode in sel or self.rootBuildNode in sel:
            add_action.setEnabled(True)
            delete_action.setEnabled(False)
        else:
            add_action.setEnabled(False)
            delete_action.setEnabled(True)

        menu.exec_(self.mapToGlobal(point))

    def add_node(self):
        sel = self.selectedItems()
        root = self.rootExportNode
        text = "New export setting"
        data = copy.copy(DEF_EXPORT_NODE_DATA)

        if self.rootBuildNode in sel:
            root = self.rootBuildNode
            text = "New build setting"
            data = copy.copy(DEF_BUILD_NODE_DATA)

        new_node =QTreeWidgetItem()
        new_node.setText(1,text)
        new_node.setCheckState(0,Qt.Checked)

        new_node.setData(2,Qt.UserRole,data)
        root.addChild(new_node)

        self.dataStructureChanged.emit()

    def delete_node(self):
        sel = self.selectedItems()
        for item in sel:
            parent = item.parent()
            print(item.data(2,Qt.UserRole))
            parent.removeChild(item)

        self.dataStructureChanged.emit()

    def all_data(self):
        build_settings=[]
        export_settings=[]
        for i in range( self.rootBuildNode.childCount()):
            item =self.rootBuildNode.child(i)
            data =item.data(2,Qt.UserRole)
            data["enable"] = item.checkState(0)== Qt.Checked
            build_settings.append(data)

        for i in range(self.rootExportNode.childCount()):
            item =self.rootExportNode.child(i)
            data =item.data(2,Qt.UserRole)
            data["enable"] = item.checkState(0) == Qt.Checked
            export_settings.append(data)
        all_data = {"buildSettings": build_settings, "exportSettings": export_settings,
                    "buildEnable": self.rootBuildNode.checkState(0) == Qt.Checked,
                    "exportEnable": self.rootExportNode.checkState(0) == Qt.Checked}
        return all_data

    def reset_data(self):
        self.rootBuildNode.setCheckState(0,Qt.Checked)
        self.rootExportNode.setCheckState(0,Qt.Checked)
        for i in range(self.rootExportNode.childCount()):
            self.rootExportNode.removeChild(self.rootExportNode.child(0))

        for i in range(self.rootBuildNode.childCount()):
            self.rootBuildNode.removeChild(self.rootBuildNode.child(0))
    def set_all_data(self, all_data):
        self.reset_data()
        if all_data is None:
            return


        if all_data["buildEnable"] is False:
            self.rootBuildNode.setCheckState(0,Qt.Unchecked)

        if all_data["exportEnable"] is False:
            self.rootExportNode.setCheckState(0,Qt.Unchecked)

        export_settings = all_data["exportSettings"]
        build_settings = all_data["buildSettings"]




        for data in build_settings:
            item = QTreeWidgetItem()
            check_state = Qt.Unchecked
            if data["enable"]:
                check_state = Qt.Checked
            item.setCheckState(0,check_state)
            item.setText(1,data["target"])
            item.setData(2,Qt.UserRole,data)
            self.rootBuildNode.addChild(item)

        for data in export_settings:
            item = QTreeWidgetItem()
            check_state = Qt.Unchecked
            if data["enable"]:
                check_state = Qt.Checked
            item.setCheckState(0, check_state)
            item.setText(1, data["target"])
            item.setData(2, Qt.UserRole, data)
            self.rootExportNode.addChild(item)

class BuildAndExport(MayaQWidgetDockableMixin, QWidget):
    def __init__(self, parent=None):
        super(BuildAndExport, self).__init__(parent=parent)

        self.isLoading = True

        self.exportExecButton = QPushButton("Execute Selection")
        self.exportSettingPanel = ExportSettingPanel()
        self.gamePathPanel =azteca.game_path_panel.GamePathPanel()
        self.nodeTree = NodeTreeWidget()

        self.currentItem = None
        self.sync_data ={}

        self.initUI()
        self.load()

        cmds.scriptJob(event=["PostSceneRead", "azteca.build_and_export.load()"], protected=True)
        #cmds.scriptJob(event=["deleteAll", "azteca.build_and_export.load()"], protected=True)
        #cmds.scriptJob(event=["SceneSaved", "azteca.build_and_export.save()"], protected=True)


    def initUI(self):
        main_layout = QVBoxLayout()
        #ゲームパス選択
        main_layout.addWidget(self.gamePathPanel)
        # ツリーウィジェット
        self.nodeTree.currentItemChanged.connect(self.current_item_changed)
        self.nodeTree.dataStructureChanged.connect(self.data_structure_changed)
        self.nodeTree.itemChanged.connect(self.data_structure_changed)
        main_layout.addWidget(self.nodeTree)

        #エクスポート設定パネル
        self.exportSettingPanel.dataChanged.connect(self.export_setting_changed)
        self.exportSettingPanel.setVisible(False)

        main_layout.addWidget(self.exportSettingPanel)

        #ビルド設定パネル
        self.buildSettingPanel = BuildSettingPanel()
        self.buildSettingPanel.dataChanged.connect(self.export_setting_changed)
        self.buildSettingPanel.setVisible(False)


        main_layout.addWidget(self.buildSettingPanel)

        #実行レイアウト
        execLayout: QHBoxLayout = QHBoxLayout()
        execLayout.addWidget(QLabel("Execute"))

        #全部実行ボタン
        execute_all_button = QPushButton("Excute All")
        execute_all_button.clicked.connect(self._executeAll)
        execLayout.addWidget(execute_all_button)

        main_layout.addLayout(execLayout)

        #実行ボタン
        self.exportExecButton.clicked.connect(self._executeSelection)

        execLayout.addWidget(self.exportExecButton)

        #フォルダシンク
        main_layout.addItem(QSpacerItem(0, 0, QSizePolicy.Maximum, QSizePolicy.Maximum))
        self.folder_sync_ui =azteca.folder_sync.FolderSync()
        self.folder_sync_ui.dataChanged.connect(self._folder_sync_changed)
        main_layout.addWidget(self.folder_sync_ui)

        #メインレイアウトセット
        self.setLayout(main_layout)
        self.setWindowTitle('Build And Export')

    def current_item_changed(self, current, previous):
        if current:
            self.isLoading =True
            self.currentItem = current
            parent = current.parent()
            if parent ==  self.nodeTree.rootExportNode:
                #エクスポートノード
                self.exportSettingPanel.setVisible(True)
                self.buildSettingPanel.setVisible(False)

                data =current.data(2,Qt.UserRole)
                self.exportSettingPanel.setData(data)


            elif parent == self.nodeTree.rootBuildNode:
                #ビルドノード
                self.buildSettingPanel.setVisible(True)
                self.exportSettingPanel.setVisible(False)

                data = current.data(2, Qt.UserRole)
                self.buildSettingPanel.setData(data)

            else:#ルートノード
                self.exportSettingPanel.setVisible(False)
                self.buildSettingPanel.setVisible(False)
            self.isLoading=False
        else:#選択なし
            self.exportSettingPanel.setData(None)
            self.exportSettingPanel.setVisible(False)

    def load(self):
        self.isLoading =True
        data =self._load_json()
        self.nodeTree.set_all_data(data)
        self.folder_sync_ui.set_data(data["syncData"])
        self.isLoading = False

    def data_structure_changed(self):
        self.save_json()

    def export_setting_changed(self, data):
        if self.currentItem:
            self.isLoading=True
            self.currentItem.setData(2, Qt.UserRole, data)
            self.isLoading=False
            self.currentItem.setText(1,data["target"])
            self.isLoading=False
        self.save_json()

    def _folder_sync_changed(self, data):
        print(data)
        self.sync_data=data
        self.save_json()

    def _executeSelection(self):
        selected_items = self.nodeTree.selectedItems()
        if len(selected_items):
            item =selected_items[0]
            data = item.data(2,Qt.UserRole)
            parent = item.parent()

            if parent == self.nodeTree.rootExportNode:
                self._export(data)
            elif parent == self.nodeTree.rootBuildNode:
                self._build(data)

    def _executeAll(self):
        allData = self.nodeTree.all_data()
        if allData["buildEnable"]:
            build_settings : list[dict] = allData["buildSettings"]
            for data in build_settings:
                if data["enable"]:
                    self._build(data)
        if allData["exportEnable"]:
            export_settings: list[dict] = allData["exportSettings"]
            for data in export_settings:
                if data["enable"]:
                    self._export(data)

    def _build(self,data):
        source = data["source"]
        target = data["target"]
        combine_mode =data["combineMode"]
        copy_skin =data["copySkin"]
        sub_to_poly = data["sub2poly"]
        surface_association =data["surfaceAssociation"]
        influence_association =data["influenceAssociation"]

        azteca.build.main(source,target,sub_to_poly,combine_mode,copy_skin,surface_association,influence_association)
    def _export(self,data):
        options = "v=0"
        if data["format"] == "OBJexport":
            options = "groups=1;ptgroups=1;materials=1;smoothing=1;normals=1"

        base_path = cmds.workspace(listFullWorkspaces=True)[0]
        if data["base"] == "game":
            base_path = cmds.optionVar(q=azteca.game_path_panel.GAME_PATH_OPTION_VAR_NAME)

        path = base_path+data["path"]

        cmds.select(data["target"])
        cmds.file(path, force=True, options=options, pr=True, type=data["format"], exportSelected=True)

    def save_json(self):
        if self.isLoading is False:
            scene_name = cmds.file(query=True, sceneName=True)
            if scene_name == "":
                return
            else:
                scene_name =scene_name.replace(scene_name.split(".")[-1],"json")

            allItem =  self.nodeTree.all_data()
            allItem["syncData"]=self.sync_data
            print("Build and Expot:Save Setting File:"+scene_name)
            with open(scene_name, "w") as f:
                json.dump(allItem, f, indent=2)

    def _load_json(self):
        scene_name = cmds.file(query=True, sceneName=True)
        json_str = ""
        json_data = None

        if scene_name == "":
            return None

        scene_name = scene_name.replace(scene_name.split(".")[-1],"json")

        if os.path.isfile(scene_name):
            with open(scene_name) as f:
                json_str = f.read()
                print("読み出したJSONです")
                print(json_str)

        if json_str != "":
            json_data = json.loads(json_str)

        return json_data

def load():
    print("ロードが呼ばれました")
    if Window is not None:
        Window.load()

def save():
    if Window is not None:
        Window.save_json()

def open_window(restore=False):
    global Window

    if restore:
        restored_control = omui.MQtUtil.getCurrentParent()

    if Window is None:

        Window = BuildAndExport()
        #Window.setObjectName('AZTBuildAndExportPanel')

    if restore:
        mixin_ptr = omui.MQtUtil.findControl(Window.objectName())
        omui.MQtUtil.addWidgetToMayaLayout(int(mixin_ptr), int(restored_control))
    else:
        Window.show(dockable=True, height=600, width=300,
                    uiScript='import azteca.build_and_export; azteca.build_and_export.open_window(restore=True)')

    return Window

def string_array_to_id(string_array,key_string):
    for i in range(len(string_array)):
        if string_array[i] == key_string:
            return i
    return 0

def main():
    ui = open_window()
    return ui



if __name__ == '__main__':
    main()
