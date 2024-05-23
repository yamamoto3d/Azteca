import maya.cmds as cmds
import maya.mel as mel

TRASH_BOX = 'trash_box'
def swap(source,target,keep_target = True):
    target_parent = cmds.listRelatives(target, parent =True, fullPath=True)[0]
    print("ペアレントパス:"+target_parent)
    after_parent =target_parent+"|"+cmds.parent(source,target_parent)[0]
    print("ペアレント後"+after_parent)
    name = target.split("|")[-1]
    print("名前:"+name)

    if keep_target:
        if cmds.objExists(TRASH_BOX) is False:
            cmds.group(empty=True,name=TRASH_BOX,world=True)
        cmds.parent(target,TRASH_BOX)

    cmds.rename(after_parent,name)

def smooth_mesh_preview_to_polygon(target):
    targets = cmds.listRelatives(target,path=True,shapes= False,allDescendents=True,type="shape")
    if targets :
        for t in targets:
            preview_on = cmds.getAttr(t+".displaySmoothMesh")
            if preview_on>0:
                div = cmds.getAttr(t+".smoothLevel")
                cmds.polySmooth(t,constructionHistory=False, dv=div,continuity=1, keepBorder=False,keepHardEdge=False)
                cmds.setAttr(t+".displaySmoothMesh",False)


def combine_child(target):
    children = cmds.listRelatives(target, children=True, path=True)
    for child in children:
        all_decendents = cmds.listRelatives(child,children=True,allDescendents=True,type="mesh",path=True)
        if all_decendents is not None:
            child_name=child.split("|")[-1]
            if len(all_decendents) >1:
                result = cmds.polyUnite(all_decendents, constructionHistory=False,name =child)
                new_path=cmds.parent(result,target)
                cmds.rename(new_path, child_name)

            if len(all_decendents) is 1:#グループないに一個の子供があるケース
                #メッシュ単体の場合とグループの中にメッシュが一つのケースはこの処理で判別できる
                #メッシュ単体はシェイプのみが出てきて、グループ内の単体メッシュの場合そのトランスフォームとシェイプがある
                mesh_or_group=len( cmds.listRelatives(child,allDescendents=True))==2
                if mesh_or_group:
                    only_child_path =cmds.listRelatives(child,path=True)
                    new_path=cmds.parent(only_child_path,target)
                    cmds.delete(child)
                    cmds.rename(new_path,child_name)

    return  target


def combine_all(target):
    all_decendents = cmds.listRelatives(target, children=True, allDescendents=True, type="mesh", path=True)
    new_path = cmds.polyUnite(all_decendents, constructionHistory=False, name=target)[0]
    cmds.delete(target)
    return new_path

def triangulate_mesh(target):
    cmds.polyTriangulate(target, constructionHistory=False)

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

def main(source,
         target,
         sub_div_to_poly=False,
         combine_mode="None",
         copy_skin=False,
         surface_association="closestPoint",
         influence_association="closestJoint",
         triangulate=False):
    d_copy=cmds.duplicate(source,fullPath=True)[0]
    print("デュプリケート後:"+d_copy)
    if sub_div_to_poly:
        smooth_mesh_preview_to_polygon(d_copy)

    if combine_mode == "all":
        d_copy = combine_all(d_copy)
        print("全コンバイン後:"+d_copy)
    elif combine_mode =="first children":
        d_copy = combine_child(d_copy)
        print("子コンバイン後:"+d_copy)

    if triangulate:
        print("トライアングレート")
        triangulate_mesh(d_copy)

    if copy_skin:
        copy_skin_keep_joint(target,d_copy,surface_association,influence_association)

    swap(d_copy,target)

