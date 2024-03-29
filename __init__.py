import bpy
import bpy.utils.previews
import time
import sys
from . import ops
from . import props
from . import actions
from . import prefs
from . import ui_panel
from . import version
from . import icons
from . import animall
from bpy.app.handlers import persistent

bl_info = {
    "name": "AniMix",
    "author": "Anthony Aragues, Adam Earle",
    "version": (1, 3, 3),
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


class KEY_PT_Main(bpy.types.Panel):
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = "Animate"
    bl_label = "AniMix"
    bl_idname = "KEY_PT_Main"

    # create the panel

    def draw_header(self, context):
        layout = self.layout
        row = layout.row()
        row.label(text='', icon_value=icons.getIconId("logo_16"))

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
        split = row.split(factor=0.25, align=True)
        colLabel = split.column(align=True)
        colLabel.alignment = "RIGHT"
        colButtons = split.column_flow(columns=4, align=True)
        colLabel.label(text="Onion Skin")
        colButtons.operator("key.pin_frames", text="",
                            icon_value=icons.getIconId("pin_frame_16"))
        colButtons.operator("key.unpin_frames", text="",
                            icon_value=icons.getIconId("unpin_16"))

        row = layout.row()
        split = row.split(factor=0.25, align=True)
        colLabel = split.column(align=True)
        colLabel.alignment = "RIGHT"
        colButtons = split.column_flow(columns=4, align=True)
        colLabel.label(text="Swap Keys")
        colButtons.operator("key.clear_key", text="",
                            icon_value=icons.getIconId("clear_key_16"))
        colButtons.operator("key.insert_key", text="",
                            icon_value=icons.getIconId("insert_key_16"))
        colButtons.operator("key.remove_key", text="",
                            icon_value=icons.getIconId("remove_key_16"))
        colButtons.operator("key.blank_key", text="",
                            icon_value=icons.getIconId("blank_key_16"))

        row = layout.row()
        split = row.split(factor=0.25, align=True)
        colLabel = split.column(align=True)
        colLabel.alignment = "RIGHT"
        colButtons = split.column_flow(columns=4, align=True)
        if hasattr(bpy.types, "ANIM_OT_insert_keyframe_animall"):
            colLabel.label(text="Anim All")
            colButtons.operator("anim.insert_keyframe_animall", text="",
                                icon_value=icons.getIconId("insert_animall_16"))

        row = layout.row()
        split = row.split(factor=0.25, align=True)
        colLabel = split.column(align=True)
        colLabel.alignment = "RIGHT"
        colLabel.label(text="Duplicate")
        colButtons = split.column_flow(columns=4, align=True)
        colButtons.operator("key.clone_key", text="",
                            icon_value=icons.getIconId("clone_key_16"))
        colButtons.operator("key.clone_object", text="",
                            icon_value=icons.getIconId("clone_object_16"))
        colButtons.operator("key.clone_object_blank_keys", text="",
                            icon_value=icons.getIconId("clone_object_blank_keys_16"))

        row = layout.row()
        split = row.split(factor=0.25, align=True)
        colLabel = split.column(align=True)
        colLabel.alignment = "RIGHT"
        colButtons = split.column_flow(columns=4, align=True)
        colLabel.label(text="Frame Objects")
        colButtons.operator("key.separate_objects", text="",
                            icon_value=icons.getIconId("separate_objects_16"))
        colButtons.operator("key.combine_objects", text="",
                            icon_value=icons.getIconId("combine_objects_16"))

        row = layout.row()
        split = row.split(factor=0.25, align=True)
        colLabel = split.column(align=True)
        colLabel.alignment = "RIGHT"
        colButtons = split.column_flow(columns=4, align=True)
        colLabel.label(text="Asset Library")
        colButtons.operator("key.add_asset", text="",
                            icon_value=icons.getIconId("add_asset_16"))

        row = layout.row()
        split = row.split(factor=0.25, align=True)
        colLabel = split.column(align=True)
        colLabel.alignment = "RIGHT"
        colButtons = split.column_flow(columns=4, align=True)
        colLabel.label(text="Space Keys")
        colButtons.operator("key.add_space", text="",
                            icon_value=icons.getIconId("add_space_16"))
        colButtons.operator("key.remove_space", text="",
                            icon_value=icons.getIconId("remove_space"))
        colButtons.operator("key.no_space", text="",
                            icon_value=icons.getIconId("no_space_16"))
        row = layout.row()
        split = row.split(factor=0.25, align=True)
        colLabel = split.column(align=True)
        colLabel.label(text="")
        split = split.split()
        colButtons = split.column()
        colButtons.prop(context.scene, "KEY_frameSpace")
        colButtons = split.column_flow(columns=2)
        colButtons.operator("key.set_space", text="",
                            icon_value=icons.getIconId("set_space_16"))

        row = layout.row()
        box = row.box()

        if context.preferences.addons[__package__].preferences.KEY_MULTI_MODS == True:
            row = box.row()
            row.label(text="apply mods", icon='ERROR')
            row.prop(context.scene, "KEY_apply_modifiers")
        row = box.row()
        row.prop(context.scene, "KEY_count")
        row.operator("key.iterate", text="MULTI KEY")
        if context.scene.KEY_current > 0:
            row = box.row()
            row.label(
                text=f'frame progress: {context.scene.KEY_current}/{context.scene.KEY_frameSpace}')

        row = layout.row()
        row.separator()
        if context.space_data.type == 'VIEW_3D':
            remoteVisible = (context.window_manager.KEY_UI.RemoVisible and int(
                time.time()) - context.window_manager.KEY_UI.btnRemoTime <= 1)
            # -- remote control switch button
            if remoteVisible:
                op = self.layout.operator(
                    'key.viewport_panel', text="Pro User Panel", icon_value=icons.getIconId("show_panel_16"))
            else:
                # Make sure the button starts turned off every time
                op = self.layout.operator(
                    'key.viewport_panel', text="Pro User Panel", icon_value=icons.getIconId("show_panel_16"))
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
    if bpy.context.object:
        current_mode = bpy.context.object.mode
        if current_mode != mode_tracker.previous_mode:
            if bpy.context.window_manager.KEY_state != 'ANIMALL':
                if mode_tracker.previous_mode == 'EDIT' and bpy.context.active_object and scene.frame_current == mode_tracker.frame:
                    print(current_mode, mode_tracker.previous_mode,
                          'updating data block')
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
    KEY_PT_Main
]


def cleanse_modules():
    """search for your plugin modules in blender python sys.modules and remove them"""
    for module_name in sorted(sys.modules.keys()):
        if module_name.startswith(__name__):
            del sys.modules[module_name]


addon_keymaps = []


def register():
    animall.register()
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
    props.register()
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
    props.unregister()
    icons.delIcons()
    animall.unregister()
