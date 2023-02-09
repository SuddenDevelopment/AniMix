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


class KEY_OT_ClearKey(bpy.types.Operator):
    """remove all geo on current frame for active object"""
    bl_idname = "key.clear_key"
    bl_label = "Clear Key"
    bl_options = {'REGISTER', 'UNDO'}

    ctrl_pressed: bpy.props.BoolProperty(default=False)
    alt_pressed: bpy.props.BoolProperty(default=False)

    def invoke(self, context, event):
        if event.ctrl:
            self.ctrl_pressed = True
        else:
            self.ctrl_pressed = False
        if event.alt:
            self.alt_pressed = True
        else:
            self.alt_pressed = False
        return self.execute(context)

    @ classmethod
    def poll(cls, context):
        return len(context.selected_objects) > 0

    def execute(self, context):
        if len(context.selected_objects) > 0:
            strMode = context.object.mode
            obj = context.active_object
            # object swapping for key feature
            if strMode == 'EDIT':
                if self.alt_pressed == True:
                    if obj.type == 'MESH':
                        bpy.ops.mesh.select_all(action='INVERT')
                    elif obj.type == 'CURVE':
                        bpy.ops.curve.select_all(action='INVERT')
                if self.ctrl_pressed == True or self.alt_pressed == True:
                    if obj.type == 'MESH':
                        bpy.ops.mesh.delete(type='VERT')
                    elif obj.type == 'CURVE':
                        bpy.ops.curve.delete(type='VERT')
                else:
                    bpy.ops.object.mode_set(mode='OBJECT')
                    actions.removeGeo(obj)
                    bpy.ops.object.mode_set(mode='EDIT')
            else:
                actions.removeGeo(obj)
            # actions.setSwapObject(context, context.active_object, context.scene.frame_current)
        return {'FINISHED'}


class KEY_OT_InsertKey(bpy.types.Operator):
    """Create a Stop Motion Key for the current object"""
    bl_idname = "key.insert_key"
    bl_label = "Insert Stop Motion Key"
    bl_options = {'REGISTER', 'UNDO'}

    ctrl_pressed: bpy.props.BoolProperty(default=False)

    def invoke(self, context, event):
        if event.ctrl:
            self.ctrl_pressed = True
        else:
            self.ctrl_pressed = False
        return self.execute(context)

    @ classmethod
    def poll(cls, context):
        return len(context.selected_objects) > 0

    def execute(self, context):
        if context.active_object.data is not None and hasattr(context.active_object.data, 'animation_data') and hasattr(context.active_object.data.animation_data, 'action'):
            self.report(
                {'ERROR'}, "This object has data block animation data that will not survive data block swapping")
        if len(context.selected_objects) > 0:
            for obj in context.selected_objects:
                intFrame = context.scene.frame_current
                intDirection = 1
                if self.ctrl_pressed == True:
                    intDirection = -1
                intNextFrame = intFrame+intDirection
                strAction = keyframes.getKeyframeVacancy(
                    obj, '["key_object_id"]', intFrame, intNextFrame)
                if strAction == 'CURRENT':
                    actions.setSwapObject(
                        context, obj, intFrame)
                elif strAction == 'NEXT':
                    context.scene.frame_set(intNextFrame)
                    actions.setSwapObject(
                        context, obj, intNextFrame)
                else:
                    intStartFrame = intFrame
                    intStopFrame = None
                    if intDirection == -1:
                        intStartFrame = 0
                        intStopFrame = intFrame
                    keyframes.nudgeFrames(
                        obj, intStartFrame, intDirection, False, intStopFrame)
                    actions.setSwapObject(
                        context, obj, intFrame)

        return {'FINISHED'}


class KEY_OT_RemoveKey(bpy.types.Operator):
    """remove swap keys for selected objects+frames"""
    bl_idname = "key.remove_key"
    bl_label = "Remove Key Data"
    bl_options = {'REGISTER', 'UNDO'}

    @ classmethod
    def poll(cls, context):
        return len(context.selected_objects) > 0

    def execute(self, context):
        for obj in context.selected_objects:
            actions.remove_keys(
                obj, context.scene.frame_current, True)
        # actions.onFrame(context.scene)
        return {'FINISHED'}


class KEY_OT_BlankKey(bpy.types.Operator):
    bl_idname = "key.blank_key"
    bl_label = "Insert Blank Key"
    bl_options = {'REGISTER', 'UNDO'}
    ctrl_pressed: bpy.props.BoolProperty(default=False)

    def invoke(self, context, event):
        if event.ctrl:
            self.ctrl_pressed = True
        else:
            self.ctrl_pressed = False
        return self.execute(context)

    @ classmethod
    def poll(cls, context):
        return len(context.selected_objects) > 0

    def execute(self, context):
        if len(context.selected_objects) > 0:
            intDirection = 1
            if self.ctrl_pressed == True:
                intDirection = -1
            intNextFrame = context.scene.frame_current+intDirection
            for obj in context.selected_objects:
                objBlank = actions.getBlankFrameObject(obj)
                intSwapObjectID = objBlank.get('key_object_id')
                strAction = keyframes.getKeyframeVacancy(
                    obj, '["key_object_id"]', context.scene.frame_current, intNextFrame)
                if strAction == 'CURRENT':
                    actions.setSwapKey(obj, intSwapObjectID,
                                       context.scene.frame_current, update=True, )
                elif strAction == 'NEXT':
                    context.scene.frame_set(intNextFrame)
                    actions.setSwapKey(obj, intSwapObjectID,
                                       intNextFrame, update=False)
                else:
                    intStartFrame = context.scene.frame_current
                    intStopFrame = None
                    if intDirection == -1:
                        intStartFrame = 0
                        intStopFrame = context.scene.frame_current
                    keyframes.nudgeFrames(
                        obj, intStartFrame, intDirection, False, intStopFrame)
                    actions.setSwapKey(obj, intSwapObjectID,
                                       context.scene.frame_current, update=False)
            actions.onFrame(context.scene)
        return {'FINISHED'}


class KEY_OT_CloneKey(bpy.types.Operator):
    bl_idname = "key.clone_key"
    bl_label = "Duplicate Key"
    bl_options = {'REGISTER', 'UNDO'}
    ctrl_pressed: bpy.props.BoolProperty(default=False)

    def invoke(self, context, event):
        if event.ctrl:
            self.ctrl_pressed = True
        else:
            self.ctrl_pressed = False
        return self.execute(context)

    @ classmethod
    def poll(cls, context):
        return len(context.selected_objects) > 0

    def execute(self, context):
        if len(context.selected_objects) > 0:
            intDirection = 1
            if self.ctrl_pressed == True:
                intDirection = -1
            intNextFrame = context.scene.frame_current + intDirection
            for obj in context.selected_objects:
                actions.clone_key(
                    context, obj, context.scene.frame_current, intNextFrame)
            context.scene.frame_set(intNextFrame)
        return {'FINISHED'}


class KEY_OT_CloneUniqueKey(bpy.types.Operator):
    bl_idname = "key.clone_unique_key"
    bl_label = "Duplicate Unique Key"
    bl_options = {'REGISTER', 'UNDO'}

    @ classmethod
    def poll(cls, context):
        return len(context.selected_objects) > 0

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
        return len(context.selected_objects) > 0

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
        return len(context.selected_objects) > 0

    def execute(self, context):
        if len(context.selected_objects) > 0:
            for obj in context.selected_objects:
                objNew = actions.clone_object(context, obj, True)
                actions.removeGeo(objNew)
                actions.removeGeo(actions.getTmp(objNew))
        return {'FINISHED'}


class KEY_OT_AddSpace(bpy.types.Operator):
    bl_idname = "key.add_space"
    bl_label = "Add Keyframe Space"
    bl_options = {'REGISTER', 'UNDO'}
    ctrl_pressed: bpy.props.BoolProperty(default=False)

    def invoke(self, context, event):
        if event.ctrl:
            self.ctrl_pressed = True
        else:
            self.ctrl_pressed = False
        return self.execute(context)

    @ classmethod
    def poll(cls, context):
        return len(context.selected_objects) > 0

    def execute(self, context):
        # nudgeFrames(obj, intStart, intMove, inDataBlock=False, intStop=None)
        intStart = context.scene.frame_current+1
        intStop = None
        intDirection = 1
        if self.ctrl_pressed == True:
            intStart = 0
            intStop = context.scene.frame_current
            intDirection = -1
        for obj in context.selected_objects:
            keyframes.nudgeFrames(
                obj, intStart, intDirection, True, intStop)
            keyframes.nudgeFrames(
                obj, intStart, intDirection, False, intStop)
        return {'FINISHED'}


class KEY_OT_RemoveSpace(bpy.types.Operator):
    bl_idname = "key.remove_space"
    bl_label = "Remove Keyframe Space"
    bl_options = {'REGISTER', 'UNDO'}
    ctrl_pressed: bpy.props.BoolProperty(default=False)

    def invoke(self, context, event):
        if event.ctrl:
            self.ctrl_pressed = True
        else:
            self.ctrl_pressed = False
        return self.execute(context)

    @ classmethod
    def poll(cls, context):
        return len(context.selected_objects) > 0

    def execute(self, context):
        # nudgeFrames(obj, intStart, intMove, inDataBlock=False, intStop=None)
        intStart = context.scene.frame_current+1
        intStop = None
        intDirection = -1
        if self.ctrl_pressed == True:
            intStart = 0
            intStop = context.scene.frame_current
            intDirection = 1
        for obj in context.selected_objects:
            keyframes.nudgeFrames(
                obj, intStart, intDirection, True, intStop)
            keyframes.nudgeFrames(
                obj, intStart, intDirection, False, intStop)
        return {'FINISHED'}


class KEY_OT_SetSpace(bpy.types.Operator):
    bl_idname = "key.set_space"
    bl_label = "Set Keyframe Space"
    bl_options = {'REGISTER', 'UNDO'}

    @ classmethod
    def poll(cls, context):
        return len(context.selected_objects) > 0

    def execute(self, context):
        for obj in context.selected_objects:
            keyframes.setFrameSpacing(obj, context.scene.KEY_frameSpace, True)
            keyframes.setFrameSpacing(obj, context.scene.KEY_frameSpace, False)
        return {'FINISHED'}


class KEY_OT_NoSpace(bpy.types.Operator):
    bl_idname = "key.no_space"
    bl_label = "Remove Keyframe Space"
    bl_options = {'REGISTER', 'UNDO'}

    @ classmethod
    def poll(cls, context):
        return len(context.selected_objects) > 0

    def execute(self, context):
        for obj in context.selected_objects:
            keyframes.setFrameSpacing(obj, 1, True)
            keyframes.setFrameSpacing(obj, 1, False)
        return {'FINISHED'}


class KEY_OT_SeparateObjects(bpy.types.Operator):
    """remove selected frames from active object to be their own objects in a collection"""
    bl_idname = "key.separate_objects"
    bl_label = "Separate Selected Frames"
    bl_options = {'REGISTER', 'UNDO'}
    ctrl_pressed: bpy.props.BoolProperty(default=False)
    alt_pressed: bpy.props.BoolProperty(default=False)

    def invoke(self, context, event):
        if event.ctrl:
            self.ctrl_pressed = True
        else:
            self.ctrl_pressed = False
        if event.alt:
            self.alt_pressed = True
        else:
            self.alt_pressed = False
        return self.execute(context)

    @ classmethod
    def poll(cls, context):
        return len(context.selected_objects) > 0

    def execute(self, context):
        strMode = context.object.mode
        obj = context.active_object
        # exposeSelectedFrameObjects(obj, intFrame, remove=False, select=True)
        if strMode == 'EDIT':
            objNew = actions.getCurrentFrame(obj, context.scene.frame_current)
            bpy.ops.object.mode_set(mode='OBJECT')
            obj.select_set(False)
            context.view_layer.objects.active = objNew
            objNew.select_set(True)
            bpy.ops.object.mode_set(mode='EDIT')
            if self.alt_pressed == False:
                if objNew.type == 'MESH':
                    bpy.ops.mesh.select_all(action='INVERT')
                elif objNew.type == 'CURVE':
                    bpy.ops.curve.select_all(action='INVERT')
            if objNew.type == 'MESH':
                bpy.ops.mesh.delete(type='VERT')
            elif objNew.type == 'CURVE':
                bpy.ops.curve.delete(type='VERT')
            bpy.ops.object.mode_set(mode='OBJECT')
            objNew.select_set(False)
            obj.select_set(True)
            context.view_layer.objects.active = obj
            bpy.ops.object.mode_set(mode='EDIT')
        else:
            if self.ctrl_pressed == True or self.alt_pressed == True:
                actions.exposeSelectedFrameObjects(
                    obj, self.alt_pressed, self.alt_pressed)
            else:
                actions.getCurrentFrame(obj, context.scene.frame_current)
        return {'FINISHED'}


class KEY_OT_CombineObjects(bpy.types.Operator):
    """add selected objects as keyframe objects in active_object"""
    bl_idname = "key.combine_objects"
    bl_label = "Add Selected to Active"
    bl_options = {'REGISTER', 'UNDO'}
    ctrl_pressed: bpy.props.BoolProperty(default=False)

    def invoke(self, context, event):
        if event.ctrl:
            self.ctrl_pressed = True
        else:
            self.ctrl_pressed = False
        return self.execute(context)

    @ classmethod
    def poll(cls, context):
        return len(context.selected_objects) > 0 and context.active_object is not None

    def execute(self, context):
        if self.ctrl_pressed == True:
            actions.addSwapObjects(
                context, context.selected_objects, context.active_object)
            for obj in context.selected_objects:
                if obj != context.active_object:
                    bpy.data.objects.remove(obj)
        else:
            bpy.ops.object.join()
            actions.setSwapObject(context, context.active_object,
                                  context.scene.frame_current)
        return {'FINISHED'}


class KEY_OT_PinFrames(bpy.types.Operator):
    bl_idname = "key.pin_frames"
    bl_label = "Pin Frames"
    bl_options = {'REGISTER', 'UNDO'}
    ctrl_pressed: bpy.props.BoolProperty(default=False)

    def invoke(self, context, event):
        if event.ctrl:
            self.ctrl_pressed = True
        else:
            self.ctrl_pressed = False
        return self.execute(context)

    @ classmethod
    def poll(cls, context):
        return len(context.selected_objects) > 0 and context.active_object is not None

    def execute(self, context):
        if self.ctrl_pressed:
            actions.unpinFrames()
        else:
            for obj in context.selected_objects:
                if obj.type == 'MESH' or obj.type == 'CURVE':
                    actions.pinFrame(context, obj, context.scene.frame_current)
        return {'FINISHED'}


class KEY_OT_MergeData(bpy.types.Operator):
    """merge selected objects to the current frame of active object"""
    bl_idname = "key.merge_data"
    bl_label = "Merge Selected to Active"
    bl_options = {'REGISTER', 'UNDO'}

    @ classmethod
    def poll(cls, context):
        return context.active_object is not None and len(context.selected_objects) > 0

    def execute(self, context):
        bpy.ops.object.join()
        actions.setSwapObject(context, context.active_object,
                              context.scene.frame_current)
        return {'FINISHED'}


class KEY_OT_AddAsset(bpy.types.Operator):
    """copy selected frames to be their own object"""
    bl_idname = "key.add_asset"
    bl_label = "Frames to Assets"
    bl_options = {'REGISTER', 'UNDO'}

    @ classmethod
    def poll(cls, context):
        return len(context.selected_objects) > 0

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
    KEY_OT_ClearKey,
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
    KEY_OT_NoSpace,
    KEY_OT_SeparateObjects,
    KEY_OT_CombineObjects,
    KEY_OT_PinFrames,
    KEY_OT_MergeData,
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
