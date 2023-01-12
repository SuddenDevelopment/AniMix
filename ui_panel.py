
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
        # Prevents multiple instances of panel
        try:
            if context.window_manager.KEY_UI.RemoVisible and int(time.time()) - context.window_manager.KEY_UI.btnRemoTime <= 1:
                return False
        except:
            return False
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
            "bg_color": (0, 0, 0, 0),
            "text": "",
            "outline_color": (1, 1, 1, 0.4),
            "roundness": 0.4,
            "corner_radius": 10,
            "has_shadow": True,
            "rounded_corners": (0, 0, 0, 0),
            "iconFile": 'add_asset',
            "imageSize": (44, 44),
            "imagePosition": (3, 3)
        }
        # group buttons and give overrides
        self.arrButtonGroups = [
            {
                "name": 'StopMotion Keys',
                "buttons": {
                    "clear_key": {"description": "Clear a single keyframe to the right of the timeline indicators playhead."},
                },
            }, {
                "name": '',
                "buttons": {
                    "insert_key": {"description": "Add a single keyframe to the right of the timeline indicators playhead."},
                    "remove_key": {"description": "Remove a single keyframe to the right of the timeline indicators playhead."},
                    "blank_key": {"description": "Insert a single blank keyframe to the right of the timeline indicators playhead."},
                },
            }, {
                "name": 'Duplicate',
                "buttons":
                    {
                        "clone_key": {"description": "Duplicate the current keyframe to the right of the current active keyframe/s."},
                        "clone_unique_key": {"description": "Duplicate the current keyframe to the right of the current active keyframe/s with a unique id."},
                        "clone_object": {"description": "Duplicate the object/s and the current keyframes with a unique id."},
                    },
            },  {
                "name": 'Frame Spacing',
                "setPosition": True,
                "buttons": {
                    "add_space": {
                        "description": "Adds a single extra space between selected keyframes.",
                        "imageSize": (44, 22),
                        "buttonSize": (50, 28)
                    },
                    "remove_space": {
                        "description": "Subtracts a single between selected keyframes. A cumulative behavior till there are no more spaces between keyframes.",
                        "imageSize": (44, 22),
                        "buttonSize": (50, 28)
                    },
                    "no_space": {
                        "description": "Removes all space between selected keyframes",
                        "imageSize": (44, 22),
                        "buttonSize": (50, 28)
                    }
                }
            }, {
                "name": 'Compose Frames',
                "buttons":
                    {
                        "separate_objects": {"description": "Separates and converts the currently active selection in edit mode to a new object."},
                        "combine_objects": {"description": "Combines the selected object with the active merging keyframe data"}
                    },
            }, {
                "name": 'Geo',
                "buttons": {
                    "copy_data": {"description": "Copies object data."},
                },
            }, {
                "name": 'Assets',
                "buttons":
                    {
                        "add_asset": {"description": "Create assets out of what is selected. Object & Edit mode and Keyframe data is supported."},
                    }
            }
        ]
        # layout settings
        intGroupSpacing = 10
        intButtonSpacing = 5
        intButtonSize = 50

        # flywheel values
        intPositionX = 0
        intPositionY = 20
        for objButtonGroup in self.arrButtonGroups:
            intPositionX += intGroupSpacing
            intButtonCount = len(objButtonGroup['buttons'])
            # create the group label
            objLabel = BL_UI_Label(
                intPositionX+intGroupSpacing, 15,
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
            self.Frame_SpacingPosition[0] + intButtonSpacing, self.Frame_SpacingPosition[1]+32, 105, 18)
        objSlider.style = 'NUMBER_CLICK'
        objSlider.text = 'Frame Space'
        objSlider.value = 2
        objSlider.step = 1
        objSlider.min = 1
        objSlider.max = 10
        objSlider.precision = 0
        objSlider.description = 'set the value for frame spacing'
        objSlider.set_value_updated(self.frame_space_slider_update)
        setattr(self, 'frame_space_slider', objSlider)

        intPositionX += intGroupSpacing
        # (panX, panY, panW, panH)
        self.panel = BL_UI_Drag_Panel(
            intButtonSize, intButtonSize*2, intPositionX, 80)
        # Options are: {HEADER,PANEL,SUBPANEL,TOOLTIP,NONE}
        self.panel.style = 'PANEL'
        self.panel.bg_color = (0, 0, 0, 0.5)

    def on_invoke(self, context, event):
        # Add your widgets here (TODO: perhaps a better, more automated solution?)
        # --------------------------------------------------------------------------------------------------
        widgets_panel = [self.panel]
        #widgets_items = [self.frame_space_slider]
        widgets_items = [self.frame_space_slider]
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
                package = __package__[0:__package__.find(".")]
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
        self.value = intValue
        print(intValue)
        bpy.context.scene.KEY_frameSpace = intValue

    def clear_key_click(self, widget, event, x, y):
        bpy.ops.key.clear_key()

    def insert_key_click(self, widget, event, x, y):
        bpy.ops.key.insert_key()

    def remove_key_click(self, widget, event, x, y):
        bpy.ops.key.remove_key()

    def blank_key_click(self, widget, event, x, y):
        bpy.ops.key.blank_key()

    def clone_key_click(self, widget, event, x, y):
        bpy.ops.key.clone_key()

    def clone_unique_key_click(self, widget, event, x, y):
        bpy.ops.key.clone_unique_key()

    def clone_object_click(self, widget, event, x, y):
        bpy.ops.key.clone_object()

    # def clone_object_blank_keys_click(self, widget, event, x, y):
    #    bpy.ops.key.clone_object_blank_keys()

    def add_space_click(self, widget, event, x, y):
        bpy.ops.key.add_space()

    def remove_space_click(self, widget, event, x, y):
        bpy.ops.key.remove_space()

    def no_space_click(self, widget, event, x, y):
        bpy.ops.key.no_space()

    def separate_objects_click(self, widget, event, x, y):
        bpy.ops.key.separate_objects()

    def combine_objects_click(self, widget, event, x, y):
        bpy.ops.key.combine_objects()

    def copy_data_click(self, widget, event, x, y):
        bpy.ops.key.merge_data()

    def add_asset_click(self, widget, event, x, y):
        bpy.ops.key.add_asset()

# -----------------------------------------
# -Register/unregister processes


def register():
    bpy.utils.register_class(KEY_OT_draw_operator)


def unregister():
    bpy.utils.unregister_class(KEY_OT_draw_operator)


if __name__ == '__main__':
    register()
