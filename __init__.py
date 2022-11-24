import bpy
import sys
from . import actions
from bpy.app.handlers import persistent

bl_info = {
    "name": "StopMotion",
    "author": "Anthony Aragues, Adam Earle",
    "version": (0, 9, 7),
    "blender": (3, 2, 0),
    "location": "3D View > Toolbox > Animation tab > StopMotion",
    "description": "Stop Motion functionality for meshes and curves",
    "warning": "",
    "category": "Animation",
}
####|| CREDIT ||####
# stop motion logic was started from the keymesh addon https://github.com/pablodp606/keymesh-addon

####|| NOTES ||####
# custom_properties:
# key_id = the container object id, may change later to allow copying frames across objects
# key_object = the swap NAME data currently in use
# key_object_id = the id NEEDED and set by the key

# /Applications/Blender.app/Contents/MacOS/Blender


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
        row.operator("key.remove")


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
        if hasattr(context.active_object.data, 'animation_data') and hasattr(context.active_object.data.animation_data, 'action'):
            self.report(
                {'ERROR'}, "This object has data block animation data that will not survive data block swapping")
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
    KEY_OT_Remove
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


def unregister():
    cleanse_modules()
    for i in arrClasses:
        bpy.utils.unregister_class(i)
    bpy.app.handlers.load_post.remove(onFrame_handler)
    bpy.app.handlers.frame_change_post.clear()
    # Remove the hotkey
    for km, kmi in addon_keymaps:
        km.keymap_items.remove(kmi)
    addon_keymaps.clear()


if __name__ == "__main__":
    register()
