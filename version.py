import bpy
import requests
import json
import textwrap

URL = 'https://anthonyaragues.com/stopmotion_check.json'
PREFIX = 'key'


class KEY_Preferences(bpy.types.AddonPreferences):
    bl_idname = __package__

    json_message: bpy.props.StringProperty(
        name="",
        default=json.dumps(objDefault)
    )


class KEY_OT_Hide_Version(bpy.types.Operator):
    bl_idname = f'{PREFIX}.hide_version_panel'
    bl_label = "x"
    bl_description = "Dismiss this version"

    def execute(self, context):
        objPreferences = getPreferences()
        objPreferences["hide_version"] = True
        setPreferences(objPreferences)
        return {'FINISHED'}


class KEY_OT_Hide_Message(bpy.types.Operator):
    bl_idname = f'{PREFIX}.hide_message_panel'
    bl_label = "x"
    bl_description = "Dismiss this message"

    def execute(self, context):
        objPreferences = getPreferences()
        objPreferences["hide_message"] = True
        setPreferences(objPreferences, True)
        return {'FINISHED'}


def getIntVersion(strVersion):
    # expects bl_info as a string str(bl_info["version"])
    strVersion = strVersion.replace(",", ".").replace(")", "").replace("(", "")
    return int(strVersion.replace(".", "").replace(" ", ""))


def getPreferences():
    objPreferences = None
    if bpy.context.preferences.addons[__package__].preferences.json_message != "":
        try:
            objPreferences = json.loads(
                bpy.context.preferences.addons[__package__].preferences.json_message)
        except:
            pass
    return objPreferences


def setPreferences(objPreferences, saveMe=False):
    bpy.context.preferences.addons[__package__].preferences.json_message = json.dumps(
        objPreferences)
    if saveMe == True:
        bpy.ops.wm.save_userpref()


def check_version(bl_info):
    objResponse = None
    objVersion = None
    objPreference = getPreferences()
    try:
        objResponse = requests.get(URL)
    except:
        pass
    if objResponse and objResponse.status_code == 200:
        try:
            objVersion = json.loads(objResponse.text)
        except:
            pass
        if objVersion is not None:
            if getIntVersion(objVersion["version"]) > getIntVersion(str(bl_info["version"])):
                if getIntVersion(objVersion["version"]) > getIntVersion(objPreference["version"]):
                    objVersion["hide_version"] = False
                else:
                    objVersion["hide_version"] = objPreference["hide_version"]
            else:
                objVersion["hide_version"] = True
            if objVersion["message"] != objPreference["message"]:
                objVersion["hide_message"] = False
            else:
                objVersion["hide_message"] = objPreference["hide_message"]
    setPreferences(objVersion)


def getTextArray(context, text):
    intWidth = int(context.region.width)-30
    chars = intWidth / 7   # 7 pix on 1 character
    wrapper = textwrap.TextWrapper(width=chars)
    return wrapper.wrap(text=text)


def draw_version_box(objPanel, context):
    # ---------------  VERSION CHECK PANEL -----------------
    objVersion = None
    layout = objPanel.layout
    if context.preferences.addons[__package__].preferences.json_message != "":
        objVersion = json.loads(
            context.preferences.addons[__package__].preferences.json_message)
    if objVersion is not None and "hide_version" in objVersion.keys() and objVersion["hide_version"] != True:
        box = layout.box()
        row = box.row(align=True)
        row.alignment = 'EXPAND'
        row.label(icon="INFO", text=objVersion["ver_message"])
        # uncomment to let user dismiss till version changes
        # row.operator(f'{PREFIX}.hide_version_panel', text="", icon="X")
        row = box.row()
        row.operator(
            'wm.url_open', text="Blender Market", icon="URL").url = objVersion["bm_url"]
        row = box.row()
        row.operator(
            'wm.url_open', text="GumRoad", icon="URL").url = objVersion["gm_url"]
    if objVersion is not None and "hide_message" in objVersion.keys() and objVersion["hide_message"] != True:
        box = layout.box()
        arrText = getTextArray(context, objVersion["message"])
        for i, strText in enumerate(arrText):
            row = box.row()
            row.label(text=strText)
            if i == 0:
                row.operator(f'{PREFIX}.hide_message_panel', text="", icon="X")
        if objVersion["url"] != "":
            row = box.row(align=True)
            row.operator(
                'wm.url_open', text=objVersion["btn_name"], icon="URL").url = objVersion["url"]


arrClasses = [
    KEY_Preferences,
    KEY_OT_Hide_Version,
    KEY_OT_Hide_Message
]


def register(bl_info):
    for i in arrClasses:
        bpy.utils.register_class(i)
    check_version(bl_info)


def unregister():
    for i in reversed(arrClasses):
        bpy.utils.unregister_class(i)
