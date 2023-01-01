
# --- ### Header
from .bl_ui_widgets.bl_ui_drag_panel import BL_UI_Drag_Panel
from .bl_ui_widgets.bl_ui_draw_op import BL_UI_OT_draw_operator
from .bl_ui_widgets.bl_ui_tooltip import BL_UI_Tooltip
from .bl_ui_widgets.bl_ui_button import BL_UI_Button
from .bl_ui_widgets.bl_ui_label import BL_UI_Label
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

        # From Preferences/Themes/User Interface/"State"
        # theme = bpy.context.preferences.themes[0]
        # ui = theme.user_interface
        # widget_style = getattr(ui, "wcol_state")
        # status_color = tuple(widget_style.inner_changed) + (0.3,)
        # -----------

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
                "name": 'keys',
                "buttons": {
                    "insert_key": {"description": "Adds a single keyframe to the right of the timeline indicators playhead."},
                    "remove_key": {"description": "Removes a single keyframe to the right of the timeline indicators playhead."},
                    "insert_blank_key": {"description": "Inserts a single blank keyframe to the right of the timeline indicators playhead."},
                },
            }, {
                "name": 'duplicate',
                "buttons":
                    {
                        "clone_key": {"description": "Duplicates the current keyframe to the right of the current active keyframe/s."},
                        "clone_unique_key": {"description": "Duplicates the current keyframe to the right of the current active keyframe/s with a unique id."},
                        "clone_object": {"description": "Duplicates the object/s and the current keyframes with a unique id."},
                        "clone_object_blank_keys": {"description": "Duplicates the object/s with blank keyframes."},
                    },
            },  {
                "name": 'frames',
                "buttons": {
                    "add_space": {
                        "description": "Adds a single extra space between selected keyframes.",
                        "text": "ADD",
                        "textwo": "SPACE"
                    },
                    "remove_space": {
                        "description": "Subtracts a single between selected keyframes. A cumulative behavior till there are no more spaces between keyframes.",
                        "text": "REMOVE",
                        "textwo": "SPACE"
                    },
                    "set_space": {
                        "description": "Removes all space between selected keyframes",
                        "text": "NO",
                        "textwo": "SPACE"
                    }
                }
            }, {
                "name": 'objects',
                "buttons":
                    {
                        "separate_objects": {"description": "Separates and converts the currently active selection in edit mode to a new object."},
                        "combine_objects": {"description": "Combines the selected object with the active merging keyframe data"}
                    },
            }, {
                "name": 'geometry',
                "buttons": {
                    "copy_data": {"description": "Copies object data."},
                    "cut_data": {"description": "Cuts object data."},
                    "paste_data": {"description": "Paste object data."},
                },
            }, {
                "name": 'selected',
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
                objNewBtn = BL_UI_Button(
                    intPositionX, intPositionY, intButtonSize, intButtonSize)
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
        intPositionX += intGroupSpacing
        # (panX, panY, panW, panH)
        self.panel = BL_UI_Drag_Panel(
            intButtonSize, intButtonSize*2, intPositionX, 80)
        # Options are: {HEADER,PANEL,SUBPANEL,TOOLTIP,NONE}
        self.panel.style = 'PANEL'
        self.panel.bg_color = (0, 0, 0, 0.5)

        self.label1 = BL_UI_Label(5, 12, intPositionX, 18)
        self.label1.style = 'TITLE'
        self.label1.text = "StopMotion Actions"
        self.label1.size = 14

    def on_invoke(self, context, event):
        # Add your widgets here (TODO: perhaps a better, more automated solution?)
        # --------------------------------------------------------------------------------------------------
        widgets_panel = [self.panel]
        widgets_items = [self.label1]
        for objGroup in self.arrButtonGroups:
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

    def insert_key_click(self, widget, event, x, y):
        bpy.ops.key.insert()

    def remove_key_click(self, widget, event, x, y):
        print('remove_key_click')

    def insert_blank_key_click(self, widget, event, x, y):
        print('insert_blank_key_click')

    def clone_key_click(self, widget, event, x, y):
        print('clone_key_click')

    def clone_unique_key_click(self, widget, event, x, y):
        print('clone_unique_key_click')

    def clone_object_click(self, widget, event, x, y):
        print('clone_object_click')

    def clone_object_blank_keys_click(self, widget, event, x, y):
        print('clone_object_blank_keys_click')

    def add_space_click(self, widget, event, x, y):
        print('add_space_click')

    def remove_space_click(self, widget, event, x, y):
        print('remove_space_click')

    def set_space_click(self, widget, event, x, y):
        print('set_space_click')

    def separate_objects_click(self, widget, event, x, y):
        print('separate_objects_click')

    def combine_objects_click(self, widget, event, x, y):
        print('combine_objects_click')

    def copy_data_click(self, widget, event, x, y):
        print('copy_data_click')

    def cut_data_click(self, widget, event, x, y):
        print('cut_data_click')

    def paste_data_click(self, widget, event, x, y):
        print('paste_data_click')

    def add_asset_click(self, widget, event, x, y):
        print('add_asset_click', widget, event, x, y)

# -----------------------------------------
# -Register/unregister processes


def register():
    bpy.utils.register_class(KEY_OT_draw_operator)


def unregister():
    bpy.utils.unregister_class(KEY_OT_draw_operator)


if __name__ == '__main__':
    register()
