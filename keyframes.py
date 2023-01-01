def getFCurves(obj, inDataBlock=False):
    arrFCurves = []
    if inDataBlock == False and hasattr(obj, 'animation_data') == True and obj.animation_data != None:
        arrFCurves = obj.animation_data.action.fcurves
    if inDataBlock == True and hasattr(obj.data, 'animation_data') == True and obj.data.animation_data != None:
        arrFCurves = obj.data.animation_data.action.fcurves
    return arrFCurves


def actKeyframe(obj, intFrame, strMode, inDataBlock=False):
    arrFcurves = getFCurves(obj, inDataBlock)
    for fcurve in arrFcurves:
        for keyframe in fcurve.keyframe_points:
            if keyframe.co[0] == intFrame:
                if strMode == 'get':
                    return keyframe
                elif strMode == 'remove':
                    fcurve.keyframe_points.remove(keyframe)


def setFrameSpacing(obj, intSpacing):
    # get the selected range of frames for an object. Space the keyframe_points evenly by the input param
    # apply to object and data block animation_data
    arrAllFrames = getFCurves(obj, False)
    arrDataFrames = getFCurves(obj, True)
    arrAllFrames = arrAllFrames + arrDataFrames
    # ordered unique set of selected Frames to work with across obj and data block
    arrAllFrames.sort()
    arrAllFrames = [*set(arrAllFrames)]
    intFrameCount = len(arrAllFrames)
    intFirstFrame = arrAllFrames[0]
    intRange = arrAllFrames[intFrameCount-1]-intFirstFrame
    # anything after this frame needs to get pushed by the delta.
    intLastFrame = intFirstFrame+(intFrameCount*intSpacing)
    # need to know if new range is larger or smaller
    dicFrames = {}
    if intFrameCount > 1:
        for i, intFrame in enumerate(arrAllFrames):
            dicFrames[intFrame] = intFirstFrame+(i*intSpacing)
    setNewFrames(obj, dicFrames, intLastFrame,
                 intRange, inDataBlock=False)
    setNewFrames(obj, dicFrames, intLastFrame,
                 intRange, True)
    return


def setNewFrames(obj, dicFrames, intLastFrame, intPushFrames, inDataBlock=False):
    arrFCurves = getFCurves(obj, inDataBlock)
    print(dicFrames)
    for i, fcurve in enumerate(arrFCurves):
        for ii, keyframe_point in enumerate(fcurve.keyframe_points):
            intFrame = keyframe_point.co.x
            intNewFrame = dicFrames.get(intFrame)
            if intNewFrame != None:
                keyframe_point.co.x = intNewFrame
            elif intFrame > intLastFrame:
                keyframe_point.co.x += intPushFrames
    return


def getKeyframeValue(obj, strPath, intFrame, mode):
    intFrameId = None
    arrFcurves = getFCurves(obj)
    for fcurve in arrFcurves:
        if fcurve.data_path == strPath:
            for keyframe_point in fcurve.keyframe_points:
                if mode == '<':
                    if keyframe_point.co.x < intFrame or (intFrameId is None and keyframe_point.co.x != intFrame):
                        intFrameId = keyframe_point.co.y
                elif mode == '=':
                    if keyframe_point.co.x == intFrame:
                        intFrameId = keyframe_point.co.y
                        break
                elif mode == '<=':
                    if keyframe_point.co.x <= intFrame or intFrameId is None:
                        intFrameId = keyframe_point.co.y
                elif mode == 'max':
                    if intFrameId is None:
                        intFrameId = 0
                    if keyframe_point.co.y > intFrameId or intFrameId is None:
                        intFrameId = keyframe_point.co.y
    if intFrameId != None:
        intFrameId = int(intFrameId)
    return intFrameId


def getSelectedFrames(obj, strPath, inDataBlock=False):
    arrFrames = []
    arrFCurves = getFCurves(obj, inDataBlock)
    for i, fcurve in enumerate(arrFCurves):
        if fcurve.data_path == strPath:
            for ii, keyframe_point in enumerate(fcurve.keyframe_points):
                if keyframe_point.select_control_point == True:
                    arrFrames.append(int(keyframe_point.co.x))
    return arrFrames


def removeKeyframes(obj, strPath, inDataBlock=False):
    arrFrames = []
    arrFCurves = getFCurves(obj, inDataBlock)
    for i, fcurve in enumerate(arrFCurves):
        if fcurve.data_path == strPath:
            for ii, keyframe in enumerate(fcurve.keyframe_points):
                if keyframe.select_control_point == True:
                    fcurve.keyframe_points.remove(keyframe, fast=True)
    return


def nudgeFrames(obj, intStart, intMove, inDataBlock=False):
    arrFCurves = getFCurves(obj, inDataBlock)
    for i, fcurve in enumerate(arrFCurves):
        for ii, keyframe_point in enumerate(fcurve.keyframe_points):
            if keyframe_point.co.x >= intStart:
                keyframe_point.co.x = keyframe_point.co.x + intMove
    return


def getFrames(obj, strPath, intFrame, intCount, mode):
    arrFrames = []
    arrFcurves = getFCurves(obj)
    for fcurve in arrFcurves:
        if fcurve.data_path == strPath:
            for keyframe_point in fcurve.keyframe_points:
                if mode == '<' and keyframe_point.co.x < intFrame:
                    arrFrames.append(keyframe_point.co.x)
                elif mode == '>' and keyframe_point.co.x > intFrame:
                    arrFrames.append(keyframe_point.co.x)
            break
    if len(arrFrames) > intCount:
        if mode == '<':
            arrFrames = arrFrames[-intCount]
            # reverse the array
            arrFrames = arrFrames[::-1]
        elif mode == '>':
            arrFrames = arrFrames[0:intCount]
    return arrFrames
