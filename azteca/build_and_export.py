import os.path
from builtins import int
from typing import List, Any

from PySide2.QtWidgets import QHBoxLayout, QTreeWidgetItem, QPushButton, QComboBox
from maya.app.general.mayaMixin import MayaQWidgetDockableMixin
from maya import OpenMayaUI as omui
from maya import OpenMaya as om
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
import azteca.build_setting_panel
import azteca.export_setting_panel

#Global変数
Window = None
DEF_EXPORT_NODE_DATA ={"enable":True,
                       "target": "",
                       "base": "maya",
                       "path": "",
                       "format": "FBX export",
                       "exportSettings": {}}
DEF_BUILD_NODE_DATA ={"enable":True,
                    "source":"",
                    "target":"",
                    "combineMode":"None",
                    "copySkin":False,
                    "surfaceAssociation":"closestPoint",
                    "influenceAssociation":"closestJoint",
                    "sub2poly":False,
                    "triangulate":False,
                    "setMaterial":False,
                    "materials":[]}



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
        self.exportSettingPanel =azteca.export_setting_panel.ExportSettingPanel()
        self.gamePathPanel =azteca.game_path_panel.GamePathPanel()
        self.nodeTree = NodeTreeWidget()

        self.currentItem = None

        self.initUI()
        self.load()

        cmds.scriptJob(event=["PostSceneRead", "azteca.build_and_export.load()"], protected=True)
        #cmds.scriptJob(event=["deleteAll", "azteca.build_and_export.load()"], protected=True)
        #cmds.scriptJob(event=["SceneSaved", "azteca.build_and_export.save()"], protected=True)


    def initUI(self):
        main_layout = QVBoxLayout()

        #ファイル関連
        file_layout = QHBoxLayout()
        refresh_button = QPushButton("Refresh")
        refresh_button.clicked.connect(self.load)
        file_layout.addWidget(refresh_button)

        import_button = QPushButton("Import")
        import_button.clicked.connect(self.import_json)
        file_layout.addWidget(import_button)

        main_layout.addLayout(file_layout)

        #ゲームパス選択
        main_layout.addWidget(self.gamePathPanel)

        #タブウィジェットを作成
        tab_widget = QTabWidget()
        main_layout.addWidget(tab_widget)

        #タブ1
        tab1 = QWidget()
        tab1_layout = QVBoxLayout()
        tab1.setLayout(tab1_layout)

        # ツリーウィジェット
        self.nodeTree.currentItemChanged.connect(self.current_item_changed)
        self.nodeTree.dataStructureChanged.connect(self.data_structure_changed)
        self.nodeTree.itemChanged.connect(self.data_structure_changed)
        tab1_layout.addWidget(self.nodeTree)

        #エクスポート設定パネル
        self.exportSettingPanel.dataChanged.connect(self.export_setting_changed)
        self.exportSettingPanel.setVisible(False)

        tab1_layout.addWidget(self.exportSettingPanel)

        #ビルド設定パネル
        self.buildSettingPanel =azteca.build_setting_panel.BuildSettingPanel()
        self.buildSettingPanel.dataChanged.connect(self.export_setting_changed)
        self.buildSettingPanel.setVisible(False)


        tab1_layout.addWidget(self.buildSettingPanel)

        #実行レイアウト
        execLayout: QHBoxLayout = QHBoxLayout()
        execLayout.addWidget(QLabel("Execute"))

        #全部実行ボタン
        execute_all_button = QPushButton("Excute All")
        execute_all_button.clicked.connect(self._executeAll)
        execLayout.addWidget(execute_all_button)

        tab1_layout.addLayout(execLayout)

        #実行ボタン
        self.exportExecButton.clicked.connect(self._executeSelection)

        execLayout.addWidget(self.exportExecButton)
        tab1_layout.addItem(QSpacerItem(0, 0, QSizePolicy.MinimumExpanding, QSizePolicy.MinimumExpanding))


        #タブ2
        tab2 = QWidget()
        tab2_layout = QVBoxLayout()
        tab2.setLayout(tab2_layout)

        #フォルダシンク
        self.folder_sync_ui =azteca.folder_sync.FolderSync()
        self.folder_sync_ui.dataChanged.connect(self._folder_sync_changed)
        tab2_layout.addWidget(self.folder_sync_ui)
        tab2_layout.addItem(QSpacerItem(0, 0, QSizePolicy.MinimumExpanding, QSizePolicy.MinimumExpanding))


        #タブウィジェットにタブを追加
        tab_widget.addTab(tab1, "Build and Export")
        tab_widget.addTab(tab2, "Folder Sync")

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
        if data is not None:
            self.folder_sync_ui.set_data(data["syncData"])
        self.isLoading = False

    def import_json(self):
        #読み込むJSONファイルを選択するダイアログを開く
        file_path = QFileDialog.getOpenFileName(self, "Open JSON File", "", "JSON Files (*.json)")
        #JSONファイルが存在する場合読み出し
        if file_path[0] != "":
            with open(file_path[0]) as f:
                self.isLoading = True
                json_data = json.load(f)
                self.nodeTree.set_all_data(json_data)
                if json_data is not None:
                    self.folder_sync_ui.set_data(json_data["syncData"])
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
        triangulate_flag =data["triangulate"]
        set_material =data["setMaterial"]
        materials =data["materials"]
        azteca.build.main(source,
                          target,
                          sub_to_poly,
                          combine_mode,
                          copy_skin,
                          surface_association,
                          influence_association,
                          triangulate=triangulate_flag,
                          setMaterial=set_material,
                            materials=materials)
    def _export(self,data):
        base_path = cmds.workspace(listFullWorkspaces=True)[0]
        if data["base"] == "game":
            base_path = cmds.optionVar(q=azteca.game_path_panel.GAME_PATH_OPTION_VAR_NAME)

        path = base_path + data["path"]
        cmds.select(data["target"])

        if data["format"] == "FBX export":
            es = data["exportSettings"]
            cmds.FBXPushSettings()
            try:
                cmds.FBXResetExport()

                cmds.FBXExportSmoothingGroups("-v", es["smoothing_group"])
                cmds.FBXExportSmoothMesh("-v", es["smooth_mesh"])
                cmds.FBXExportHardEdges("-v", es["split_vertex"])

                tr = "false"
                if es["triangulate"]:
                    tr = "true"
                cmds.FBXProperty("Export|IncludeGrp|Geometry|Triangulate", "-v",int(es["triangulate"]))
                cmds.FBXExportTangents("-v", es["tangent"])

                cmds.FBXExportSkins("-v", es["skinning"])
                # cmds.FBXProperty("Export|IncludeGrp|Animation|Deformation|Shape", "-v", 0)
                cmds.FBXExportShapes("-v", es["blendshape"])

                cmds.FBXProperty("Export|IncludeGrp|Animation", "-v", int(es["animation"]))
                cmds.FBXExportUpAxis(es["up_axis"]) #or z
                cmds.FBXExportEmbeddedTextures("-v", es["embedded_textures"])

                cmds.FBXExportInAscii("-v", int(es["file_type"] == "ascii"))
                cmds.FBXExportFileVersion("-v", "FBX201400")

                cmds.FBXExportCameras("-v", 0)
                cmds.FBXExportLights("-v", 0)
                om.MGlobal.executeCommand('FBXExport("-f", "{}", "-s")'.format(path))
            finally:
                cmds.FBXPopSettings()
        else:
            options = "v=0"
            if data["format"] == "OBJexport":
                options = "groups=1;ptgroups=1;materials=1;smoothing=1;normals=1"

            cmds.file(path, force=True, options=options, pr=True, type=data["format"], exportSelected=True)

    def save_json(self):
        if self.isLoading is False:
            scene_name = cmds.file(query=True, sceneName=True)
            if scene_name == "":
                return
            else:
                scene_name =scene_name.replace(scene_name.split(".")[-1],"json")

            allItem =  self.nodeTree.all_data()
            allItem["syncData"]=self.folder_sync_ui.get_data()
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

def main():
    ui = open_window()
    return ui



if __name__ == '__main__':
    main()
