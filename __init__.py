import bpy
import time
import sys
from . import actions
from . import prefs
from . import ui_panel
from . import version
from bpy.app.handlers import persistent

bl_info = {
    "name": "StopMotion",
    "author": "Anthony Aragues, Adam Earle",
    "version": (0, 9, 9),
    "blender": (3, 2, 0),
    "location": "3D View > Toolbox > Animation tab > StopMotion",
    "description": "Stop Motion functionality for meshes and curves",
    "warning": "",
    "website": "https://blendermarket.com/products/lily-gizmos",
    "category": "Animation",
}
####|| CREDIT ||####
# stop motion logic was started from the keymesh addon https://github.com/pablodp606/keymesh-addon
# UI is from the bl_ui_widgets library here: https://github.com/mmmrqs/bl_ui_widgets
####|| NOTES ||####
# custom_properties:
# key_id = the container object id, may change later to allow copying frames across objects
# key_object = the swap NAME data currently in use
# key_object_id = the id NEEDED and set by the key

# /Applications/Blender.app/Contents/MacOS/Blender


class PanelProps(bpy.types.PropertyGroup):
    RemoVisible: bpy.props.BoolProperty(default=False)
    btnRemoText: bpy.props.StringProperty(default="Open Demo Panel")
    btnRemoTime: bpy.props.IntProperty(default=0)

# --- ### Helper functions


def is_quadview_region(context):
    """ Identifies whether screen is in QuadView mode and if yes returns the corresponding area and region
    """
    for area in context.screen.areas:
        if area.type == 'VIEW_3D':
            if len(area.spaces.active.region_quadviews) > 0:
                region = [
                    region for region in area.regions if region.type == 'WINDOW'][3]
                return (True, area, region)
    return (False, None, None)


class KEY_PT_Main(bpy.types.Panel):
    bl_label = "StopMotion"
    bl_category = "Animate"
    bl_idname = "KEY_PT_Main"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    # create the panel

    def draw(self, context):
        layout = self.layout
        row = layout.row()
        row.label(text="ctrl + shift + A")
        row = layout.row()
        row.operator("key.insert")
        row = layout.row()
        row.operator("key.add_selected")
        row = layout.row()
        row.operator("key.copy_selected")
        row = layout.row()
        row.operator("key.separate_selected")
        row = layout.row()
        row.operator("key.merge")
        row = layout.row()
        row.operator("key.remove")
        if context.space_data.type == 'VIEW_3D':
            remoteVisible = (context.window_manager.KEY_UI.RemoVisible and int(
                time.time()) - context.window_manager.KEY_UI.btnRemoTime <= 1)
            # -- remote control switch button
            if remoteVisible:
                op = self.layout.operator(
                    KEY_OT_Show_Panel.bl_idname, text="Hide Viewport Panel")
            else:
                # Make sure the button starts turned off every time
                op = self.layout.operator(
                    KEY_OT_Show_Panel.bl_idname, text="Show Viewport Panel")
        if bpy.context.window_manager.KEY_message != "":
            box = layout.box()
            row = box.row(align=True)
            row.alignment = 'EXPAND'
            row.label(icon="INFO", text=bpy.context.window_manager.KEY_message)
            row = box.row()
            row.operator(
                'wm.url_open', text="Product Page", icon="URL").url = bl_info['website']
        return None


class KEY_OT_Show_Panel(bpy.types.Operator):
    ''' Opens/Closes the remote control demo panel '''
    bl_idname = "object.set_demo_panel"
    bl_label = "Open Demo Panel"
    bl_description = "Turns the remote control demo panel on/off"

    # --- Blender interface methods
    @classmethod
    def poll(cls, context):
        return True

    def invoke(self, context, event):
        # input validation:
        return self.execute(context)

    def execute(self, context):
        if context.window_manager.KEY_UI.RemoVisible and int(time.time()) - context.window_manager.KEY_UI.btnRemoTime <= 1:
            # If it is active then set its visible status to False so that it be closed and reset the button label
            context.window_manager.KEY_UI.btnRemoText = "Show Viewport Panel"
            context.window_manager.KEY_UI.RemoVisible = False
        else:
            # If it is not active then set its visible status to True so that it be opened and reset the button label
            context.window_manager.KEY_UI.btnRemoText = "Hide Viewport Panel"
            context.window_manager.KEY_UI.RemoVisible = True
            is_quadview, area, region = is_quadview_region(context)
            if is_quadview:
                override = bpy.context.copy()
                override["area"] = area
                override["region"] = region
            # Had to put this "try/except" statement because when user clicked repeatedly too fast
            # on the operator's button it would crash the call due to a context incorrect situation
            try:
                if is_quadview:
                    context.window_manager.KEY_UI.objRemote = bpy.ops.object.dp_ot_draw_operator(
                        override, 'INVOKE_DEFAULT')
                else:
                    context.window_manager.KEY_UI.objRemote = bpy.ops.object.dp_ot_draw_operator(
                        'INVOKE_DEFAULT')
            except:
                return {'CANCELLED'}

        return {'FINISHED'}


class KEY_OT_Remove(bpy.types.Operator):
    """Create a Key for the current object, type of ket is determined by what you edit"""
    bl_idname = "key.remove"
    bl_label = "Remove Key Data"
    bl_options = {'REGISTER', 'UNDO'}

    @ classmethod
    def poll(cls, context):
        return context.selected_objects is not None

    def execute(self, context):
        for obj in context.selected_objects:
            actions.removeAllKeyData(obj)
        return {'FINISHED'}


class KEY_OT_Insert(bpy.types.Operator):
    """Create a Stop Motion Key for the current object"""
    bl_idname = "key.insert"
    bl_label = "Insert Stop Motion Key"
    bl_options = {'REGISTER', 'UNDO'}

    @ classmethod
    def poll(cls, context):
        return context.selected_objects is not None

    def execute(self, context):
        if context.active_object.data is not None and hasattr(context.active_object.data, 'animation_data') and hasattr(context.active_object.data.animation_data, 'action'):
            self.report(
                {'ERROR'}, "This object has data block animation data that will not survive data block swapping")
        actions.setSwapObject(context, context.active_object,
                              context.scene.frame_current)
        return {'FINISHED'}


class KEY_OT_AddSelected(bpy.types.Operator):
    """add selected objects as keyframe objects in active_object"""
    bl_idname = "key.add_selected"
    bl_label = "Add Selected to Active"
    bl_options = {'REGISTER', 'UNDO'}

    @ classmethod
    def poll(cls, context):
        return context.selected_objects is not None and context.active_object is not None

    def execute(self, context):
        actions.addSwapObjects(
            context, context.selected_objects, context.active_object)
        return {'FINISHED'}


class KEY_OT_CopySelected(bpy.types.Operator):
    """copy selected frames to be their own object"""
    bl_idname = "key.copy_selected"
    bl_label = "Copy Selected Frames"
    bl_options = {'REGISTER', 'UNDO'}

    @ classmethod
    def poll(cls, context):
        return context.active_object is not None

    def execute(self, context):
        actions.exposeSelectedFrameObjects(context.active_object, False)
        return {'FINISHED'}


class KEY_OT_SeparateSelected(bpy.types.Operator):
    """remove selected frames from active object to be their own objects in a collection"""
    bl_idname = "key.separate_selected"
    bl_label = "Separate Selected Frames"
    bl_options = {'REGISTER', 'UNDO'}

    @ classmethod
    def poll(cls, context):
        return context.active_object is not None

    def execute(self, context):
        actions.exposeSelectedFrameObjects(context.active_object, True)
        return {'FINISHED'}


class KEY_OT_Merge(bpy.types.Operator):
    """merge selected objects to the current frame of active object"""
    bl_idname = "key.merge"
    bl_label = "Merge Selected to Active"
    bl_options = {'REGISTER', 'UNDO'}

    @ classmethod
    def poll(cls, context):
        return context.active_object is not None and context.selected_objects is not None

    def execute(self, context):
        bpy.ops.object.join()
        actions.setSwapObject(context, context.active_object,
                              context.scene.frame_current)
        return {'FINISHED'}

####|| HANDLER ||####


@persistent
def onFrame_handler(scene: bpy.types.Scene):
    for obj in bpy.context.scene.objects:
        if obj.get("key_id"):
            bpy.app.handlers.frame_change_post.clear()
            bpy.app.handlers.frame_change_post.append(actions.onFrame)
            break


####|| CLASS MAINTENANCE ||####
arrClasses = [
    KEY_PT_Main,
    KEY_OT_Insert,
    KEY_OT_AddSelected,
    KEY_OT_CopySelected,
    KEY_OT_SeparateSelected,
    KEY_OT_Merge,
    KEY_OT_Remove,
    KEY_OT_Show_Panel,
    PanelProps
]


def cleanse_modules():
    """search for your plugin modules in blender python sys.modules and remove them"""
    for module_name in sorted(sys.modules.keys()):
        if module_name.startswith(__name__):
            del sys.modules[module_name]


addon_keymaps = []


def register():
    for i in arrClasses:
        bpy.utils.register_class(i)
    bpy.app.handlers.load_post.append(onFrame_handler)
    bpy.app.handlers.frame_change_post.clear()
    bpy.app.handlers.frame_change_post.append(actions.onFrame)
    # Add the hotkey
    wm = bpy.context.window_manager
    kc = wm.keyconfigs.addon
    if kc:
        km = wm.keyconfigs.addon.keymaps.new(
            name='3D View', space_type='VIEW_3D')
        kmi = km.keymap_items.new(
            "key.insert", type="A", value="PRESS", shift=True, ctrl=True)
        addon_keymaps.append((km, kmi))
    bpy.types.WindowManager.KEY_UI = bpy.props.PointerProperty(type=PanelProps)
    bpy.types.WindowManager.KEY_message = bpy.props.StringProperty(
        name="Info", default="")
    ui_panel.register()
    prefs.register()
    version.check_version(bl_info)


def unregister():
    cleanse_modules()
    for i in reversed(arrClasses):
        bpy.utils.unregister_class(i)
    bpy.app.handlers.load_post.remove(onFrame_handler)
    bpy.app.handlers.frame_change_post.clear()
    # Remove the hotkey
    for km, kmi in addon_keymaps:
        km.keymap_items.remove(kmi)
    addon_keymaps.clear()
    ui_panel.unregister()
    prefs.unregister()
    del bpy.types.WindowManager.KEY_UI
    del bpy.types.WindowManager.KEY_message


if __name__ == "__main__":
    register()
