import maya.cmds as cmds

def main():
    result = cmds.promptDialog(
        title='Set Subdividion Level',
        message='Subdivision Level:',
        button=['OK', 'Cancel'],
        defaultButton='OK',
        cancelButton='Cancel',
        dismissString='Cancel')

    if result == "OK":
        text = cmds.promptDialog(query=True, text=True)
        print(text)
        string_int = int(text)
        selections = cmds.ls(sl=True,long=True)
        allDescendents = cmds.listRelatives(allDescendents=True,path=True,type="shape")
        for shape in allDescendents:
            cmds.setAttr(shape+".smoothLevel",string_int)

if __name__ == '__main__':
    main()