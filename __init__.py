import bpy
import bpy.utils.previews
import time
import sys
from . import ops
from . import actions
from . import prefs
from . import ui_panel
from . import version
from . import icons
from bpy.app.handlers import persistent

bl_info = {
    "name": "AniMix",
    "author": "Anthony Aragues, Adam Earle",
    "version": (1, 2, 3),
    "blender": (3, 2, 0),
    "location": "3D View > Toolbox > Animation tab > aniMix",
    "description": "Stop Motion functionality for meshes and curves",
    "warning": "",
    "category": "Animation",
}
#### || CREDIT ||####
# stop motion logic was started from the keymesh addon https://github.com/pablodp606/keymesh-addon
# UI is from the bl_ui_widgets library here: https://github.com/mmmrqs/bl_ui_widgets
#### || NOTES ||####
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
    bl_label = "AniMix"
    bl_category = "Animate"
    bl_idname = "KEY_PT_Main"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    # create the panel

    def draw_header(self, context):
        layout = self.layout
        row = layout.row()
        row.label(text='AniMix', icon_value=icons.getIconId("logo_16"))

    def draw_header_preset(self, context):
        layout = self.layout
        row = layout.row()
        row.operator("wm.url_open", text="",
                     icon_value=icons.getIconId("youtube_16")).url = 'https://www.youtube.com/watch?v=Xzw8j2OyHOc&list=PLWn1OdWrqvz1bhMiWifHW1bYkMfESFTlh'
        row.operator("wm.url_open", text="",
                     icon_value=icons.getIconId("3dialogue_16")).url = 'https://discord.gg/wMmgzB5QGH'

    def draw(self, context):
        layout = self.layout
        row = layout.row()
        row.label(text="Onion Skin")
        row = layout.column_flow(columns=2)
        row.operator("key.pin_frames", text="PIN",
                     icon_value=icons.getIconId("pin_frame_16"))
        row.operator("key.unpin_frames", text="UNPIN",
                     icon_value=icons.getIconId("unpin_16"))
        row = layout.row()
        row.label(text="Clear Frame")
        row.operator("key.clear_key", text="CLEAR",
                     icon_value=icons.getIconId("clear_key_16"))
        row = layout.row()
        row.label(text="StopMotion Keys")
        row = layout.column_flow(columns=3)
        row.operator("key.insert_key", text="ADD",
                     icon_value=icons.getIconId("insert_key_16"))
        row.operator("key.remove_key", text="DEL",
                     icon_value=icons.getIconId("remove_key_16"))
        row.operator("key.blank_key", text="BLA",
                     icon_value=icons.getIconId("blank_key_16"))
        row = layout.row()
        row.label(text="Duplicate")
        row = layout.column_flow(columns=3)
        row.operator("key.clone_key", text="KEY",
                     icon_value=icons.getIconId("clone_key_16"))
        row.operator("key.clone_object", text="OBJ",
                     icon_value=icons.getIconId("clone_object_16"))
        row.operator("key.clone_object_blank_keys", text="BLA",
                     icon_value=icons.getIconId("clone_object_blank_keys_16"))
        row = layout.row()
        row.label(text="Frame Spacing")
        row = layout.column_flow(columns=3)
        row.operator("key.add_space", text="ADD",
                     icon_value=icons.getIconId("add_space_16"))
        row.operator("key.remove_space", text="DEL",
                     icon_value=icons.getIconId("remove_space"))
        row.operator("key.no_space", text="NO",
                     icon_value=icons.getIconId("no_space_16"))
        row = layout.row(align=True)
        row.prop(context.scene, "KEY_frameSpace")
        row.operator("key.set_space", text="SET",
                     icon_value=icons.getIconId("set_space_16"))

        row = layout.row()
        row.label(text="Frame Objects")
        row = layout.column_flow(columns=2)
        row.operator("key.separate_objects", text="SEP",
                     icon_value=icons.getIconId("separate_objects_16"))
        row.operator("key.combine_objects", text="COM",
                     icon_value=icons.getIconId("combine_objects_16"))
        row = layout.row()
        row.label(text="Asset Library")
        row.operator("key.add_asset", text="SET",
                     icon_value=icons.getIconId("add_asset_16"))
        row = layout.row()
        row.separator()
        if context.space_data.type == 'VIEW_3D':
            remoteVisible = (context.window_manager.KEY_UI.RemoVisible and int(
                time.time()) - context.window_manager.KEY_UI.btnRemoTime <= 1)
            # -- remote control switch button
            if remoteVisible:
                op = self.layout.operator(
                    'key.viewport_panel', text="Hide Viewport Panel", icon_value=icons.getIconId("show_panel_16"))
            else:
                # Make sure the button starts turned off every time
                op = self.layout.operator(
                    'key.viewport_panel', text="Show Viewport Panel", icon_value=icons.getIconId("show_panel_16"))
        version.draw_version_box(self, context)
        return None


#### || HANDLER ||####


@persistent
def onFrame_handler(scene: bpy.types.Scene):
    for obj in bpy.context.scene.objects:
        if obj.get("key_id"):
            bpy.app.handlers.frame_change_post.clear()
            bpy.app.handlers.frame_change_pre.clear()
            bpy.app.handlers.frame_change_post.append(actions.onFrame)
            bpy.app.handlers.frame_change_pre.append(actions.onFramePre)
            break


class ModeTracker:
    def __init__(self):
        self.previous_mode = None
        self.frame = None


def on_depsgraph_update(scene, mode_tracker):
    current_mode = bpy.context.object.mode
    if current_mode != mode_tracker.previous_mode:
        if mode_tracker.previous_mode == 'EDIT' and bpy.context.active_object and scene.frame_current == mode_tracker.frame:
            obj = bpy.context.active_object
            if obj.get("key_id"):
                strFrame = obj.get("key_object")
                objFrame = actions.getObject(strFrame)
                objTmp = actions.getTmp(obj)
                actions.setDataBlock(objFrame, objTmp)
        mode_tracker.previous_mode = current_mode
        mode_tracker.frame = scene.frame_current


#### || CLASS MAINTENANCE ||####
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
    icons.initIcons()
    mode_tracker = ModeTracker()
    bpy.app.handlers.depsgraph_update_pre.append(
        lambda scene: on_depsgraph_update(scene, mode_tracker))
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
    version.register(bl_info)


def unregister():
    cleanse_modules()
    for i in reversed(arrClasses):
        bpy.utils.unregister_class(i)
    bpy.app.handlers.depsgraph_update_pre.clear()
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
    icons.delIcons()
