import maya.cmds as cmds
import maya.mel as mel

def copy_skin_keep_joint(source, destination, surface_association="closestPoint", influence_association="closestJoint"):

    histories = cmds.listHistory(source, pruneDagObjects=True, interestLevel=2)
    source_skincluster = cmds.ls(histories, type="skinCluster")[0]
    max_influences = cmds.getAttr(source_skincluster+".maxInfluences")
    #skin
    joints = cmds.skinCluster(source, inf=True, q=True)


    selection_to_shapes = cmds.listRelatives(destination, allDescendents=True, path=True, type="shape", noIntermediate=True)
    # copy_targetにまずスキンクラスターを作る

    for shape in selection_to_shapes:
        add = joints+[shape]
        print(add)
        destination_skin_cluster = cmds.skinCluster(add ,obeyMaxInfluences =True, maximumInfluences=max_influences)[0]


        cmds.copySkinWeights(sourceSkin=source_skincluster,
                         destinationSkin=destination_skin_cluster,
                         noMirror=True,
                         surfaceAssociation =surface_association,
                         influenceAssociation = influence_association)
def main():
    selection = cmds.ls(sl=True, long=True)
    for target in selection:
        all_decendents = cmds.listRelatives(target, children=True, allDescendents=True, type="mesh", path=True)
        skin_cluster = cmds.ls(cmds.listHistory(target), type="skinCluster")
        if skin_cluster:
            cmds.select(target, r=True)
            mel.eval("GoToBindPose")
            cmds.select(clear=True)

            d_copy = cmds.duplicate(target, fullPath=True)[0]
            print("デュプリケート後:" + d_copy)
            copy_skin_keep_joint(target, d_copy)
            cmds.delete(target)
            cmds.rename(d_copy, target.split("|")[-1])

            intermediate_objects = cmds.ls(type="shape", intermediateObjects=True)
            for intermediate_object in intermediate_objects:
                #何にも接続されていないオブジェクトを削除
                if not cmds.listConnections(intermediate_object):
                    cmds.delete(intermediate_object)
