def getFCurves(obj, inDataBlock=False):
    arrFCurves = []
    if inDataBlock == False and hasattr(obj, 'animation_data') == True and hasattr(obj.animation_data, 'action') == True:
        try:
            arrFCurves = obj.animation_data.action.fcurves
        except:
            pass
    if inDataBlock == True and hasattr(obj.data, 'animation_data') == True and hasattr(obj.data.animation_data, 'action') == True:
        try:
            arrFCurves = obj.data.animation_data.action.fcurves
        except:
            pass
    return arrFCurves


def getFCurveByPath(obj, strPath, inDataBlock):
    arrFCurves = getFCurves(obj, inDataBlock)
    for fcurve in arrFCurves:
        if fcurve.data_path == strPath:
            return fcurve
    return None


def actKeyframe(obj, intFrame, strMode, inDataBlock=False):
    arrFcurves = getFCurves(obj, inDataBlock)
    for fcurve in arrFcurves:
        for keyframe in fcurve.keyframe_points:
            if keyframe.co[0] == intFrame:
                if strMode == 'get':
                    return keyframe
                elif strMode == 'remove':
                    fcurve.keyframe_points.remove(keyframe)


def setFrameSpacing(obj, intSpacing, inDataBlock=False):
    # get the selected range of frames for an object. Space the keyframe_points evenly by the input param
    # apply to object and data block animation_data
    arrSelectedFrames = getSelectedFrames(
        obj, None, 'x', inDataBlock, frames='selected')
    arrUnSelectedFrames = getSelectedFrames(
        obj, None, 'x', inDataBlock, frames='unSelected')
    intFrameCount = len(arrSelectedFrames)
    if intFrameCount > 0:
        # ordered unique set of selected Frames to work with across obj and data block
        arrSelectedFrames = list(set(arrSelectedFrames))
        arrSelectedFrames.sort()
        intFirstFrame = arrSelectedFrames[0]
        intRange = arrSelectedFrames[intFrameCount-1]-intFirstFrame
        # anything after this frame needs to get pushed by the delta.
        intLastFrame = intFirstFrame+(intFrameCount*intSpacing)
        # need to know if new range is larger or smaller
        dicFrames = {}
        if intFrameCount > 1:
            for i, intFrame in enumerate(arrSelectedFrames):
                dicFrames[intFrame] = intFirstFrame+(i*intSpacing)
        if len(arrUnSelectedFrames) > 0 and arrUnSelectedFrames[-1] > arrSelectedFrames[-1]:
            # make room by moving the unselected frame outside the range used + space
            arrFramesToMove = []
            for intFrame in arrUnSelectedFrames:
                if intFrame > arrSelectedFrames[-1]:
                    arrFramesToMove.append(intFrame)
            for i, intFrame in enumerate(arrFramesToMove):
                intDistance = intFrame - arrSelectedFrames[-1]
                # the new last position + the spacing being set + how many spaces ahead it was
                dicFrames[intFrame] = dicFrames[arrSelectedFrames[-1]
                                                ] + intDistance
        setNewFrames(obj, dicFrames, intLastFrame,
                     intRange, inDataBlock)
    return


def setNewFrames(obj, dicFrames, intLastFrame, intPushFrames, inDataBlock=False):
    arrFCurves = getFCurves(obj, inDataBlock)
    for i, fcurve in enumerate(arrFCurves):
        for ii, keyframe_point in enumerate(fcurve.keyframe_points):
            intFrame = keyframe_point.co.x
            intNewFrame = dicFrames.get(intFrame)
            if intNewFrame != None:
                intDiff = intNewFrame - keyframe_point.co.x
                keyframe_point.co.x = intNewFrame
                keyframe_point.handle_left.x = keyframe_point.handle_left.x + intDiff
                keyframe_point.handle_right.x = keyframe_point.handle_right.x + intDiff
            elif intFrame > intLastFrame:
                keyframe_point.co.x += intPushFrames
                keyframe_point.handle_left.x = keyframe_point.handle_left.x + intPushFrames
                keyframe_point.handle_right.x = keyframe_point.handle_right.x + intPushFrames
    return


def getKeyframeValue(obj, strPath, intFrame, mode, value='y'):
    intFrameId = None
    objFCurve = getFCurveByPath(obj, strPath, False)
    if objFCurve != None:
        for keyframe_point in objFCurve.keyframe_points:
            intValue = getattr(keyframe_point.co, value)
            if mode == '<':
                if keyframe_point.co.x < intFrame or (intFrameId is None and keyframe_point.co.x != intFrame):
                    intFrameId = intValue
            elif mode == '=':
                if keyframe_point.co.x == intFrame:
                    intFrameId = intValue
                    break
            elif mode == '<=':
                if keyframe_point.co.x <= intFrame or intFrameId is None:
                    intFrameId = intValue
            elif mode == 'max':
                if intFrameId is None:
                    intFrameId = 0
                if keyframe_point.co.y > intFrameId or intFrameId is None:
                    intFrameId = intValue
    if intFrameId != None:
        intFrameId = int(intFrameId)
    return intFrameId


def getSelectedFrames(obj, strPath, mode='y', inDataBlock=False, frames='selected'):
    arrFrames = []
    arrFCurves = getFCurves(obj, inDataBlock)
    for i, fcurve in enumerate(arrFCurves):
        if strPath is None or fcurve.data_path == strPath:
            for ii, keyframe_point in enumerate(fcurve.keyframe_points):
                if frames == 'selected' and keyframe_point.select_control_point == True:
                    arrFrames.append(getattr(keyframe_point.co, mode))
                elif frames == 'unSelected' and keyframe_point.select_control_point == False:
                    arrFrames.append(getattr(keyframe_point.co, mode))
                elif frames == 'all':
                    arrFrames.append(getattr(keyframe_point.co, mode))
    return arrFrames


def removeSelectedKeyframe(obj, strPath, inDataBlock=False):
    arrFrames = []
    objFCurve = getFCurveByPath(obj, strPath, inDataBlock)
    if objFCurve != None:
        for ii, keyframe in enumerate(objFCurve.keyframe_points):
            if keyframe.select_control_point == True:
                try:
                    objFCurve.keyframe_points.remove(keyframe, fast=True)
                except:
                    pass
    return


def removeKeyframe(obj, strPath, intFrame, inDataBlock=False):
    arrFCurves = getFCurves(obj, inDataBlock)
    for i, fcurve in enumerate(arrFCurves):
        if fcurve.data_path == strPath or strPath == None:
            for ii, keyframe in enumerate(fcurve.keyframe_points):
                if int(keyframe.co.x) == intFrame:
                    try:
                        fcurve.keyframe_points.remove(keyframe, fast=True)
                    except:
                        pass
    return

# keyframes.setKeyType(obj, '["key_object_id"]', intFrame+1, 'MOVING_HOLD')


def setKeyType(obj, strPath, intFrame, strType, inDataBlock=False):
    objFCurve = getFCurveByPath(obj, strPath, inDataBlock)
    if objFCurve != None:
        for ii, keyframe in enumerate(objFCurve.keyframe_points):
            if keyframe.co.x == intFrame:
                try:
                    keyframe.type = strType
                except:
                    pass
    return


def nudgeFrames(obj, intStart, intMove, inDataBlock=False, intStop=None, strPath=None):
    arrFCurves = getFCurves(obj, inDataBlock)
    for i, fcurve in enumerate(arrFCurves):
        if fcurve.data_path == strPath or strPath == None:
            intX = 0
            for ii, keyframe_point in enumerate(fcurve.keyframe_points):
                intNextFrame = None
                if len(fcurve.keyframe_points) > ii+1:
                    intNextFrame = fcurve.keyframe_points[ii+1].co.x
                if keyframe_point.co.x >= intStart and (intStop == None or intStop >= keyframe_point.co.x):
                    # lets make sure we aren't overwriting a keyframe_point
                    intNewX = keyframe_point.co.x + intMove
                    if intNewX > intX and intNewX >= intStart:
                        keyframe_point.co.x = intNewX
                        keyframe_point.handle_left.x = keyframe_point.handle_left.x + intMove
                        keyframe_point.handle_right.x = keyframe_point.handle_right.x + intMove
                    intX = keyframe_point.co.x
    return


def getKeyframeVacancy(obj, strpath, intFrame, intNextFrame):
    # if current frame is open
    intCurrentKeyValue = getKeyframeValue(
        obj, strpath, intFrame, '=', value='y')
    if intCurrentKeyValue is None:
        return 'CURRENT'
    # if this frame has a key but next one is open
    intNextKeyValue = getKeyframeValue(
        obj, strpath, intNextFrame, '=', value='y')
    if intNextKeyValue is None:
        return 'NEXT'
    # if this frame has a key and next one has a key
    return 'MOVE'


def getFrames(obj, strPath, intFrame, direction, mode='y', intCount=False):
    # mode = x for frame number, mode = y for value
    arrFrames = []
    objFCurve = getFCurveByPath(obj, strPath, False)
    if objFCurve != None:
        for keyframe_point in objFCurve.keyframe_points:
            if direction == '<' and keyframe_point.co.x < intFrame:
                arrFrames.append(getattr(keyframe_point.co, mode))
            elif direction == '>' and keyframe_point.co.x > intFrame:
                arrFrames.append(getattr(keyframe_point.co, mode))
        if intCount is not False and len(arrFrames) > intCount:
            if direction == '<':
                arrFrames = arrFrames[-intCount]
                # reverse the array
                arrFrames = arrFrames[::-1]
            elif direction == '>':
                arrFrames = arrFrames[0:intCount]
    return arrFrames


def transferFrameState(objSource, objTarget, intFrame, inDataBlock=False):
    arrFcurves = getFCurves(objSource, inDataBlock)
    for fcurve in arrFcurves:
        if fcurve.array_index is not None and fcurve.data_path[0] != '[':
            strDataPath = fcurve.data_path
            if inDataBlock == True:
                strDataPath = f'data.{strDataPath}'
            objData = objTarget.path_resolve(strDataPath)
            intValue = fcurve.evaluate(intFrame)
            if isinstance(objData, float):
                # need to back string path off one and not use the array_index
                arrDataPath = strDataPath.split('.')
                strProperty = arrDataPath.pop()
                # objData = eval('.'.join(arrDataPath))
                objData = objTarget.path_resolve('.'.join(arrDataPath))
                setattr(objData, strProperty, intValue)
            else:
                objData[fcurve.array_index] = intValue
            # except Exception as e:
