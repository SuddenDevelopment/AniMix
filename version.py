import bpy
import requests
import json

URL = 'https://anthonyaragues.com/stopmotion_check.json'
PROP = 'KEY_message'


def getIntVersion(strVersion):
    # expects blinfo as a string str(bl_info["version"])
    strVersion = strVersion.replace(",", ".").replace(")", "").replace("(", "")
    return int(strVersion.replace(".", "").replace(" ", ""))


def show_message(msg, bl_info):
    print(f'{bl_info["name"]}: {msg}')
    try:
        # set as window manager because scene isnt there yet and window is more appropriate level
        setattr(bpy.context.window_manager, PROP, msg)
    except:
        pass


def check_version(bl_info):
    # example response
    # { "version": 1.4.0, "message": "upgrade for these new features" }
    objResponse = requests.get(URL)
    if objResponse.status_code == 200:
        objVersion = json.loads(objResponse.text)
        intCurrent = getIntVersion(objVersion["version"])
        intInstalled = getIntVersion(str(bl_info["version"]))
        if intCurrent > intInstalled:
            # print(f'version: {intInstalled} < {intCurrent}')
            show_message(
                f'{objVersion["message"]} {objVersion["version"]}', bl_info)
    else:
        show_message("couldn't check version", bl_info)
