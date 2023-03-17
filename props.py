import bpy


class PanelProps(bpy.types.PropertyGroup):
    RemoVisible: bpy.props.BoolProperty(default=False)
    btnRemoText: bpy.props.StringProperty(default="Open Demo Panel")
    btnRemoTime: bpy.props.IntProperty(default=0)


def register():
    bpy.utils.register_class(PanelProps)
    bpy.types.Scene.KEY_frameSpace = bpy.props.IntProperty(
        name="Frame Space", default=2, min=1, max=100)
    bpy.types.Scene.KEY_count = bpy.props.IntProperty(
        name="Keys", default=30, min=1, max=120)
    bpy.types.Scene.KEY_current = bpy.props.IntProperty(
        name="Current Frame", default=0)
    bpy.types.WindowManager.KEY_UI = bpy.props.PointerProperty(type=PanelProps)
    bpy.types.WindowManager.KEY_state = bpy.props.StringProperty(
        name="State", default="")
    bpy.types.Scene.KEY_apply_modifiers = bpy.props.BoolProperty(
        name="modifiers", default=False)


def unregister():
    bpy.utils.unregister_class(PanelProps)
    del bpy.types.Scene.KEY_apply_modifiers
    del bpy.types.Scene.KEY_frameSpace
    del bpy.types.Scene.KEY_count
    del bpy.types.WindowManager.KEY_UI
    del bpy.types.WindowManager.KEY_state
