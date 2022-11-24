def getKeyframeValue(obj, strPath, intFrame, mode):
    intFrameId = None
    if hasattr(obj, 'animation_data') == True and hasattr(obj.animation_data, 'action'):
        for fcurve in obj.animation_data.action.fcurves:
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
                break
    if intFrameId != None:
        intFrameId = int(intFrameId)
    return intFrameId


def removeKeyframes(obj, strPath):
    if hasattr(obj, 'animation_data') == True and hasattr(obj.animation_data, 'action'):
        for fcurve in obj.animation_data.action.fcurves:
            if fcurve.data_path == strPath:
                obj.animation_data.action.fcurves.remove(fcurve)


def getFrames(obj, strPath, intFrame, intCount, mode):
    arrFrames = []
    if hasattr(obj, 'animation_data') == True and hasattr(obj.animation_data, 'action'):
        for fcurve in obj.animation_data.action.fcurves:
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
