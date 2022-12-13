def getFCurves(obj, inDataBlock=False):
    arrFCurves = []
    if inDataBlock == False and hasattr(obj, 'animation_data') == True and obj.animation_data != None:
        arrFCurves = obj.animation_data.action.fcurves
    if inDataBlock == True and hasattr(obj.data, 'animation_data') == True and obj.data.animation_data != None:
        arrFCurves = obj.data.animation_data.action.fcurves
    return arrFCurves


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


def removeKeyframes(obj, strPath):
    arrFcurves = getFCurves(obj)
    for fcurve in arrFcurves:
        if fcurve.data_path == strPath:
            obj.animation_data.action.fcurves.remove(fcurve)


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
