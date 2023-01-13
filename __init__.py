import bpy
import time
import sys
from . import ops
from . import actions
from . import prefs
from . import ui_panel
from . import version
from bpy.app.handlers import persistent

bl_info = {
    "name": "StopMotion",
    "author": "Anthony Aragues, Adam Earle",
    "version": (1, 0, 5),
    "blender": (3, 2, 0),
    "location": "3D View > Toolbox > Animation tab > StopMotion",
    "description": "Stop Motion functionality for meshes and curves",
    "warning": "",
    "website": "https://blendermarket.com/products/stopmotion",
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
        row.label(text="StopMotion Keys")
        row = layout.column_flow(columns=3)
        row.operator("key.insert_key", text="ADD")
        row.operator("key.remove_key", text="DEL")
        row.operator("key.blank_key", text="BLA")
        row = layout.row()
        row.label(text="Duplicate")
        row = layout.column_flow(columns=3)
        row.operator("key.clone_key", text="KEY")
        row.operator("key.clone_unique_key", text="UNI")
        row.operator("key.clone_object", text="OBJ")
        row = layout.row()
        row.label(text="Frame Spacing")
        row = layout.column_flow(columns=3)
        row.operator("key.add_space", text="ADD")
        row.operator("key.remove_space", text="DEL")
        row.operator("key.set_space", text="SET")
        row = layout.row()
        row.prop(context.scene, "KEY_frameSpace")
        row = layout.row()
        row.label(text="Frame Objects")
        row = layout.column_flow(columns=3)
        row.operator("key.separate_objects", text="SEP")
        row.operator("key.combine_objects", text="COM")
        row.operator("key.merge_data", text="MER")
        row = layout.row()
        row.operator("key.add_asset")
        row = layout.row()
        row.separator()
        if context.space_data.type == 'VIEW_3D':
            remoteVisible = (context.window_manager.KEY_UI.RemoVisible and int(
                time.time()) - context.window_manager.KEY_UI.btnRemoTime <= 1)
            # -- remote control switch button
            if remoteVisible:
                op = self.layout.operator(
                    'key.viewport_panel', text="Hide Viewport Panel")
            else:
                # Make sure the button starts turned off every time
                op = self.layout.operator(
                    'key.viewport_panel', text="Show Viewport Panel")
        if bpy.context.window_manager.KEY_message != "":
            box = layout.box()
            row = box.row(align=True)
            row.alignment = 'EXPAND'
            row.label(icon="INFO", text=bpy.context.window_manager.KEY_message)
            row = box.row()
            row.operator(
                'wm.url_open', text="Product Page", icon="URL").url = bl_info['website']
        return None


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
            "key.insert_key", type="A", value="PRESS", shift=True, ctrl=True)
        addon_keymaps.append((km, kmi))
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
    ops.unregister()
    del bpy.types.Scene.KEY_frameSpace
    del bpy.types.WindowManager.KEY_UI
    del bpy.types.WindowManager.KEY_message
