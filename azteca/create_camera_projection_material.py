# -*- coding: utf-8 -*-
from maya import cmds
def main(prefix="Mat_"):
    selection = cmds.ls(sl=True, long=True)
    cameraShape = cmds.listRelatives(selection, fullPath=True, allDescendents=True, type="camera")
    if cameraShape:
        cameraShape = cameraShape[0]
    else:
        print("Select camera")
        return
    camera = cmds.listRelatives(cameraShape, parent=True)[0]
    mesh = cmds.listRelatives(selection, fullPath=True, allDescendents=True, type="mesh",noIntermediate=True)

    print(camera)

    #ランバートマテリアルを作成
    lambert = cmds.shadingNode("lambert", asShader=True)
    sg = cmds.sets(renderable=True, noSurfaceShader=True, empty=True, name=prefix + camera + "SG")
    cmds.connectAttr(lambert + ".outColor", sg + ".surfaceShader")
    cmds.setAttr(lambert + ".ambientColor", 1, 1, 1, type="double3")
    cmds.setAttr(lambert + ".diffuse",0)


    projection = cmds.shadingNode("projection", asUtility=True)
    cmds.connectAttr(projection + ".outColor", lambert + ".color")
    cmds.setAttr(projection + ".fitType", 2)
    cmds.setAttr(projection + ".projType", 8)
    cmds.connectAttr(cameraShape + ".message", projection + ".linkedCamera")

    file = cmds.shadingNode("file", asTexture=True)
    cmds.connectAttr(file + ".outColor", projection + ".image")

    if mesh:
        cmds.sets(mesh,edit=True,forceElement=sg)

    cmds.rename(lambert, prefix + camera)
    cmds.select(file)