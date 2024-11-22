import os
import maya.cmds as cmds
from PIL import Image
import shutil
from PySide6.QtWidgets import QApplication, QLabel, QComboBox, QDialog, QLineEdit, QWidget, QProgressBar, QCheckBox, QVBoxLayout, QPushButton, QFileDialog
from maya import OpenMayaUI as omui
from shiboken6 import wrapInstance




class fbxExport:
    def __init__(self, file_path, filename):
        self.selected_objects = cmds.ls(sl=True)
        self.file_path = file_path
        self.layer_name = 'EXPORT'
        self.workspace = self.filePath()
        self.file_name = (self.workspace)+filename
        
        def getTexFile(self):

            textures_list= []
            for s in self.selectMeshOnly():
                if s == False:
                    cmds.warning('Selection is empty!')
                    return False
                t = (cmds.listRelatives(s, ad=True))
                if t is not None:
                        material = (cmds.listConnections(t, type='shadingEngine'))
                        material = (cmds.listConnections(material, type='lambert'))
                        textures = (cmds.listConnections(material, type='file'))
                        for t in textures:
                            try: 
                                texture_file = cmds.getAttr(t+'.fileTextureName')
                                if os.path.exists(texture_file):
                                    print(f"The texture file exists at: {texture_file}")
                                    textures_list.append(texture_file)
                                else:
                                    print(f"Warning: The texture file does not exist at: ({texture_file})")
                                    self.texture_file_name = os.path.basename(texture_file)
                                
                            except Exception as e: 
                                if texture_file is None: 
                                    cmds.error("Node has no file attached:", e)
                                    return False

                                
                            
            print('textlist',textures_list)
            return textures_list



        def convertPng(self):
            fname = os.path.join(self.file_path)
            os.chdir(fname)
            save_dir = self.workspace+f'/export/textures'
            for texture_file in self.getTexFile():
                print('Converting file:', texture_file)

                if not texture_file.endswith('.png'):
                    try:
                        im = Image.open(texture_file)  
                        new_filename = f'{os.path.splitext(texture_file)[0]}.png' 
                        new_file_path = os.path.join(save_dir, os.path.basename(new_filename)) 
                        im.save(new_file_path) 
                        print(f'Converted {texture_file} to {new_filename}')
                    except Exception as e:
                        print(f'Error converting {texture_file}: {e}')
                else:
                    print(f'{texture_file} is already a PNG, skipping.')

        
        def exportSelTexture(self):
    
            save_path= self.workspace+f'/export/textures/{self.texture_file_name}'
            new_textures = []
            
            if not self.selected_objects:
                    cmds.warning("Nothing is selected.")
                    return False
            for mesh in self.selected_objects:
                for texture in self.getTexFile():
                    new_textures.append(shutil.copyfile(texture, save_path))

                return new_textures


    def getBoundingBox(self):
        for object_name in self.selectMeshOnly():
            if cmds.objExists(object_name+f'UCX_{object_name}'):
                print(f'bounding box for {object_name} alr exists')
                return True
            else:
                cmds.duplicate(object_name, name = object_name+'duplicate')
                bbox = cmds.geomToBBox(object_name+'duplicate', name = f'UCX_{object_name}')
                return bbox


    def currentUv(self):
            uv_sets = cmds.polyUVSet(self.selectMeshOnly(), q=True, allUVSets=True)
            return uv_sets
    



    def duplicateUvSet(self, obj, uv_set_name, new_uv_set_name):

        #if not cmds.polyUVSet(obj, query=True, uvSet=uv_set_name):
            #raise RuntimeError(f"UV set '{uv_set_name}' not found on object '{obj}'")


        cmds.polyUVSet(obj, create=True, uvSet=new_uv_set_name)


        cmds.polyCopyUV(obj, uvSetNameInput=uv_set_name, uvSetName=new_uv_set_name)






    def checkUv(self):

        self.currentUv()

        for set in self.currentUv():
            if set.startswith('uv_set'):
                return True
            else:
                self.duplicateUvSet(self.selectMeshOnly(), set, 'LightmapUV'+set)
            return True


def runFbxExport():
    fbx_export = fbxExport(file_path=r'C:\Users\Soleil\Documents\Tech Art\Project\Project', filename='\Source\Arcade_Room.mb')
    print(fbx_export.filePath()) # Returns baseDirectory
    print(fbx_export.checkFileLocation()) # Checks designated file is where it should be
    print(fbx_export.selectMeshOnly()) # Deselects anything that isn't a mesh
    print(fbx_export.exportSelected()) # Exports selected mesh to FBX
    print(fbx_export.exportAll()) # Exports all mesh to FBX
    print(fbx_export.checkNaming()) # Renames mesh to fit working standard
    print(fbx_export.layerExists()) # Checks if export layer exists and if not, creates it
    print(fbx_export.moveObject()) # Moves mesh to export layer
    print(fbx_export.bottomPivot()) # Bottom and centers the mesh and pivot point
    print(fbx_export.getTexFile()) # Gets names of textures assigned to selected mesh
    print(fbx_export.exportSelTexture()) #Makes a copy of the texture into the export/texture folder
    print(fbx_export.convertPng()) # Converts textures to PNGs
    print(fbx_export.getBoundingBox()) # Creates bounding box / collision mesh for selected mesh
    print(fbx_export.currentUv()) # Returns existing UV sets
    print(fbx_export.checkUv()) # Creates Lightmap UV set if one does not already exist





class fbxExporterUI(QDialog):
    
    def __init__(self):
        # Set Maya's main window as the parent
        main_window = self.mayaMainWindow() 
        super(fbxExporterUI, self).__init__(parent=main_window)
        self.export_path = None
        self.setupUI()


    def mayaMainWindow(self):
        # Retrieve the Maya main window as the parent
        main_window_pointer = omui.MQtUtil.mainWindow()
        return wrapInstance(int(main_window_pointer), QDialog)


    def setupUI(self):
        self.setWindowTitle("FBX Export Options")
        layout = QVBoxLayout(self)
        # Export Textures Checkbox
        self.export_checkbox = QCheckBox("Export Textures")
        self.export_checkbox.stateChanged.connect(self.toggleDropdown)

        # Export textures dropdown
        self.texture_dropdown_label = QLabel("Texture File Type:")
        self.texture_dropdown = QComboBox()
        self.texture_dropdown.addItem("PNG")
        self.texture_dropdown.addItem("JPG")
        self.texture_dropdown.addItem("TGA")
        self.texture_dropdown_label.hide()
        self.texture_dropdown.hide()

        # Path input and button
        self.set_path_field = QLineEdit(self)
        self.set_path_field.setPlaceholderText("Select the export path...")
        set_btn = QPushButton('Set Export Folder', self)
        set_btn.clicked.connect(self.setPath)
        btn_widget = QWidget()
        btn_layout = QVBoxLayout(btn_widget)

        exportFBXBtn = QPushButton('Export FBX')
        exportFBXBtn.clicked.connect(self.exportFbx)
        btn_layout.addWidget(exportFBXBtn)

        # Progress bar 
        self.progress_bar = QProgressBar(self)
        self.progress_bar.setRange(0, 100)
        self.progress_bar.setValue(0)
        self.progress_bar.setVisible(False)

        # Layout setup
        layout.addWidget(self.export_dropdown)
        layout.addWidget(self.bb_checkbox)
        layout.addWidget(self.pivot_checkbox)        
        layout.addWidget(self.uv_checkbox)
        layout.addWidget(self.export_checkbox)
        layout.addWidget(self.texture_dropdown_label)
        layout.addWidget(self.texture_dropdown)
        layout.addWidget(self.set_path_field)
        layout.addWidget(set_btn)
        layout.addWidget(btn_widget)
        layout.addWidget(self.progress_bar)  

def showUI():
    ui = fbxExporterUI()
    ui.show()
    return ui

if __name__ == "__main__":
    import sys
    app = QApplication.instance() or QApplication(sys.argv) 
    window = showUI()
    app.exec()