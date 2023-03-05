import bpy
from bpy.types import AddonPreferences, Operator
from bpy.props import StringProperty, IntProperty, BoolProperty, EnumProperty, FloatProperty, FloatVectorProperty

from .bl_ui_widgets.bl_ui_draw_op import get_3d_area_and_region


class BL_UI_Widget_Preferences(AddonPreferences):
    bl_idname = __package__

    KEY_MULTI_MODS: BoolProperty(
        name="Enable multi key modifiers",
        description="Apply the modifier stack every frame of multi key. This can be unstable or unpredictable depending on the modifier stack used.",
        default=False
    )
    KEY_MULTI_LIMIT: IntProperty(
        name="Limit in seconds per frame of multi key",
        description="If a frame take longer than this setting in seconds, stop.",
        default=30, min=1
    )

    KEY_UNSELECT: BoolProperty(
        name="Select key on creation",
        description="When a stop motion key is created select at afterwards.",
        default=False
    )

    RC_UI_BIND: BoolProperty(
        name="General scaling for 'Remote Control' panel",
        description="If (ON): remote panel size changes per Blender interface's resolution scale.\nIf (OFF): remote panel size can only change per its own addon scaling factor",
        default=True
    )

    RC_SCALE: FloatProperty(
        name="",
        description="Scaling to be applied on the 'Remote Control' panel over (in addition to) the interface's resolution scale",
        default=1.0,
        max=2.00,
        min=0.50,
        soft_max=1.50,
        soft_min=0.50,
        step=1,
        precision=2,
        unit='NONE'
    )

    RC_SLIDE: BoolProperty(
        name="Keep Remote Control panel pinned when resizing viewport",
        description="If (ON): remote panel slides together with viewport's bottom border.\nIf (OFF): remote panel stays in place regardless of viewport resizing",
        default=False
    )

    RC_POSITION: BoolProperty(
        name="Remote Control panel position per scene",
        description="If (ON): remote panel initial position is the same as in the last opened scene.\nIf (OFF): remote panel remembers its position per each scene",
        default=False
    )

    RC_POS_X: IntProperty(
        name="",
        description="Remote Control panel position 'X' from latest opened scene",
        default=-10000
    )

    RC_POS_Y: IntProperty(
        name="",
        description="Remote Control panel position 'Y' from latest opened scene",
        default=-10000
    )

    RC_PAN_W: IntProperty(
        name="",
        description="Panel width saved on 'drag_panel_op.py'"
    )

    RC_PAN_H: IntProperty(
        name="",
        description="Panel height saved on 'drag_panel_op.py'"
    )

    def ui_scale(self, value):
        if bpy.context.preferences.addons[__package__].preferences.RC_UI_BIND:
            # From Preferences/Interface/"Display"
            return (value * bpy.context.preferences.view.ui_scale)
        else:
            return (value)

    def over_scale(self, value):
        over_scale = bpy.context.preferences.addons[__package__].preferences.RC_SCALE
        return (self.ui_scale(value) * over_scale)

    def draw(self, context):
        layout = self.layout

        split = layout.split(factor=0.45, align=True)
        split.label(text="Apply Modifier Stack on Multi Key:", icon='ERROR')
        splat = split.split(factor=0.4, align=True)
        splat.prop(self, 'KEY_MULTI_MODS', text="may be unstable")

        split = layout.split(factor=0.45, align=True)
        split.label(
            text="Limit per multi key frame before stopping:", icon='ERROR')
        splat = split.split(factor=0.4, align=True)
        splat.prop(self, 'KEY_MULTI_LIMIT', text="seconds")

        split = layout.split(factor=0.45, align=True)
        split.label(text="Swap key selection:", icon='DECORATE')
        splat = split.split(factor=0.4, align=True)
        splat.prop(self, 'KEY_UNSELECT', text="Unselect on creation")

        split = layout.split(factor=0.45, align=True)
        split.label(text="Update Keyframe Theme Colors:", icon='DECORATE')
        splat = split.split(factor=0.4, align=True)
        splat.operator(KEY_OT_SetKeyColors.bl_idname)

        split = layout.split(factor=0.45, align=True)
        split.label(text="General scaling for panel:", icon='DECORATE')
        splat = split.split(factor=0.8, align=True)
        splat.prop(self, 'RC_UI_BIND', text=" Bound to Blender's UI")

        split = layout.split(factor=0.45, align=True)
        split.label(text="User defined addon scaling:", icon='DECORATE')
        splat = split.split(factor=0.4, align=True)
        splat.prop(self, 'RC_SCALE', text="")

        split = layout.split(factor=0.45, align=True)
        split.label(text="Panel sliding option:", icon='DECORATE')
        splat = split.split(factor=0.8, align=True)
        splat.prop(self, 'RC_SLIDE', text=" Move along viewport border")

        split = layout.split(factor=0.45, align=True)
        split.label(text="Opening screen position:", icon='DECORATE')
        splat = split.split(factor=0.8, align=True)
        splat.prop(self, 'RC_POSITION',
                   text=" Same as in the last opened scene")

        if bpy.context.scene.get("bl_ui_panel_saved_data") is None:
            coords = "x: 0    " + \
                     "y: 0    "
        else:
            # Panel height
            panH = bpy.context.preferences.addons[__package__].preferences.RC_PAN_H
            pos_x = int(round(bpy.context.scene.get(
                "bl_ui_panel_saved_data")["panX"]))
            pos_y = int(round(bpy.context.scene.get(
                "bl_ui_panel_saved_data")["panY"]))
            # Note: Because of the scaling logic it was necessary to do this weird math correction below
            coords = "x: " + str(pos_x) + "    " + \
                     "y: " + \
                str(pos_y + int(panH * (self.over_scale(1) - 1))) + "    "

        split = layout.split(factor=0.45, align=True)
        split.label(text="Current screen position:", icon='DECORATE')
        splat = split.split(factor=0.4, align=True)
        splat.label(text=coords)
        splot = splat.split(factor=0.455, align=True)
        splot.operator(Reset_Coords.bl_idname)


class KEY_OT_SetKeyColors(bpy.types.Operator):
    """update the keyframe theme colors"""
    bl_idname = "key.set_key_colors"
    bl_label = "Set Key Colors"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
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
        return {'FINISHED'}


class Reset_Coords(bpy.types.Operator):
    bl_idname = "object.reset_coords"
    bl_label = "Reset Pos"
    bl_description = "Resets the 'Remote Control' panel screen position for this current session only.\n" \
                     "Use this button to recover the panel if it has got stuck out of the viewport area.\n" \
                     "You will need to reopen the panel for the new screen position to take effect"

    @classmethod
    def poll(cls, context):
        return (not bpy.context.scene.get("bl_ui_panel_saved_data") is None)

    def invoke(self, context, event):
        return self.execute(context)

    def execute(self, context):
        # Panel width
        panW = bpy.context.preferences.addons[__package__].preferences.RC_PAN_W
        # Panel height
        panH = bpy.context.preferences.addons[__package__].preferences.RC_PAN_H
        # Panel X coordinate, for top-left corner (some default, case it fails below)
        panX = 100
        panY = panH + 40 - 1   # Panel Y coordinate, for top-left corner

        region = get_3d_area_and_region(prefs=True)[1]
        if region:
            if bpy.context.preferences.addons[__package__].preferences.RC_UI_BIND:
                # From Preferences/Interface/"Display"
                ui_scale = bpy.context.preferences.view.ui_scale
            else:
                ui_scale = 1
            over_scale = bpy.context.preferences.addons[__package__].preferences.RC_SCALE
            # Need this just because I want the panel to be centered
            panX = int(
                (region.width - (panW * ui_scale * over_scale)) / 2.0) + 1
        try:
            bpy.context.preferences.addons[__package__].preferences.RC_POS_X = panX
            bpy.context.preferences.addons[__package__].preferences.RC_POS_Y = panY
            bpy.context.scene.get("bl_ui_panel_saved_data")["panX"] = panX
            bpy.context.scene.get("bl_ui_panel_saved_data")["panY"] = panY
            # These two next statements cause the remote panel to be closed by the BL_UI_OT_draw_operator modal class
            # and changes the operator's label on the N-Panel UI accordingly to indicate panel can be opened again.
            bpy.context.scene.var.RemoVisible = False
            bpy.context.scene.var.btnRemoText = "Open Remote Control"
        except Exception as e:
            pass
        return {'FINISHED'}


# Registration
def register():
    bpy.utils.register_class(Reset_Coords)
    bpy.utils.register_class(KEY_OT_SetKeyColors)
    bpy.utils.register_class(BL_UI_Widget_Preferences)


def unregister():
    bpy.utils.unregister_class(BL_UI_Widget_Preferences)
    bpy.utils.unregister_class(KEY_OT_SetKeyColors)
    bpy.utils.unregister_class(Reset_Coords)


if __name__ == '__main__':
    register()
