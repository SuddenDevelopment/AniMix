import bpy
from . import config
from . import keyframes


def getSwapId(obj):
    intId = obj.get('key_id')
    if intId is not None:
        return intId
    return None


def getNextSwapId():
    intIndex = 0
    for obj in bpy.data.objects:
        intId = getSwapId(obj)
        if intId is not None and intId > intIndex:
            intIndex = intId
    return intIndex+1


def getNextSwapObjectId():
    intIndex = 0
    for obj in bpy.data.objects:
        intObjectId = obj.get("key_object_id")
        if intObjectId is not None and intObjectId > intIndex:
            intIndex = intObjectId
    return intIndex+1


def setSwapKey(obj, intObjectId, intFrame):
    obj['key_object_id'] = intObjectId
    obj.keyframe_insert(
        data_path='["key_object_id"]', frame=intFrame)
    for fcurve in obj.animation_data.action.fcurves:
        if fcurve.data_path == '["key_object_id"]':
            for keyframe_point in fcurve.keyframe_points:
                keyframe_point.interpolation = 'CONSTANT'


def getSwapObjectName(obj, intFrame):
    # container/placeholder id + frame created
    # frame created doesn't need to be the only frame used. you can copy and past the key to reuse
    intSwapId = obj.get("key_id")
    if intSwapId is not None:
        return f'{config.PREFIX}_{intSwapId}_{intFrame}'


def getObject(strName):
    for obj in bpy.data.objects:
        if obj.name_full == strName:
            return obj
    return None


def swapData(objTarget, objReference):
    objTarget.data = objReference.data
    if objReference.animation_data is not None:
        objTarget.animation_data = objReference.animation_data
    objTarget["key_object"] = objReference.name_full


def getFrameObject(obj, intObjectId):
    if intObjectId is not None:
        strSwapObject = getSwapObjectName(obj, intObjectId)
        objFrame = getObject(strSwapObject)
        if objFrame is not None:
            return objFrame
    return None


def onFrame(scene):
    context = bpy.context
    strMode = context.object.mode
    # object swapping for key feature
    if strMode == 'EDIT':
        bpy.ops.object.mode_set(mode='OBJECT')
    for obj in scene.objects:
        # obj must have an id and set an object_id it expects
        # obj must have same id as swa object and not already by the one in use
        # intObjectId = obj.get("key_object_id")
        intObjectId = keyframes.getKeyframeValue(
            obj, '["key_object_id"]', scene.frame_current, '<=')
        if obj.get("key_id") is not None and intObjectId is not None:
            objFrame = getFrameObject(obj, intObjectId)
            if objFrame is not None and obj.get("key_object") != objFrame.name_full:
                swapData(obj, objFrame)
    if strMode == 'EDIT':
        bpy.ops.object.mode_set(mode='EDIT')


def setSwapObject(context, obj, intFrame):
    if context.object.mode == 'EDIT':
        obj.update_from_editmode()
    # get the ID for the OBJECT group (not the frame/mesh)
    intSwapId = obj.get('key_id')
    if intSwapId is None:
        intSwapId = getNextSwapId()
        obj['key_id'] = intSwapId
    if hasattr(context, 'active_object') == False:
        context.view_layer.objects.active = obj
    intSwapObjectId = keyframes.getKeyframeValue(
        obj, '["key_object_id"]', intFrame, '=')
    # print('setSwapObject', intFrame, intSwapObjectId)
    if intSwapObjectId is None:
        intSwapObjectId = getNextSwapObjectId()
        intSwapObjectId = int(intSwapObjectId)
    strFrame = getSwapObjectName(obj, intSwapObjectId)
    obj["key_object"] = strFrame
    # make sure a frame object doesn't already exist
    objFrame = getObject(strFrame)
    if objFrame is None:
        print('no frame object found', strFrame)
        # create the frame object
        objFrame = bpy.data.objects.new(strFrame, obj.data.copy())
        objFrame.data.use_fake_user = True
        objFrame["key_id"] = obj.get('key_id')
    else:
        objFrame.data = obj.data.copy()
    if obj.animation_data is not None and hasattr(obj.animation_data, 'copy'):
        objFrame.animation_data = obj.animation_data.copy()
    if obj.data.animation_data is not None and hasattr(obj.data.animation_data, 'copy'):
        objFrame.data.animation_data = obj.data.animation_data.copy()
    setSwapKey(obj, intSwapObjectId, intFrame)
    bpy.app.handlers.frame_change_post.clear()
    bpy.app.handlers.frame_change_post.append(onFrame)


def removeObject(obj):
    bpy.data.objects.remove(obj)
    strType = obj.type
    if strType == 'CURVE':
        bpy.data.curves.remove(obj.data)
    elif strType == 'MESH':
        bpy.data.meshes.remove(obj.data)


def removeAllKeyData(obj):
    keyframes.removeKeyframes(obj, '["key_object_id"]')
    intGroupID = obj.get('key_id')
    if intGroupID is not None:
        for objTmp in bpy.data.objects:
            if objTmp.get('key_id') == intGroupID and objTmp.name_full.startswith(f'{config.PREFIX}_'):
                removeObject(obj)
    return
