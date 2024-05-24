try:
    from PySide2.QtCore import *
    from PySide2.QtGui import *
    from PySide2.QtWidgets import *
except:
    from PySide6.QtCore import *
    from PySide6.QtGui import *
    from PySide6.QtWidgets import *

import maya.cmds as cmds

COMBINE_MODE =["None", "all", "first children"]
SURFACE_ASSOCIATION =["closestPoint","closestComponent","rayCast"]
INFLUENCE_ASSOCIATION =["closestJoint","closestBone","label","name","oneToOne"]
class MaterialListWidget(QTreeWidget):
    data_changed = Signal()
    def __init__(self, *args, **kwargs):
        super(MaterialListWidget, self).__init__(*args, **kwargs)

        self.setContextMenuPolicy(Qt.CustomContextMenu)
        self.customContextMenuRequested.connect(self.contextMenu)

        self.initUI()

    def initUI(self):
        self.setHeaderLabels(["Material","Target"])

    def contextMenu(self, pos):
        menu = QMenu()
        #右クリックされた場所にあるアイテムを取得
        item = self.itemAt(pos)
        label = "add"
        if item:
            label = "Update from selection"
            remove_action = menu.addAction("Remove")

        add_action = menu.addAction(label)
        action = menu.exec_(self.mapToGlobal(pos))
        if action == add_action:
            self.addMaterial(item)
        elif action == remove_action:
            self.removeMaterial(item)

    def addMaterial(self,item=None):
        selection = cmds.ls(sl=True,long=True)
        materials = cmds.ls(selection,materials=True,long=True)
        others = list(set(selection) - set(materials))

        if len(materials) or len(others):
            if not item:
                item = QTreeWidgetItem()
            if len(materials):
                item.setText(0,materials[0])
            if len(others):
                item.setText(1,others[0])
                item.setData(1,Qt.UserRole,others)
            self.addTopLevelItem(item)
            self.data_changed.emit()

    def removeMaterial(self,item=None):
        #アイテムが選択されている場合削除
        if item:
            self.takeTopLevelItem(self.indexOfTopLevelItem(item))
            self.data_changed.emit()

    def all_data(self):
        items = []
        for i in range(self.topLevelItemCount()):
            item = self.topLevelItem(i)
            data ={"material":item.text(0),"target":item.data(1,Qt.UserRole)}
            items.append(data)
        return items

    def setData(self,data):
        self.clear()
        for d in data:
            item = QTreeWidgetItem()
            item.setText(0,d["material"])
            item.setText(1,d["target"][0])
            item.setData(1,Qt.UserRole,d["target"])
            self.addTopLevelItem(item)

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

        #セットマテリアル
        set_material_layout = QVBoxLayout()
        self.set_material_check_box = QCheckBox("Set Material")
        self.set_material_check_box.clicked.connect(self._set_material_checked)
        set_material_layout.addWidget(self.set_material_check_box)
        self.material_list_widget = MaterialListWidget()
        self.material_list_widget.data_changed.connect(self.materialDataChanged)
        self.material_list_widget.setVisible(False)
        set_material_layout.addWidget(self.material_list_widget)
        main_layout.addLayout(set_material_layout)

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

        #三角化
        self.triangulateCheckBox = QCheckBox("Triangulate")
        self.triangulateCheckBox.clicked.connect(self._transigulate_checked)
        main_layout.addWidget(self.triangulateCheckBox)

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
        self.combineComboBox.setCurrentText(data["combineMode"])

        copy_skin = Qt.Unchecked
        if data["copySkin"]:
            copy_skin = Qt.Checked
            self.skin_settinng_group.setVisible(True)
        else:
            self.skin_settinng_group.setVisible(False)

        self.skinCheckBox.setChecked(copy_skin)

        self.surface_association_combo_box.setCurrentText(data["surfaceAssociation"])
        self.influence_association_combo_box.setCurrentText(data["influenceAssociation"])

        sub2_poly = Qt.Unchecked
        if data["sub2poly"]:
            sub2_poly =Qt.Checked

        self.subDivCheckBox.setChecked(sub2_poly)

        tri = Qt.Unchecked
        if data["triangulate"]:
            tri = Qt.Checked
        self.triangulateCheckBox.setChecked(tri)

        set_material = Qt.Unchecked
        if data["setMaterial"]:
            set_material = Qt.Checked
            self.set_material_check_box.setChecked(set_material)
        self.material_list_widget.setVisible(data["setMaterial"])

        self.material_list_widget.setData(data["materials"])

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

    def _set_material_checked(self):
        if self.currentData:
            checked = self.set_material_check_box.checkState() == Qt.Checked
            self.currentData["setMaterial"]=checked
            self.material_list_widget.setVisible(checked)
            self.dataChanged.emit(self.currentData)

    def materialDataChanged(self):
        if self.currentData:
            materials = self.material_list_widget.all_data()
            self.currentData["materials"] = materials
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

    def _transigulate_checked(self):
        if self.currentData:
            self.currentData["triangulate"]=self.triangulateCheckBox.checkState() == Qt.Checked
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
