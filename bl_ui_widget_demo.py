# ##### BEGIN GPL LICENSE BLOCK #####
#
#  This program is free software; you can redistribute it and/or
#  modify it under the terms of the GNU General Public License
#  as published by the Free Software Foundation; either version 2
#  of the License, or (at your option) any later version.
#
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with this program; if not, write to the Free Software Foundation,
#  Inc., 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301, USA.
#
# ##### END GPL LICENSE BLOCK #####

# --- ### Header
bl_info = {"name": "BL UI Widgets",
           "description": "UI Widgets to draw in the 3D view",
           "author": "Marcelo M. Marques",
           "version": (1, 0, 3),
           "blender": (2, 80, 75),
           "location": "View3D > side panel ([N]), [BL_UI_Widget] tab",
           "support": "COMMUNITY",
           "category": "3D View",
           "warning": "",
           "doc_url": "https://github.com/mmmrqs/bl_ui_widgets",
           "tracker_url": "https://github.com/mmmrqs/bl_ui_widgets/issues"
           }

# --- ### Change log

# v1.0.3 (09.28.2022) - by Marcelo M. Marques
# Fixed: issue with a 'context is incorrect' situation that would be caused by user calling 'Set_Demo_Panel' repeatedly and too fast

# v1.0.2 (09.25.2022) - by Marcelo M. Marques
# Added: 'is_quadview_region' function to identify whether screen is in QuadView mode and if yes to return the corresponding area and region.
# Added: 'btnRemoTime' session variable to hold the clock time which is constantly updated by the 'terminate_execution' function in demo_panel_op.py
#        so that the N-panel is more precisely informed about the remote panel status when it has to determine how to display the Open/Close button.
# Added: Logic to the 'execute' method of the Set_Demo_Panel class for better displaying the Open/Close button, per item described above.

# v1.0.1 (09.20.2021) - by Marcelo M. Marques
# Chang: just some pep8 code formatting

# v1.0.0 (09.01.2021) - by Marcelo M. Marques
# Added: initial creation

# --- ### Imports
import bpy
import time

from bpy.props import StringProperty, IntProperty, BoolProperty

# --- ### Helper functions
def is_quadview_region(context):
    """ Identifies whether screen is in QuadView mode and if yes returns the corresponding area and region
    """
    for area in context.screen.areas:
        if area.type == 'VIEW_3D':
            if len(area.spaces.active.region_quadviews) > 0:
                region = [region for region in area.regions if region.type == 'WINDOW'][3]
                return (True, area, region)
    return (False, None, None)


# --- ### Properties
class Variables(bpy.types.PropertyGroup):
    OpState1: bpy.props.BoolProperty(default=False)
    OpState2: bpy.props.BoolProperty(default=False)
    OpState3: bpy.props.BoolProperty(default=False)
    OpState4: bpy.props.BoolProperty(default=False)
    OpState5: bpy.props.BoolProperty(default=False)
    OpState6: bpy.props.BoolProperty(default=False)
    RemoVisible: bpy.props.BoolProperty(default=False)
    btnRemoText: bpy.props.StringProperty(default="Open Demo Panel")
    btnRemoTime: IntProperty(default=0)


def is_desired_mode(context=None):
    """ Returns True, when Blender is in one of the desired Modes
        Arguments:
            @context (Context):  current context (optional - as received by the operator)

       Possible desired mode options (as of Blender 2.8):
            'EDIT_MESH', 'EDIT_CURVE', 'EDIT_SURFACE', 'EDIT_TEXT', 'EDIT_ARMATURE', 'EDIT_METABALL',
            'EDIT_LATTICE', 'POSE', 'SCULPT', 'PAINT_WEIGHT', 'PAINT_VERTEX', 'PAINT_TEXTURE', 'PARTICLE',
            'OBJECT', 'PAINT_GPENCIL', 'EDIT_GPENCIL', 'SCULPT_GPENCIL', 'WEIGHT_GPENCIL',
       Additional valid mode option (as of Blender 2.9):
            'VERTEX_GPENCIL'
       Additional valid mode options (as of Blender 3.2):
            'EDIT_CURVES', 'SCULPT_CURVES'
    """
    desired_modes = ['OBJECT', 'EDIT_MESH', 'POSE', ]
    if context:
        return (context.mode in desired_modes)
    else:
        return (bpy.context.mode in desired_modes)


class Set_Demo_Panel(bpy.types.Operator):
    ''' Opens/Closes the remote control demo panel '''
    bl_idname = "object.set_demo_panel"
    bl_label = "Open Demo Panel"
    bl_description = "Turns the remote control demo panel on/off"

    # --- Blender interface methods
    @classmethod
    def poll(cls, context):
        return is_desired_mode(context)

    def invoke(self, context, event):
        # input validation:
        return self.execute(context)

    def execute(self, context):
        if context.scene.var.RemoVisible and int(time.time()) - context.scene.var.btnRemoTime <= 1:
            # If it is active then set its visible status to False so that it be closed and reset the button label
            context.scene.var.btnRemoText = "Open Remote Control"
            context.scene.var.RemoVisible = False
        else:
            # If it is not active then set its visible status to True so that it be opened and reset the button label
            context.scene.var.btnRemoText = "Close Remote Control"
            context.scene.var.RemoVisible = True
            is_quadview, area, region = is_quadview_region(context)
            if is_quadview:
                override = bpy.context.copy()
                override["area"] = area
                override["region"] = region
            # Had to put this "try/except" statement because when user clicked repeatedly too fast 
            # on the operator's button it would crash the call due to a context incorrect situation
            try:
                if is_quadview:
                    context.scene.var.objRemote = bpy.ops.object.dp_ot_draw_operator(override, 'INVOKE_DEFAULT')
                else:    
                    context.scene.var.objRemote = bpy.ops.object.dp_ot_draw_operator('INVOKE_DEFAULT')
            except:
                return {'CANCELLED'}

        return {'FINISHED'}


class OBJECT_PT_Demo(bpy.types.Panel):
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = "BL_UI_Widget"
    bl_label = "BL_UI_Widget"

    @classmethod
    def poll(cls, context):
        return is_desired_mode()

    def draw(self, context):
        if context.space_data.type == 'VIEW_3D' and is_desired_mode():
            remoteVisible = (context.scene.var.RemoVisible and int(time.time()) - context.scene.var.btnRemoTime <= 1)
            # -- remote control switch button
            if remoteVisible:
                op = self.layout.operator(Set_Demo_Panel.bl_idname, text="Close Remote Control")
            else:
                # Make sure the button starts turned off every time
                op = self.layout.operator(Set_Demo_Panel.bl_idname, text="Open Remote Control")
        return None


import bpy.app
from bpy.utils import unregister_class, register_class

# List of classes in this add-on to be registered in Blender's API:
classes = [Variables,
           Set_Demo_Panel,
           OBJECT_PT_Demo,
           ]


def register():
    for cls in classes:
        register_class(cls)
    bpy.types.Scene.var = bpy.props.PointerProperty(type=Variables)


def unregister():
    del bpy.types.Scene.var
    for cls in reversed(classes):
        unregister_class(cls)


if __name__ == '__main__':
    register()
