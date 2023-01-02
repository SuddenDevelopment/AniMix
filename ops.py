import bpy
import time
import sys
from . import actions
from . import keyframes

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


class KEY_OT_InsertKey(bpy.types.Operator):
    """Create a Stop Motion Key for the current object"""
    bl_idname = "key.insert_key"
    bl_label = "Insert Stop Motion Key"
    bl_options = {'REGISTER', 'UNDO'}

    @ classmethod
    def poll(cls, context):
        return context.selected_objects is not None

    def execute(self, context):
        if context.active_object.data is not None and hasattr(context.active_object.data, 'animation_data') and hasattr(context.active_object.data.animation_data, 'action'):
            self.report(
                {'ERROR'}, "This object has data block animation data that will not survive data block swapping")
        actions.setSwapObject(context, context.active_object,
                              context.scene.frame_current)
        return {'FINISHED'}


class KEY_OT_RemoveKey(bpy.types.Operator):
    """remove swap keys for selected objects+frames"""
    bl_idname = "key.remove_key"
    bl_label = "Remove Key Data"
    bl_options = {'REGISTER', 'UNDO'}

    @ classmethod
    def poll(cls, context):
        return context.selected_objects is not None

    def execute(self, context):
        for obj in context.selected_objects:
            actions.remove_keys(obj)
        return {'FINISHED'}


class KEY_OT_BlankKey(bpy.types.Operator):
    bl_idname = "key.blank_key"
    bl_label = "Insert Blank Key"
    bl_options = {'REGISTER', 'UNDO'}

    @ classmethod
    def poll(cls, context):
        return context.selected_objects is not None

    def execute(self, context):
        for obj in context.selected_objects:
            keyframes.nudgeFrames(
                obj, context.scene.frame_current, 1, False)
            if obj.type == 'CURVE':
                intSwapId = obj.get('key_id')
                intSwapObjectID = actions.getNextSwapObjectId(obj)
                strNewObjName = actions.getSwapObjectName(
                    intSwapId, intSwapObjectID)
                objData = bpy.data.curves.new(name=strNewObjName, type='CURVE')
                objTmp = bpy.data.objects.new(strNewObjName, objData)
                objTmp.data.use_fake_user = True
                objTmp["key_id"] = intSwapId
                actions.setSwapKey(obj, intSwapObjectID,
                                   context.scene.frame_current+1, update=False)
        return {'FINISHED'}


class KEY_OT_CloneKey(bpy.types.Operator):
    bl_idname = "key.clone_key"
    bl_label = "Duplicate Key"
    bl_options = {'REGISTER', 'UNDO'}

    @ classmethod
    def poll(cls, context):
        return context.selected_objects is not None

    def execute(self, context):
        for obj in context.selected_objects:
            actions.clone_key(context, obj, context.scene.frame_current)
        return {'FINISHED'}


class KEY_OT_CloneUniqueKey(bpy.types.Operator):
    bl_idname = "key.clone_unique_key"
    bl_label = "Duplicate Unique Key"
    bl_options = {'REGISTER', 'UNDO'}

    @ classmethod
    def poll(cls, context):
        return context.selected_objects is not None

    def execute(self, context):
        for obj in context.selected_objects:
            actions.clone_unique_key(context, obj, context.scene.frame_current)
        return {'FINISHED'}


class KEY_OT_CloneObject(bpy.types.Operator):
    bl_idname = "key.clone_object"
    bl_label = "Duplicate Object"
    bl_options = {'REGISTER', 'UNDO'}

    @ classmethod
    def poll(cls, context):
        return context.selected_objects is not None

    def execute(self, context):
        for obj in context.selected_objects:
            actions.clone_object(context, obj)
        return {'FINISHED'}


class KEY_OT_CloneObjectBlankKeys(bpy.types.Operator):
    bl_idname = "key.clone_object_blank_keys"
    bl_label = "Duplicate Object Blank Keys"
    bl_options = {'REGISTER', 'UNDO'}

    @ classmethod
    def poll(cls, context):
        return context.selected_objects is not None

    def execute(self, context):
        for obj in context.selected_objects:
            print('Duplicate Object Blank Keys op')
        return {'FINISHED'}


class KEY_OT_AddSpace(bpy.types.Operator):
    bl_idname = "key.add_space"
    bl_label = "Add Keyframe Space"
    bl_options = {'REGISTER', 'UNDO'}

    @ classmethod
    def poll(cls, context):
        return context.selected_objects is not None

    def execute(self, context):
        for obj in context.selected_objects:
            keyframes.nudgeFrames(
                obj, context.scene.frame_current, context.scene.KEY_frameSpace, True)
            keyframes.nudgeFrames(
                obj, context.scene.frame_current, context.scene.KEY_frameSpace, False)
        return {'FINISHED'}


class KEY_OT_RemoveSpace(bpy.types.Operator):
    bl_idname = "key.remove_space"
    bl_label = "Remove Keyframe Space"
    bl_options = {'REGISTER', 'UNDO'}

    @ classmethod
    def poll(cls, context):
        return context.selected_objects is not None

    def execute(self, context):
        for obj in context.selected_objects:
            keyframes.nudgeFrames(
                obj, context.scene.frame_current, context.scene.KEY_frameSpace*-1, True)
            keyframes.nudgeFrames(
                obj, context.scene.frame_current, context.scene.KEY_frameSpace*-1, False)
        return {'FINISHED'}


class KEY_OT_SetSpace(bpy.types.Operator):
    bl_idname = "key.set_space"
    bl_label = "Set Keyframe Space"
    bl_options = {'REGISTER', 'UNDO'}

    @ classmethod
    def poll(cls, context):
        return context.selected_objects is not None

    def execute(self, context):
        for obj in context.selected_objects:
            keyframes.setFrameSpacing(obj, context.scene.KEY_frameSpace, True)
            keyframes.setFrameSpacing(obj, context.scene.KEY_frameSpace, False)
        return {'FINISHED'}


class KEY_OT_SeparateObjects(bpy.types.Operator):
    """remove selected frames from active object to be their own objects in a collection"""
    bl_idname = "key.separate_objects"
    bl_label = "Separate Selected Frames"
    bl_options = {'REGISTER', 'UNDO'}

    @ classmethod
    def poll(cls, context):
        return context.active_object is not None

    def execute(self, context):
        actions.exposeSelectedFrameObjects(context.active_object, True)
        return {'FINISHED'}


class KEY_OT_CombineObjects(bpy.types.Operator):
    """add selected objects as keyframe objects in active_object"""
    bl_idname = "key.combine_objects"
    bl_label = "Add Selected to Active"
    bl_options = {'REGISTER', 'UNDO'}

    @ classmethod
    def poll(cls, context):
        return context.selected_objects is not None and context.active_object is not None

    def execute(self, context):
        actions.addSwapObjects(
            context, context.selected_objects, context.active_object)
        return {'FINISHED'}


class KEY_OT_MergeData(bpy.types.Operator):
    """merge selected objects to the current frame of active object"""
    bl_idname = "key.merge_data"
    bl_label = "Merge Selected to Active"
    bl_options = {'REGISTER', 'UNDO'}

    @ classmethod
    def poll(cls, context):
        return context.active_object is not None and context.selected_objects is not None

    def execute(self, context):
        bpy.ops.object.join()
        actions.setSwapObject(context, context.active_object,
                              context.scene.frame_current)
        return {'FINISHED'}


class KEY_OT_CopySelected(bpy.types.Operator):
    """copy selected frames to be their own object"""
    bl_idname = "key.copy_selected"
    bl_label = "Copy Selected Frames"
    bl_options = {'REGISTER', 'UNDO'}

    @ classmethod
    def poll(cls, context):
        return context.active_object is not None

    def execute(self, context):
        actions.exposeSelectedFrameObjects(context.active_object, False)
        return {'FINISHED'}


class KEY_OT_AddAsset(bpy.types.Operator):
    """copy selected frames to be their own object"""
    bl_idname = "key.add_asset"
    bl_label = "Frames to Assets"
    bl_options = {'REGISTER', 'UNDO'}

    @ classmethod
    def poll(cls, context):
        return context.active_object is not None

    def execute(self, context):
        # create a collection with the name of the object
        for obj in context.selected_objects:
            actions.add_asset(obj)
        return {'FINISHED'}


class KEY_OT_Show_Panel(bpy.types.Operator):
    ''' Opens/Closes the remote control demo panel '''
    bl_idname = "key.viewport_panel"
    bl_label = "Show Viewport Panel"
    bl_description = "Open the Viewport Panel for easier tablet friendly buttons"

    # --- Blender interface methods
    @classmethod
    def poll(cls, context):
        return True

    def invoke(self, context, event):
        # input validation:
        return self.execute(context)

    def execute(self, context):
        if context.window_manager.KEY_UI.RemoVisible and int(time.time()) - context.window_manager.KEY_UI.btnRemoTime <= 1:
            # If it is active then set its visible status to False so that it be closed and reset the button label
            context.window_manager.KEY_UI.btnRemoText = "Show Viewport Panel"
            context.window_manager.KEY_UI.RemoVisible = False
        else:
            # If it is not active then set its visible status to True so that it be opened and reset the button label
            context.window_manager.KEY_UI.btnRemoText = "Hide Viewport Panel"
            context.window_manager.KEY_UI.RemoVisible = True
            is_quadview, area, region = is_quadview_region(context)
            if is_quadview:
                override = bpy.context.copy()
                override["area"] = area
                override["region"] = region
            # Had to put this "try/except" statement because when user clicked repeatedly too fast
            # on the operator's button it would crash the call due to a context incorrect situation
            try:
                if is_quadview:
                    context.window_manager.KEY_UI.objRemote = bpy.ops.object.dp_ot_draw_operator(
                        override, 'INVOKE_DEFAULT')
                else:
                    context.window_manager.KEY_UI.objRemote = bpy.ops.object.dp_ot_draw_operator(
                        'INVOKE_DEFAULT')
            except:
                return {'CANCELLED'}

        return {'FINISHED'}


arrClasses = [
    KEY_OT_InsertKey,
    KEY_OT_RemoveKey,
    KEY_OT_BlankKey,
    KEY_OT_CloneKey,
    KEY_OT_CloneUniqueKey,
    KEY_OT_CloneObject,
    KEY_OT_CloneObjectBlankKeys,
    KEY_OT_AddSpace,
    KEY_OT_RemoveSpace,
    KEY_OT_SetSpace,
    KEY_OT_SeparateObjects,
    KEY_OT_CombineObjects,
    KEY_OT_MergeData,
    KEY_OT_CopySelected,
    KEY_OT_AddAsset,
    KEY_OT_Show_Panel
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


def unregister():
    cleanse_modules()
    for i in reversed(arrClasses):
        bpy.utils.unregister_class(i)
