import bpy
from . import config
from . import keyframes


def getNextSwapId():
    intIndex = 0
    for obj in bpy.data.objects:
        intId = obj.get("key_id")
        if intId is not None and intId > intIndex:
            intIndex = intId
    return intIndex+1


def getNextSwapObjectId(obj):
    intSwapObjectId = keyframes.getKeyframeValue(
        obj, '["key_object_id"]', 0, 'max')
    if intSwapObjectId is None:
        return 0
    return intSwapObjectId+1


def setSwapKey(obj, intObjectId, intFrame, update=True):
    strPath = '["key_object_id"]'
    if update == True:
        obj['key_object_id'] = intObjectId
    objFCurve = keyframes.getFCurveByPath(
        obj, strPath, False)
    if objFCurve == None:
        obj.keyframe_insert(data_path=strPath, frame=intFrame)
    else:
        objFCurve.keyframe_points.insert(
            frame=intFrame, value=intObjectId)
        for keyframe_point in objFCurve.keyframe_points:
            keyframe_point.interpolation = 'CONSTANT'
    keyframes.setKeyType(obj, strPath, intFrame,
                         'BREAKDOWN', inDataBlock=False)


def getSwapObjectName(intSwapId, intSwapObjectId):
    # container/placeholder id + frame created
    # frame created doesn't need to be the only frame used. you can copy and past the key to reuse
    if intSwapId is not None and intSwapObjectId is not None:
        return f'{config.PREFIX}_{intSwapId}_{intSwapObjectId}'


def getObject(strName):
    for obj in bpy.data.objects:
        if obj.name_full == strName:
            return obj
    return None


def getObjectCopy(obj):
    if obj is not None:
        objNew = obj.copy()
        objNew.data = obj.data.copy()
        if obj.animation_data is not None and obj.animation_data.action is not None:
            objNew.animation_data.action = obj.animation_data.action.copy()
        if obj.data.animation_data is not None and obj.data.animation_data.action is not None:
            objNew.data.animation_data.action = obj.data.animation_data.action.copy()
        return objNew


def swapData(objTarget, objReference, updateProp=True):
    if objTarget and objReference:
        objTarget.data = objReference.data
        if objReference.animation_data is not None:
            try:
                objTarget.animation_data = objReference.animation_data
            except:
                pass
        if updateProp == True:
            objTarget["key_object"] = objReference.name_full


def getFrameObject(obj, intObjectId):
    if intObjectId is not None:
        strSwapObject = getSwapObjectName(obj.get("key_id"), intObjectId)
        objFrame = getObject(strSwapObject)
        if objFrame is not None:
            return objFrame
    return None


def getTmp(objTarget):
    intSwapId = objTarget.get("key_id")
    if intSwapId is not None:
        strTmp = f'{config.PREFIX}_{intSwapId}_tmp'
        objTmp = getObject(strTmp)
        if objTmp is not None:
            return objTmp
        else:
            return setTmp(objTarget)


def setDataBlock(objTarget, objReference):
    objDataBlock = objTarget.data
    objTarget.data = objReference.data.copy()
    if objTarget.type == 'CURVE':
        bpy.data.curves.remove(objDataBlock)
    elif objTarget.type == 'MESH':
        bpy.data.meshes.remove(objDataBlock)


def setTmp(obj, forceNew=False):
    intSwapId = obj.get("key_id")
    strTmp = f'{config.PREFIX}_{intSwapId}_tmp'
    objTmp = getObject(strTmp)
    if forceNew == True and objTmp is not None:
        bpy.data.objects.remove(objTmp, do_unlink=True)
        objTmp = None
    if objTmp is not None:
        setDataBlock(objTmp, obj)
    else:
        objTmp = bpy.data.objects.new(strTmp, obj.data.copy())
        objTmp.data.use_fake_user = True
        objTmp.use_fake_user = True
        objTmp["key_id"] = intSwapId
    return objTmp


def getDataSum(obj):
    # an attempt to get the cheapest data compare possible for equal or not
    intSum = 0
    if obj:
        # add text, metaballs
        if obj.type == 'FONT':
            intSum = hash(obj.data.body)
        if obj.type == 'META':
            intSum += len(obj.data.elements)
            for elem in obj.data.elements:
                intSum += elem.co.x + elem.co.y + elem.co.z
                intSum += elem.radius
        if obj.type == 'MESH':
            intSum += len(obj.data.vertices)
            for vert in obj.data.vertices:
                intSum += vert.co.x + vert.co.y + vert.co.z
        elif obj.type == 'CURVE':
            intSum += len(obj.data.splines)
            for spline in obj.data.splines:
                intSum += len(spline.points)
                intSum += len(spline.bezier_points)
                for point in spline.points:
                    intSum += point.co.x + point.co.y + point.co.z
                for point in spline.bezier_points:
                    intSum += point.co.x + point.co.y + point.co.z
                    intSum += point.handle_left.x + point.handle_left.y + point.handle_left.z
                    intSum += point.handle_right.x + point.handle_right.y + point.handle_right.z
        return intSum
    return None


def onFramePre(scene):
    context = bpy.context
    strMode = 'OBJECT'
    if context.active_object is not None:
        strMode = context.object.mode
    # object swapping for key feature
    if strMode == 'EDIT' or strMode == 'SCULPT':
        # bpy.ops.object.mode_set(mode='OBJECT')
        for obj in scene.objects:
            obj.update_from_editmode()
            strFrame = obj.get("key_object")
            objFrame = getObject(strFrame)
            objTmp = getTmp(obj)
            if objFrame is not None and obj.get("key_object") == objFrame.name:
                intSumTmp = getDataSum(objTmp)
                intSumFrame = getDataSum(objFrame)
                if intSumTmp != intSumFrame:
                    setDataBlock(objFrame, objTmp)
        bpy.ops.object.mode_set(mode=strMode)


def onFrame(scene):
    context = bpy.context
    strMode = 'OBJECT'
    if context.active_object is not None:
        strMode = context.object.mode
    # object swapping for key feature
    if strMode == 'EDIT':
        bpy.ops.object.mode_set(mode='OBJECT')
    for obj in scene.objects:
        # obj must have an id and set an object_id it expects
        # obj must have same id as swa object and not already by the one in use
        # intObjectId = obj.get("key_object_id")
        objTmp = getTmp(obj)
        intObjectId = keyframes.getKeyframeValue(
            obj, '["key_object_id"]', scene.frame_current, '<=')
        if intObjectId is not None:
            intObjectId = int(intObjectId)
            objFrame = getFrameObject(obj, intObjectId)
            if objFrame is not None and obj.get("key_object") != objFrame.name_full:
                swapData(obj, objFrame)
                objTmp = setTmp(objFrame)
                swapData(obj, objTmp, False)
    if strMode == 'EDIT':
        bpy.ops.object.mode_set(mode='EDIT')


def getSwapId(obj):
    # get the ID for the OBJECT group (not the frame/mesh)
    intSwapId = obj.get('key_id')
    if intSwapId is None:
        intSwapId = getNextSwapId()
        obj['key_id'] = intSwapId
    # set a tmp object if none exists
    strTmp = f'{config.PREFIX}_{intSwapId}_tmp'
    objTmp = getObject(strTmp)
    if objTmp is None:
        objTmp = bpy.data.objects.new(strTmp, obj.data.copy())
        objTmp.data.use_fake_user = True
        objTmp.use_fake_user = True
        objTmp["key_id"] = intSwapId
    return intSwapId


def getSwapObjectId(obj, intFrame):
    intSwapObjectId = keyframes.getKeyframeValue(
        obj, '["key_object_id"]', intFrame, '=')
    if intSwapObjectId is None:
        intSwapObjectId = getNextSwapObjectId(obj)
    return intSwapObjectId


def removeGeo(obj):
    if obj.type == 'CURVE':
        for i, spline in enumerate(obj.data.splines):
            try:
                obj.data.splines.remove(spline)
            except:
                pass
    elif obj.type == 'MESH':
        try:
            obj.data.vertices.data.clear_geometry()
        except:
            pass


def setFrameObject(obj, strFrame, intSwapId):
    objFrame = getObject(strFrame)
    if objFrame is None:
        # create the frame object
        objFrame = bpy.data.objects.new(strFrame, obj.data.copy())
        objFrame.data.use_fake_user = True
        objFrame.use_fake_user = True
        objFrame["key_id"] = intSwapId
    else:
        objFrame.data = obj.data.copy()
    # if obj.animation_data is not None and hasattr(obj.animation_data, 'copy'):
    #    objFrame.animation_data = obj.animation_data.copy()
    if obj.data.animation_data is not None and hasattr(obj.data.animation_data, 'copy'):
        objFrame.data.animation_data = obj.data.animation_data.copy()


def setSwapObject(context, obj, intFrame):
    strMode = context.object.mode
    if strMode == 'EDIT':
        obj.update_from_editmode()
    intSwapId = getSwapId(obj)
    intSwapObjectId = getSwapObjectId(obj, intFrame)
    strFrame = getSwapObjectName(obj.get("key_id"), intSwapObjectId)
    obj["key_object"] = strFrame
    # make sure a frame object doesn't already exist
    setFrameObject(obj, strFrame, intSwapId)
    setSwapKey(obj, intSwapObjectId, intFrame)
    setTmp(obj, True)
    bpy.app.handlers.frame_change_post.clear()
    bpy.app.handlers.frame_change_post.append(onFrame)
    bpy.app.handlers.frame_change_pre.clear()
    bpy.app.handlers.frame_change_pre.append(onFramePre)


# take all selected objects, and assign them to active object as keyframes from current position
def addSwapObjects(context, arrSelected, obj):
    intSwapId = getSwapId(obj)
    intCurrentFrame = context.scene.frame_current
    for i, objSelected in enumerate(arrSelected):
        if objSelected != context.active_object:
            intInsertFrame = intCurrentFrame+i
            keyframes.nudgeFrames(obj, intInsertFrame, 1)
            intSwapObjectId = getSwapObjectId(obj, intInsertFrame)
            # get the frame object name based on the target object
            strFrame = getSwapObjectName(obj.get("key_id"), intSwapObjectId)
            # but the objects being copied are the selected ones
            setFrameObject(objSelected, strFrame, intSwapId)
            # set swap key, but dont change current key, because we are nudging frames not changing frames
            setSwapKey(obj, intSwapObjectId, intInsertFrame, update=False)


def removeObject(obj):
    bpy.data.objects.remove(obj)
    strType = obj.type
    if strType == 'CURVE':
        bpy.data.curves.remove(obj.data)
    elif strType == 'MESH':
        bpy.data.meshes.remove(obj.data)


def getBlankFrameObject(obj):
    intSwapId = obj.get('key_id')
    intSwapObjectID = getNextSwapObjectId(obj)
    strNewObjName = getSwapObjectName(
        intSwapId, intSwapObjectID)
    if strNewObjName:
        objTmp = bpy.data.objects.new(strNewObjName, obj.data.copy())
        objTmp.data.use_fake_user = True
        objTmp.use_fake_user = True
        objTmp["key_object_id"] = intSwapObjectID
        objTmp["key_id"] = intSwapId
        removeGeo(objTmp)
        return objTmp


def redraw(arrAreas=[]):
    # redraw(['DOPESHEET_EDITOR', 'GRAPH_EDITOR'])
    for area in bpy.context.screen.areas:
        if len(arrAreas) == 0 or area.type in arrAreas:
            for region in area.regions:
                region.tag_redraw()


def remove_keys(obj, intFrame, all=False):
    strPath = None
    if all == False:
        strPath = '["key_object_id"]'
    keyframes.removeKeyframe(obj, strPath, intFrame, False)
    keyframes.removeKeyframe(obj, strPath, intFrame, True)

    # pull keyframes left by one
    keyframes.nudgeFrames(obj, intFrame, -1, False, None, strPath)
    keyframes.nudgeFrames(obj, intFrame, -1, True, None, strPath)
    redraw(['DOPESHEET_EDITOR', 'GRAPH_EDITOR'])
    return


def insert_blank(obj, intFrame):
    print('not sure what to do here, BLANK is not a keyframe concept?')


def clone_key(context, obj, intFrame, intNextFrame):
    intLastKey = keyframes.getKeyframeValue(
        obj, '["key_object_id"]', intFrame, '<=', value='x')
    if intLastKey:
        strAction = keyframes.getKeyframeVacancy(
            obj, '["key_object_id"]', intFrame, intNextFrame)
        if strAction != 'CURRENT':
            # Push keyframes to make room for duplicate
            intStartFrame = intNextFrame
            intStopFrame = None
            intDirection = 1
            if intNextFrame < intFrame:
                intStartFrame = 0
                intStopFrame = intStopFrame
                intDirection = -1
            keyframes.nudgeFrames(obj, intStartFrame,
                                  intDirection, False, intStopFrame)
        else:
            intNextFrame = intFrame
        # get current key
        intSwapObjectId = obj["key_object_id"]
        # find the last frame to have this key so we can update its type

        if intSwapObjectId is not None:
            # Duplicate key in next frame
            setSwapKey(obj, intSwapObjectId, intNextFrame, update=False)

            keyframes.setKeyType(obj, '["key_object_id"]',
                                 intLastKey, 'MOVING_HOLD')
            keyframes.setKeyType(obj, '["key_object_id"]',
                                 intNextFrame, 'MOVING_HOLD')
            # bpy.context.active_object.animation_data.action.fcurves[0].keyframe_points[0].type = 'KEYFRAME'


def clone_unique_key(context, obj, intFrame):
    # Push keyframes to make room for duplicate
    keyframes.nudgeFrames(obj, intFrame+1, 1)
    # get the current frame object
    intSwapObjectId = keyframes.getKeyframeValue(
        obj, '["key_object_id"]', intFrame, '=')
    strFrameObject = getSwapObjectName(obj.get("key_id"), intSwapObjectId)
    objFrame = getObject(strFrameObject)
    # copy the current frame object to a new one
    addSwapObjects(context, [objFrame], obj)
    return


def clone_object(context, obj, blank=False):
    # copy the primary object
    objNew = getObjectCopy(obj)
    objNew['key_id'] = None
    # change the swap id
    setSwapObject(context, objNew, context.scene.frame_current)
    objCollection = obj.users_collection[0]
    objCollection.objects.link(objNew)
    # copy all of the frames associated, using the new swap id, but SAME frame object id
    intSwapId = getSwapId(objNew)
    arrFrames = keyframes.getFrames(obj, '["key_object_id"]', -1, '>')
    arrFrames = list(set(arrFrames))
    for intFrame in arrFrames:
        intFrame = int(intFrame)
        # get the frame IDs
        strFrame = getSwapObjectName(getSwapId(obj), intFrame)
        objFrame = getObject(strFrame)
        if objFrame:
            strNewFrame = getSwapObjectName(intSwapId, intFrame)
            objNewFrame = getObject(strNewFrame)
            if objNewFrame is None:
                objNewFrame = getObjectCopy(objFrame)
                objNewFrame.name = strNewFrame
            objNewFrame['key_id'] = intSwapId
            if blank == True:
                removeGeo(objNewFrame)
    return objNew


def add_asset(obj):
    # get a list of the the objects
    arrFrames = keyframes.getSelectedFrames(obj, '["key_object_id"]', 'y')
    arrFrames = list(set(arrFrames))
    # set the collection as an asset .asset_mark()
    for intFrame in arrFrames:
        intFrame = int(intFrame)
        strFrameObject = getSwapObjectName(obj.get("key_id"), intFrame)
        objFrame = getObject(strFrameObject)
        if objFrame:
            objFrame.asset_mark()
            objFrame.asset_generate_preview()


def getCurrentFrame(obj, intFrame, link=True):
    # get the data object needed.
    strFrame = obj.get("key_object")
    objFrame = getObject(strFrame)

    if objFrame == None:
        objFrame = obj
    strFrameName = f'{obj.name}_Frame_{intFrame}'
    # make a copy
    objNew = bpy.data.objects.new(
        strFrameName, objFrame.data.copy())
    if link == True:
        objCollection = obj.users_collection[0]
        objCollection.objects.link(objNew)
    objNew.data.animation_data_clear()
    keyframes.transferFrameState(obj, objNew, intFrame, False)
    keyframes.transferFrameState(obj, objNew, intFrame, True)
    return objNew


def exposeSelectedFrameObjects(obj, intFrame, remove=False, select=True):
    arrNewObjects = []
    # unselect the parent object
    obj.select_set(False)
    objCollection = obj.users_collection[0]
    # get the selected keyframes array
    arrKeyframes = keyframes.getSelectedFrames(obj, '["key_object_id"]', 'x')
    if arrKeyframes is None:
        # intFrame = keyframes.getKeyframeValue(obj, '["key_object_id"]', intFrame, '<=', 'x')
        arrKeyframes[intFrame]
    for intFrame in arrKeyframes:
        intFrame = int(intFrame)
        # get the object for that keyframe
        intSwapObjectId = keyframes.getKeyframeValue(
            obj, '["key_object_id"]', intFrame, '=')
        strFrameObject = getSwapObjectName(obj.get("key_id"), intSwapObjectId)
        objFrame = getObject(strFrameObject)
        # link the object to the same collection as parent
        if objFrame == None:
            objFrame = obj.copy()
        strFrameName = f'{obj.name}_Frame_{intFrame}'
        if remove == True:
            objFrame.name = strFrameName
            objCollection.objects.link(objFrame)
            objFrame['key_id'] = None
            # remove keyframes from old object
            keyframes.actKeyframe(obj, intFrame, 'remove')
            objFrame.animation_data_clear()
            keyframes.transferFrameState(obj, objFrame, intFrame, False)
            keyframes.transferFrameState(obj, objFrame, intFrame, True)
            arrNewObjects.append(objFrame)
        elif remove == False:
            # make a copy
            objNew = bpy.data.objects.new(
                strFrameName, objFrame.data.copy())
            objCollection.objects.link(objNew)
            objNew.select_set(select)
            objNew.data.animation_data_clear()
            keyframes.transferFrameState(obj, objNew, intFrame, False)
            keyframes.transferFrameState(obj, objNew, intFrame, True)
            copySelections(obj, objNew)
            arrNewObjects.append(objNew)
        else:
            print('stop motion could find frame object to separate', strFrameObject)
    obj.select_set(not select)
    return arrNewObjects


def getMaterial(strMaterial):
    objMaterial = None
    if strMaterial in bpy.data.materials.keys():
        objMaterial = bpy.data.materials[strMaterial]
    else:
        objMaterial = bpy.data.materials.new(name=strMaterial)
        objMaterial.use_nodes = True
        objMaterial.blend_method = 'BLEND'
        objMaterial.node_tree.nodes["Principled BSDF"].inputs['Alpha'].default_value = 0.2
    return objMaterial


def copyConstraints(context, objSource, objTarget, intFrame=None):
    for constraint in objSource.constraints:
        new_constraint = objTarget.constraints.new(constraint.type)
        for attr in dir(constraint):
            if not attr.startswith("__"):
                try:
                    setattr(new_constraint, attr, getattr(constraint, attr))
                except:
                    pass
        objConstraintTarget = constraint.target
        if intFrame != None:
            strTarget = f'{objConstraintTarget.name}_Frame_{intFrame}'
            objNewTarget = pinFrame(context, objConstraintTarget, intFrame)
            if objNewTarget:
                objConstraintTarget = objNewTarget
        new_constraint.target = objConstraintTarget


def copyModifiers(objSource, objTarget):
    # Loop through all modifiers on the source object
    for src_mod in objSource.modifiers:
        # Create a new modifier on the destination object
        dest_mod = objTarget.modifiers.new(src_mod.name, src_mod.type)
        # Copy the properties of the source modifier to the destination modifier
        for prop in src_mod.bl_rna.properties:
            if prop.identifier not in {'rna_type', 'name', 'type'}:
                try:
                    setattr(dest_mod, prop.identifier,
                            getattr(src_mod, prop.identifier))
                except:
                    pass


def getCollection(strCollection, objParent):
    if strCollection not in bpy.data.collections:
        objCollection = bpy.data.collections.new(name=strCollection)
        if objParent != None:
            objParent.children.link(objCollection)
        else:
            print("no parent for: "+strCollection)
    return bpy.data.collections[strCollection]


def pinFrame(context, obj, intFrame):
    # arrFrameObjects = exposeSelectedFrameObjects(obj, intFrame, remove=False, select=False)
    # for objFrame in arrFrameObjects:
    # set custom property as pinned so we can quickly remove later
    objCollection = getCollection(
        f'pinned_frames', context.scene.collection)
    objPinCollection = getCollection(f'pinned {obj.name}', objCollection)
    strFrame = f'{obj.name}_Frame_{intFrame}'
    objFrame = getObject(strFrame)
    if objFrame != None:
        return objFrame
    else:
        objFrame = getCurrentFrame(obj, intFrame, False)
    # get the old pin if it exists for this obj+frame, this is necessary so that some objects can create pins for relationship objects and
    if objFrame == None:
        objFrame = obj.copy()
    objPinCollection.objects.link(objFrame)
    objFrame.parent = None
    objFrame["key_object_type"] = 'pinned'

    # remove the materials
    objFrame.data.materials.clear()
    # set them as unselectable
    objFrame.hide_select = True
    objFrame.data.animation_data_clear()
    keyframes.transferFrameState(obj, objFrame, intFrame, False)
    keyframes.transferFrameState(obj, objFrame, intFrame, True)
    # move the frameobject to the sam world location as the original
    objFrame.location = obj.matrix_world.to_translation()
    objFrame.rotation_euler = obj.matrix_world.to_euler()
    copyConstraints(context, obj, objFrame, intFrame)
    copyModifiers(obj, objFrame)
    # give them a transparent material
    objMaterial = getMaterial('KEY_OnionSkin')
    if objMaterial is not None:
        objFrame.data.materials.append(objMaterial)
    return objFrame


def unpinFrames():
    for obj in bpy.data.objects:
        if obj.get("key_object_type") == 'pinned':
            bpy.data.objects.remove(obj)


def copySelections(objSource, objTarget):
    if objSource.type == 'MESH':
        for vert in objSource.data.vertices:
            try:
                objTarget.data.vertices[vert.index].Select = vert.Select
            except:
                pass
    elif objSource.type == 'CURVE':
        for i, spline in enumerate(objSource.data.splines):
            for ii, point in enumerate(spline.points):
                try:
                    objTarget.data.splines[i].points[ii].select = point.select
                except:
                    pass
            for ii, point in enumerate(spline.bezier_points):
                try:
                    objTarget.data.splines[i].bezier_points[ii].select_control_point = point.select_control_point
                except:
                    pass
