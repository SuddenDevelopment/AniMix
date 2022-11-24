import bpy
import config
from . import keyframes


def getOnionCollection(strCollection, strParent=None):
    if strCollection in bpy.data.collections:
        print(f'collection: {strCollection} already exists')
    else:
        objCollection = bpy.data.collections.new(name=strCollection)
        if strParent != None:
            bpy.data.collections[strParent].children.link(objCollection)
        else:
            print("no parent for: "+strCollection)


def setOnionSkinObject(intGroup, intObject, intDistance, mode):
    strName = f'{config.PREFIX}_{intGroup}_{intObject}'


def setOnionSkins(obj, intFrame, mode, intCount):
    strPath = '["key_object_id"]'
    intGroup = obj.get("key_id")
    arrFrames = keyframes.getFrames(
        obj, strPath, intFrame, intCount, '<')
    for i, frame in arrFrames:
        intObject = keyframes.getKeyframeValue(obj, strPath, frame, mode)
        setOnionSkinObject(intGroup, intObject, i, '<')
    arrFrames = keyframes.getFrames(
        obj, strPath, intFrame, intCount, '>')
    for i, frame in arrFrames:
        intObject = keyframes.getKeyframeValue(obj, strPath, frame, mode)
        setOnionSkinObject(intGroup, intObject, i, '>')
