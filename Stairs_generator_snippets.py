from PySide6 import QtWidgets
import maya.cmds as cmds
from shiboken6 import wrapInstance
from maya import OpenMayaUI as omui


def get_maya_window():
    main_window_pointer = omui.MQtUtil.mainWindow()
    if main_window_pointer is not None:
        return wrapInstance(int(main_window_pointer), QtWidgets.QDialog)


class stairObject:
    def __init__(self, stepcount, name, dimx, dimy, dimz):
        self.step = stepcount
        self.base_name = name 
        self.dimz = dimz

    def cubeRepeat(self):
        for i in range(self.step):
            object_name = f"{self.base_name}{i+1:02d}"  
            cmds.polyCube(sx=1, sy=1, sz=1, h=self.dimy, w=self.dimx, d=self.dimz, name=object_name)
            cmds.move(self.dimx * i, self.dimy * i, 0, object_name, absolute=True)
            





class stairObjectUI(QtWidgets.QDialog):
    def __init__(self, parent=get_maya_window()):
        super(stairObjectUI, self).__init__(parent)

        self.setWindowTitle("Stair Object Generator")
        self.setFixedSize(300, 400)

        layout = QtWidgets.QVBoxLayout(self)


        self.dimz_label = QtWidgets.QLabel("Depth (Z):")
        self.dimz_input = QtWidgets.QDoubleSpinBox()
        self.dimz_input.setRange(0.1, 100.0)
        self.dimz_input.setValue(1.0)


        self.generate_button = QtWidgets.QPushButton("Generate Staircase")
        self.generate_button.clicked.connect(self.generate_staircase)

        layout.addWidget(self.step_count_label)
        layout.addWidget(self.step_count_input)
        layout.addWidget(self.dimz_label)
        layout.addWidget(self.dimz_input)
        layout.addWidget(self.generate_button)

    def generate_staircase(self):
        step_count = self.step_count_input.value()
        base_name = self.name_input.text()
        dimx = self.dimx_input.value()
        dimy = self.dimy_input.value()
        dimz = self.dimz_input.value()

        staircase = stairObject(step_count, base_name, dimx, dimy, dimz)
        staircase.cubeRepeat()

def show_stair_object_ui():
    global stair_ui
    try:
        stair_ui.close()  
    except:
        pass
    stair_ui = stairObjectUI()
    stair_ui.show()


show_stair_object_ui()

