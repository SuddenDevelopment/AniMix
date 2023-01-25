import bpy

from bpy.types import AddonPreferences, Operator
from bpy.props import StringProperty, IntProperty, BoolProperty, EnumProperty, FloatProperty, FloatVectorProperty

from .bl_ui_widgets.bl_ui_draw_op import get_3d_area_and_region

objDefault = {
    "version": "0",
    "ver_message": "Update Available",
    "bm_url": "https://blendermarket.com/products/stopmotion",
    "message": "",
    "btn_name": "",
    "url": "",
    "hide_message": False,
    "hide_version": False
}


class BL_UI_Widget_Preferences(AddonPreferences):
    bl_idname = __package__

    json_message: bpy.props.StringProperty(
        name="",
        default=json.dumps(objDefault)
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
    bpy.utils.register_class(BL_UI_Widget_Preferences)


def unregister():
    bpy.utils.unregister_class(BL_UI_Widget_Preferences)
    bpy.utils.unregister_class(Reset_Coords)


if __name__ == '__main__':
    register()
