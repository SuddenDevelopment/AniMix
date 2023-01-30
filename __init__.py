import bpy
import bpy.utils.previews
import time
import sys
import os
from . import ops
from . import actions
from . import prefs
from . import ui_panel
from . import version
from bpy.app.handlers import persistent

bl_info = {
    "name": "StopMotion",
    "author": "Anthony Aragues, Adam Earle",
    "version": (1, 1, 3),
    "blender": (3, 2, 0),
    "location": "3D View > Toolbox > Animation tab > StopMotion",
    "description": "Stop Motion functionality for meshes and curves",
    "warning": "",
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


# ICONS
icons_collection = None
this_directory = os.path.dirname(__file__)


def load_icons():
    global icons_collection
    icons_collection = bpy.utils.previews.new()
    arrIcons = [
        'pin_frame',
        'clear_key',
        'insert_key',
        'remove_key',
        'blank_key',
        'clone_key',
        'clone_object',
        'clone_object_blank_keys',
        'add_space',
        'remove_space',
        'no_space',
        'set_space',
        'separate_objects',
        'combine_objects',
        'show_panel',
        'add_asset'
    ]
    for strIcon in arrIcons:
        strFileName = f'{this_directory}/icons_16/{strIcon}.png'
        try:
            icons_collection.load(strIcon, strFileName, "IMAGE")
        except:
            print("couldn't load:", strFileName)
            pass


class KEY_PT_Main(bpy.types.Panel):
    bl_label = "StopMotion"
    bl_category = "Animate"
    bl_idname = "KEY_PT_Main"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    # create the panel

    def draw(self, context):
        global icons_collection
        layout = self.layout
        row = layout.row()
        row.label(text="Onion Skin")
        row.operator("key.pin_frames", text="PIN",
                     icon_value=icons_collection["pin_frame"].icon_id)
        row = layout.row()
        row.label(text="StopMotion Keys")
        row = layout.column_flow(columns=3)
        row.operator("key.insert_key", text="ADD",
                     icon_value=icons_collection["insert_key"].icon_id)
        row.operator("key.remove_key", text="DEL",
                     icon_value=icons_collection["remove_key"].icon_id)
        row.operator("key.blank_key", text="BLA",
                     icon_value=icons_collection["blank_key"].icon_id)
        row = layout.row()
        row.label(text="Duplicate")
        row = layout.column_flow(columns=3)
        row.operator("key.clone_key", text="KEY",
                     icon_value=icons_collection["clone_key"].icon_id)
        row.operator("key.clone_object", text="OBJ",
                     icon_value=icons_collection["clone_object"].icon_id)
        row.operator("key.clone_object_blank_keys", text="BLA",
                     icon_value=icons_collection["clone_object_blank_keys"].icon_id)
        row = layout.row()
        row.label(text="Frame Spacing")
        row = layout.column_flow(columns=3)
        row.operator("key.add_space", text="ADD",
                     icon_value=icons_collection["add_space"].icon_id)
        row.operator("key.remove_space", text="DEL",
                     icon_value=icons_collection["remove_space"].icon_id)
        row.operator("key.no_space", text="NO",
                     icon_value=icons_collection["no_space"].icon_id)
        row = layout.row(align=True)
        row.prop(context.scene, "KEY_frameSpace")
        row.operator("key.set_space", text="SET",
                     icon_value=icons_collection["set_space"].icon_id)

        row = layout.row()
        row.label(text="Frame Objects")
        row = layout.column_flow(columns=2)
        row.operator("key.separate_objects", text="SEP",
                     icon_value=icons_collection["separate_objects"].icon_id)
        row.operator("key.combine_objects", text="COM",
                     icon_value=icons_collection["combine_objects"].icon_id)
        row = layout.row()
        row.label(text="Asset Library")
        row.operator("key.add_asset", text="SET",
                     icon_value=icons_collection["add_asset"].icon_id)
        row = layout.row()
        row.separator()
        if context.space_data.type == 'VIEW_3D':
            remoteVisible = (context.window_manager.KEY_UI.RemoVisible and int(
                time.time()) - context.window_manager.KEY_UI.btnRemoTime <= 1)
            # -- remote control switch button
            if remoteVisible:
                op = self.layout.operator(
                    'key.viewport_panel', text="Hide Viewport Panel", icon_value=icons_collection["show_panel"].icon_id)
            else:
                # Make sure the button starts turned off every time
                op = self.layout.operator(
                    'key.viewport_panel', text="Show Viewport Panel", icon_value=icons_collection["show_panel"].icon_id)
        version.draw_version_box(self, context)
        return None


####|| HANDLER ||####


@persistent
def onFrame_handler(scene: bpy.types.Scene):
    for obj in bpy.context.scene.objects:
        if obj.get("key_id"):
            bpy.app.handlers.frame_change_post.clear()
            bpy.app.handlers.frame_change_pre.clear()
            bpy.app.handlers.frame_change_post.append(actions.onFrame)
            bpy.app.handlers.frame_change_pre.append(actions.onFramePre)
            break


####|| CLASS MAINTENANCE ||####
arrClasses = [
    KEY_PT_Main,
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
    load_icons()
    bpy.app.handlers.load_post.append(onFrame_handler)
    bpy.app.handlers.frame_change_post.clear()
    bpy.app.handlers.frame_change_post.append(actions.onFrame)
    bpy.app.handlers.frame_change_pre.clear()
    bpy.app.handlers.frame_change_pre.append(actions.onFramePre)
    # Add the hotkey
    # wm = bpy.context.window_manager
    # kc = wm.keyconfigs.addon
    # if kc:
    # km = wm.keyconfigs.addon.keymaps.new(name='3D View', space_type='VIEW_3D')
    # kmi = km.keymap_items.new("key.insert_key", type="A", value="PRESS", shift=True, ctrl=True)
    # addon_keymaps.append((km, kmi))
    bpy.types.Scene.KEY_frameSpace = bpy.props.IntProperty(
        name="Frame Space", default=2, min=1, max=100)
    bpy.types.WindowManager.KEY_UI = bpy.props.PointerProperty(type=PanelProps)
    bpy.types.WindowManager.KEY_message = bpy.props.StringProperty(
        name="Info", default="")
    ops.register()
    ui_panel.register()
    prefs.register()
    bpy.context.preferences.themes['Default'].dopesheet_editor.keyframe = (
        1, 0.75, 0.20)
    bpy.context.preferences.themes['Default'].dopesheet_editor.keyframe_selected = (
        1, 0, 0)
    bpy.context.preferences.themes['Default'].dopesheet_editor.keyframe_extreme = (
        0.95, 0.5, 0.5)
    bpy.context.preferences.themes['Default'].dopesheet_editor.keyframe_extreme_selected = (
        1, 0, 0)
    bpy.context.preferences.themes['Default'].dopesheet_editor.keyframe_breakdown = (
        0.33, 0.75, 0.93)
    bpy.context.preferences.themes['Default'].dopesheet_editor.keyframe_breakdown_selected = (
        1, 0, 0)
    bpy.context.preferences.themes['Default'].dopesheet_editor.keyframe_jitter = (
        0.38, 0.75, 0.26)
    bpy.context.preferences.themes['Default'].dopesheet_editor.keyframe_jitter_selected = (
        1, 0, 0)
    bpy.context.preferences.themes['Default'].dopesheet_editor.keyframe_movehold = (
        0.64, 0, 1)
    bpy.context.preferences.themes['Default'].dopesheet_editor.keyframe_movehold_selected = (
        1, 0, 0)
    version.register(bl_info)


def unregister():
    cleanse_modules()
    for i in reversed(arrClasses):
        bpy.utils.unregister_class(i)
    bpy.app.handlers.load_post.remove(onFrame_handler)
    bpy.app.handlers.frame_change_post.clear()
    bpy.app.handlers.frame_change_pre.clear()
    # Remove the hotkey
    for km, kmi in addon_keymaps:
        km.keymap_items.remove(kmi)
    addon_keymaps.clear()
    ui_panel.unregister()
    prefs.unregister()
    ops.unregister()
    del bpy.types.Scene.KEY_frameSpace
    del bpy.types.WindowManager.KEY_UI
    del bpy.types.WindowManager.KEY_message
    global icons_collection
    icons_collection.clear()
    bpy.utils.previews.remove(icons_collection)
