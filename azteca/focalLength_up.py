# -*- coding: utf-8 -*-
from maya import cmds

def main(up=True):
    model_panel =cmds.getPanel(type='modelPanel')
    for mp in model_panel:
        camera = cmds.modelPanel(mp, q=True, camera=True)
        #カメラが平行投影出ない場合はスキップ
        if not cmds.getAttr(camera + ".orthographic"):
            #カメラの焦点距離を取得
            focalLength = cmds.getAttr(camera + ".focalLength")
            new_focalLength = 0
            if up:
                if focalLength >= 135:
                    new_focalLength = 200
                elif focalLength >= 85:
                    new_focalLength = 135
                elif focalLength >= 50:
                    new_focalLength = 85
                elif focalLength >= 35:
                    new_focalLength = 50
                elif focalLength >= 24:
                    new_focalLength = 35
                elif focalLength >= 16:
                    new_focalLength = 24
                else:
                    new_focalLength = 16
            else:
                if focalLength <= 24:
                    new_focalLength = 16
                elif focalLength <= 35:
                    new_focalLength = 24
                elif focalLength <= 50:
                    new_focalLength = 35
                elif focalLength <= 85:
                    new_focalLength = 50
                elif focalLength <= 135:
                    new_focalLength = 85
                elif focalLength <= 200:
                    new_focalLength = 135
                else:
                    new_focalLength = 200
            cmds.setAttr(camera + ".focalLength", new_focalLength)
            #ヘッドアップディスプレイで焦点距離を表示
            cmds.headsUpMessage(camera + " focalLength:" + str(new_focalLength), time=2)