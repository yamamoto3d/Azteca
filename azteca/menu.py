# -*- coding: utf-8 -*-
from maya import cmds


def main():

    # メニューバー

    cmds.menu( label='Azteca', parent='MayaWindow', tearOff=True )

    # Window

    cmds.menuItem( label='Window', tearOff=True, subMenu=True )

    cmds.menuItem( label='Build and Export', command='import azteca.build_and_export; azteca.build_and_export.main()' )

    cmds.setParent( '..', menu=True )

    # Modeling

    cmds.menuItem( label='Modeling', tearOff=True, subMenu=True )

    cmds.menuItem( label='Set Subdivision Level', command='import azteca.set_subdivision_level;azteca.set_subdivision_level.main()' )
    cmds.menuItem( label='Delete History Keep Skin', command='import azteca.delete_history_keep_skin;azteca.delete_history_keep_skin.main()' )
    cmds.setParent( '..', menu=True )

    # Camera
    cmds.menuItem( label='Camera', tearOff=True, subMenu=True )
    cmds.menuItem( label='Create Camera Projection Material', command='import azteca.create_camera_projection_material;azteca.create_camera_projection_material.main()' )
    cmds.menuItem( label='Focal Length Up', command='import azteca.focalLength_up;azteca.focalLength_up.main(True)' )
    cmds.menuItem( label='Focal Length Down', command='import azteca.focalLength_up;azteca.focalLength_up.main(False)' )
    cmds.setParent( '..', menu=True )