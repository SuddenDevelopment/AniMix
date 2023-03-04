import bpy


class PanelProps(bpy.types.PropertyGroup):
    RemoVisible: bpy.props.BoolProperty(default=False)
    btnRemoText: bpy.props.StringProperty(default="Open Demo Panel")
    btnRemoTime: bpy.props.IntProperty(default=0)


def register():
    bpy.utils.register_class(PanelProps)
    bpy.types.Scene.KEY_frameSpace = bpy.props.IntProperty(
        name="Frame Space", default=2, min=1, max=100)
    bpy.types.WindowManager.KEY_UI = bpy.props.PointerProperty(type=PanelProps)
    bpy.types.WindowManager.KEY_message = bpy.props.StringProperty(
        name="Info", default="")
    bpy.types.Scene.KEY_apply_modifiers = bpy.props.BoolProperty(
        name="modifiers", default=False)
    bpy.types.Scene.KEY_count = bpy.props.IntProperty(
        name="frames", default=10, min=1, max=1200)


def unregister():
    bpy.utils.unregister_class(PanelProps)
    del bpy.types.Scene.KEY_apply_modifiers
    del bpy.types.Scene.KEY_count
    del bpy.types.Scene.KEY_frameSpace
    del bpy.types.WindowManager.KEY_UI
    del bpy.types.WindowManager.KEY_message
