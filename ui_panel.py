
# --- ### Header
from .bl_ui_widgets.bl_ui_drag_panel import BL_UI_Drag_Panel
from .bl_ui_widgets.bl_ui_draw_op import BL_UI_OT_draw_operator
from .bl_ui_widgets.bl_ui_tooltip import BL_UI_Tooltip
from .bl_ui_widgets.bl_ui_button import BL_UI_Button
from .bl_ui_widgets.bl_ui_label import BL_UI_Label
from .bl_ui_widgets.bl_ui_slider import BL_UI_Slider
import os
import time
import bpy

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


class KEY_OT_draw_operator(BL_UI_OT_draw_operator):  # in: bl_ui_draw_op.py ##
    bl_idname = "object.dp_ot_draw_operator"
    bl_label = "bl ui widgets custom operator"
    bl_description = "Operator for bl ui widgets"
    bl_options = {'REGISTER'}

    # --- methods
    @classmethod
    def poll(cls, context):
        # Show this panel in View_3D only
        if context.space_data.type != 'VIEW_3D':
            return False
        else:
            return True

    def __init__(self):

        super().__init__()

        if __package__.find(".") != -1:
            package = __package__[0:__package__.find(".")]
        else:
            package = __package__

        # Note: Leave it empty, e.g. self.valid_modes = {}, for no restrictions to be applied.
        self.valid_modes = {}

        # This is for displaying the widgets tooltips. Only need one instance!
        self.tooltip = BL_UI_Tooltip()
# ==========
        objButtonDefaults = {
            "bg_color": (0.5, 0.5, 0.5, 0.3),
            "text": "",
            "outline_color": (0, 0, 0, 0),
            "roundness": 0.4,
            "corner_radius": 10,
            "has_shadow": True,
            "rounded_corners": (0, 0, 0, 0),
            "iconFile": 'add_asset',
            "imageSize": (32, 32),
            "imagePosition": (2, 2)
        }
        # group buttons and give overrides
        self.arrButtonGroups = [
            {
                "name": 'Onion',
                "buttons": {"pin_frames":
                            {
                                "description":
                                "Pin Frame:  Sets the selected object/s to be used as a reference.\n" +
                                "\n"
                                "Click:  Pins the current selection\n" +
                                "Ctrl + Click:  Removes all pin frames"
                            }
                            }
            }, {
                "name": 'StopMotion Keys',
                "buttons": {"clear_key":
                            {
                                "description": "Clear Keyframe:  Clears the id data from the current StopMotion object. Keyframe is not deleted.\n" +
                                "\n"
                                "Click:  Clears the geometry from the current keyframe.\n" +
                                "Ctrl + Click:  Clears the selected geometry from the current keyframe.\n" +
                                "Alt + Click:  Clears the non selected geometry from the current keyframe."
                            }
                            }
            }, {
                "name": '',
                "buttons": {"insert_key":
                            {
                                "description": "Add Keyframe:  Adds/ inserts a keyframe with unique StopMotion Object id\n" +
                                "\n"
                                "Click:  Add/ inserts a keyframe to the Right of the playhead.\n" +
                                "Ctrl + Click:  Add/ insertst a keyframe to the Left of the playhead."},
                            "remove_key":
                            {
                                "description": "Delete Keyframe:  Deletes the current keyframe & pulls keyframes into the deleted keyframe position.\n" +
                                "\n"
                                "Click:  Deletes a keyframe to the Right of the playhead.\n" +
                                "Ctrl + Click:  Deletes a keyframe to the Left of the playhead."},
                            "blank_key":
                            {
                                "description": "Insert Blank Keyframe:  Inserts a single blank keyframe to the right or the left of the playhead.\n" +
                                "\n"
                                "Click:  Inserts a blank keyframe to the Right of the playhead.\n" +
                                "Ctrl + Click:  Inserts a blank keyframe to the Left of the playhead."},
                            },
            }, {
                "name": 'Duplicate',
                "buttons":
                    {
                        "clone_key": {"description": "Duplicate Keyframe:  Duplicates the current keyframe to the right of the current active keyframe."},
                        "clone_object": {"description": "Duplicate Object With Keys:  Duplicates the object/s and the current keyframes with a unique id."},
                        "clone_object_blank_keys": {"description":  "Duplicate Object With Blank Keys:  Duplicates the object/s with blank keyframes."},
                    },
            },  {
                "name": 'Frame Spacing',
                "setPosition": True,
                "buttons": {
                    "add_space": {
                        "description": "Add Frame Space:  Inserts a single space to either the Right or Left side of the current keyframes.\n" +
                        "\n"
                        "Click:  Inserts a single space to the Right of the current keyframes.\n" +
                        "Ctrl + Click:  Inserts a single space to the Left of the current keyframes.",
                        "imageSize": (32, 16),
                        "imagePosition": (2, 0),
                        "buttonSize": (38, 17)
                    },
                    "remove_space": {
                        "description": "Subtract Frame Space :  Removes a single space from either Right or Left side of the current keyframes. Accumulative behavior till there are no more spaces between keyframes. Does not delete keys.\n" +
                        "\n"
                        "Click:  Removes a single space to the Right of the current keyframes.\n" +
                        "Ctrl + Click:  Removes a single space to the Left of the current keyframes.",
                        "imageSize": (32, 16),
                        "imagePosition": (2, 0),
                        "buttonSize": (38, 17)
                    },
                    "no_space": {
                        "description": "No Frame Space:  Removes all space between selected keyframes",
                        "imageSize": (32, 16),
                        "imagePosition": (2, 0),
                        "buttonSize": (38, 17)
                    }}
            }, {
                "name": 'Frame Objects',
                "buttons":
                    {

                        "separate_objects": {"description": "Separate Selection:  Separates the current objects transfomration to a sperate object.\n" +
                                             "Click:  Creates a Copy from the Object/ Edit mode of the selection.\n"

                                             },
                        "combine_objects": {"description": "Combine To Active Object:  Combines the selected object with the active objects keyframes.\n"
                                            "\n"
                                            "Click:  Combines the selection with the active objects keyframe.\n" +
                                            "Ctrl + Click:  Creates new keyframe/s from selected objects to the active objects keyframes.",
                                            }
                    }
            }, {
                "name": 'Assets',
                "buttons":
                    {
                        "add_asset": {"description": "Asset Library:  Creates assets in Object mode, selections in Edit mode, and from active Keyframes."},
                    }
            }
        ]
        # layout settings
        intGroupSpacing = 3
        intButtonSpacing = 3
        intButtonSize = 38

        # flywheel values
        intPositionX = 0
        intPositionY = 20
        for objButtonGroup in self.arrButtonGroups:
            intPositionX += intGroupSpacing
            intButtonCount = len(objButtonGroup['buttons'])
            # create the group label
            objLabel = BL_UI_Label(
                intPositionX+intButtonSpacing, 15,
                intButtonCount*(intButtonSpacing+intButtonSize), 18)
            objLabel.style = 'TITLE'
            objLabel.size = 14
            objLabel.text = objButtonGroup["name"]
            strGroupID = objButtonGroup["name"].replace(" ", "_")
            setattr(self, strGroupID+'Position', (intPositionX, intPositionY))
            setattr(self, strGroupID, objLabel)
            for i, strButton in enumerate(objButtonGroup['buttons']):
                # combine the defaults and overrides into one object to apply
                objButtonSettings = objButtonDefaults.copy()
                if intButtonCount > 1 and i == 0:
                    # set beginning group style
                    objButtonSettings['rounded_corners'] = (1, 1, 0, 0)
                elif intButtonCount > 1 and i == intButtonCount-1:
                    # set ending group style
                    objButtonSettings['rounded_corners'] = (0, 0, 1, 1)
                elif intButtonCount == 1:
                    # set ending group style
                    objButtonSettings['rounded_corners'] = (1, 1, 1, 1)
                for strProp in objButtonGroup['buttons'][strButton]:
                    objButtonSettings[strProp] = objButtonGroup['buttons'][strButton][strProp]
                # get the position and size
                intPositionX += intButtonSpacing
                # set up the button with defaults
                if 'buttonSize' not in objButtonSettings:
                    objButtonSettings['buttonSize'] = (
                        intButtonSize, intButtonSize)
                objNewBtn = BL_UI_Button(
                    intPositionX, intPositionY, objButtonSettings['buttonSize'][0], objButtonSettings['buttonSize'][1])
                intPositionX += intButtonSize
                for strProp in objButtonSettings:
                    if strProp == 'iconFile':
                        directory = os.path.dirname(os.path.realpath(__file__))
                        objNewBtn.set_image(
                            f'{directory}\\icons\\{strButton}.png')
                    elif strProp == 'imageSize':
                        objNewBtn.set_image_size(objButtonSettings[strProp])
                    elif strProp == 'imagePosition':
                        objNewBtn.set_image_position(
                            objButtonSettings[strProp])
                    else:
                        setattr(objNewBtn, strProp, objButtonSettings[strProp])
                try:
                    # see if there is a matching click operator setup
                    objNewBtn.set_mouse_up(getattr(self, f'{strButton}_click'))
                except:
                    pass
                # add the btn to "self"
                setattr(self, strButton, objNewBtn)
        # outside the button groups
        objSlider = BL_UI_Slider(
            self.Frame_SpacingPosition[0] + intButtonSpacing, self.Frame_SpacingPosition[1]+20, 70, 18)
        objSlider.style = 'NUMBER_CLICK'
        objSlider.text = 'space'
        objSlider.value = bpy.context.scene.KEY_frameSpace
        objSlider.step = 1
        objSlider.min = 1
        objSlider.max = 10
        objSlider.precision = 0
        objSlider.description = 'set the value for frame spacing'
        objSlider.rounded_corners = (1, 1, 0, 0)
        objSlider.set_value_updated(self.frame_space_slider_update)
        setattr(self, 'frame_space_slider', objSlider)

        objBtn = BL_UI_Button(
            self.Frame_SpacingPosition[0] + 74, self.Frame_SpacingPosition[1]+20, 50, 18)
        objBtn.text = "set"
        objBtn.description = "Frame Spacer: Set:**Applies the current number of spaces between keyframes."
        objBtn.text_size = 14
        objBtn.rounded_corners = (0, 0, 1, 1)
        objBtn.set_mouse_up(self.set_space_click)
        setattr(self, 'set_space', objBtn)

        intPositionX += intGroupSpacing
        # (panX, panY, panW, panH)
        self.panel = BL_UI_Drag_Panel(
            intButtonSize, intButtonSize*2, intPositionX, 66)
        # Options are: {HEADER,PANEL,SUBPANEL,TOOLTIP,NONE}
        self.panel.style = 'PANEL'
        self.panel.bg_color = (0, 0, 0, 0.5)
        self.panel.rounded_corners = (1, 1, 1, 1)

    def on_invoke(self, context, event):
        # Add your widgets here (TODO: perhaps a better, more automated solution?)
        # --------------------------------------------------------------------------------------------------

        widgets_panel = [self.panel]
        # widgets_items = [self.frame_space_slider]
        widgets_items = [self.frame_space_slider, self.set_space]
        for objGroup in self.arrButtonGroups:
            widgets_items.append(
                getattr(self, objGroup["name"].replace(" ", "_")))
            for strButton in objGroup['buttons']:
                widgets_items.append(getattr(self, strButton))
        widgets_items.append(self.tooltip)
        # --------------------------------------------------------------------------------------------------

        widgets = widgets_panel + widgets_items

        self.init_widgets(context, widgets, self.valid_modes)

        self.panel.add_widgets(widgets_items)

        self.panel.quadview, _, region = is_quadview_region(context)

        if self.panel.quadview and region:
            # When in QuadView mode it has to be manually repositioned otherwise may get stuck out of region space
            if __package__.find(".") != -1:
                package = __package__[0: __package__.find(".")]
            else:
                package = __package__
            if bpy.context.preferences.addons[package].preferences.RC_UI_BIND:
                # From Preferences/Interface/"Display"
                ui_scale = bpy.context.preferences.view.ui_scale
            else:
                ui_scale = 1
            over_scale = bpy.context.preferences.addons[package].preferences.RC_SCALE
            panX = int(
                (region.width - (self.panel.width * ui_scale * over_scale)) / 2.0) + 1
            panY = self.panel.height + 10 - 1  # The '10' is just a spacing from region border
            self.panel.set_location(panX, panY)
        else:
            self.panel.set_location(self.panel.x, self.panel.y)

        # This statement is necessary so that the remote panel stays open when called by Blender's <F3> menu
        bpy.context.window_manager.KEY_UI.RemoVisible = True

    # -- Helper function
    def terminate_execution(self, area, region, event):
        if self.panel.quadview and area is None:
            bpy.context.window_manager.KEY_UI.RemoVisible = False
        else:
            if not area is None:
                if area.type == 'VIEW_3D':
                    # If user switches between regular and QuadView display modes, the panel is automatically closed
                    is_quadview = (
                        len(area.spaces.active.region_quadviews) > 0)
                    if self.panel.quadview != is_quadview:
                        bpy.context.window_manager.KEY_UI.RemoVisible = False

        if event.type == 'TIMER' and bpy.context.window_manager.KEY_UI.RemoVisible:
            # Update the remote panel "clock marker". This marker is used to keep track if the remote panel is
            # actually opened and active. In the case that bpy.context.window_manager.KEY_UI.RemoVisible state gets misleading
            # the panel will be automatically closed when this clock marker has not been updated for more than 1 sec
            bpy.context.window_manager.KEY_UI.btnRemoTime = int(time.time())

        return (not bpy.context.window_manager.KEY_UI.RemoVisible)
# -------------------DEFINE OPERATORS----------------------

    def frame_space_slider_update(self, widget, value):
        intValue = round(value)
        widget.value = intValue
        try:
            bpy.context.scene.KEY_frameSpace = intValue
        except:
            pass

    def clear_key_click(self, widget, event, x, y):
        try:
            bpy.ops.key.clear_key(
                'INVOKE_DEFAULT', ctrl_pressed=event.ctrl, alt_pressed=event.alt)
        except:
            pass

    def insert_key_click(self, widget, event, x, y):
        try:
            bpy.ops.key.insert_key('INVOKE_DEFAULT', ctrl_pressed=event.ctrl)
        except:
            pass

    def remove_key_click(self, widget, event, x, y):
        try:
            bpy.ops.key.remove_key()
        except:
            pass

    def blank_key_click(self, widget, event, x, y):
        try:
            bpy.ops.key.blank_key('INVOKE_DEFAULT', ctrl_pressed=event.ctrl)
        except:
            pass

    def clone_key_click(self, widget, event, x, y):
        try:
            bpy.ops.key.clone_key('INVOKE_DEFAULT', ctrl_pressed=event.ctrl)
        except:
            pass

    def clone_unique_key_click(self, widget, event, x, y):
        try:
            bpy.ops.key.clone_unique_key()
        except:
            pass

    def clone_object_click(self, widget, event, x, y):
        try:
            bpy.ops.key.clone_object()
        except:
            pass

    def clone_object_blank_keys_click(self, widget, event, x, y):
        try:
            bpy.ops.key.clone_object_blank_keys()
        except:
            pass

    # def clone_object_blank_keys_click(self, widget, event, x, y):
    #    bpy.ops.key.clone_object_blank_keys()

    def add_space_click(self, widget, event, x, y):
        try:
            bpy.ops.key.add_space('INVOKE_DEFAULT', ctrl_pressed=event.ctrl)
        except:
            pass

    def remove_space_click(self, widget, event, x, y):
        try:
            bpy.ops.key.remove_space('INVOKE_DEFAULT', ctrl_pressed=event.ctrl)
        except:
            pass

    def no_space_click(self, widget, event, x, y):
        try:
            bpy.ops.key.no_space()
        except:
            pass

    def set_space_click(self, widget, event, x, y):
        try:
            bpy.ops.key.set_space()
        except:
            pass

    def separate_objects_click(self, widget, event, x, y):
        try:
            bpy.ops.key.separate_objects(
                'INVOKE_DEFAULT', ctrl_pressed=event.ctrl, alt_pressed=event.alt)
        except:
            pass

    def combine_objects_click(self, widget, event, x, y):
        try:
            bpy.ops.key.combine_objects(
                'INVOKE_DEFAULT', ctrl_pressed=event.ctrl)
        except:
            pass

    def pin_frames_click(self, widget, event, x, y):
        try:
            bpy.ops.key.pin_frames(
                'INVOKE_DEFAULT', ctrl_pressed=event.ctrl)
        except:
            pass

    def copy_data_click(self, widget, event, x, y):
        try:
            bpy.ops.key.merge_data()
        except:
            pass

    def add_asset_click(self, widget, event, x, y):
        try:
            bpy.ops.key.add_asset()
        except:
            pass

# -----------------------------------------
# -Register/unregister processes


def register():
    bpy.utils.register_class(KEY_OT_draw_operator)


def unregister():
    bpy.utils.unregister_class(KEY_OT_draw_operator)


if __name__ == '__main__':
    register()
