# SPDX-License-Identifier: GPL-2.0-or-later
import bpy
from bpy.types import AddonPreferences, Operator, Panel
from bpy.props import BoolProperty, StringProperty
from threading import Timer
from bpy.app.handlers import persistent

bl_info = {
    "name": "AnimAll + Auto Key",
    "author": "Daniel Salazar (ZanQdo), Damien Picard (pioverfour), Anthony Aragues (autokey functionality)",
    "version": (1, 0, 4),
    "blender": (3, 2, 0),
    "location": "3D View > Toolbox > Animation tab > AnimAll",
    "description": "Allows animation of mesh, lattice, curve and surface data",
    "warning": "",
    "doc_url": "{BLENDER_MANUAL_URL}/addons/animation/animall.html",
    "category": "Animation",
}


# Property Definitions
class AnimallProperties(bpy.types.PropertyGroup):
    key_selected: BoolProperty(
        name="Key Selected Only",
        description="Insert keyframes only on selected elements",
        default=False)
    key_autokey: BoolProperty(
        name="AutoKey",
        description="Allow AutoKey to use AnimAll on changes",
        default=True)

    # Generic attributes
    key_point_location: BoolProperty(
        name="Location",
        description="Insert keyframes on point locations",
        default=True)
    key_shape_key: BoolProperty(
        name="Shape Key",
        description="Insert keyframes on active Shape Key layer",
        default=False)
    key_material_index: BoolProperty(
        name="Material Index",
        description="Insert keyframes on face material indices",
        default=False)

    # Mesh attributes
    key_vertex_bevel: BoolProperty(
        name="Vertex Bevel",
        description="Insert keyframes on vertex bevel weight",
        default=False)
    # key_vertex_crease: BoolProperty(
    #     name="Vertex Crease",
    #     description="Insert keyframes on vertex crease weight",
    #     default=False)
    key_vertex_group: BoolProperty(
        name="Vertex Group",
        description="Insert keyframes on active vertex group values",
        default=False)

    key_edge_bevel: BoolProperty(
        name="Edge Bevel",
        description="Insert keyframes on edge bevel weight",
        default=False)
    key_edge_crease: BoolProperty(
        name="Edge Crease",
        description="Insert keyframes on edge creases",
        default=False)

    key_attribute: BoolProperty(
        name="Attribute",
        description="Insert keyframes on active attribute values",
        default=False)
    key_uvs: BoolProperty(
        name="UVs",
        description="Insert keyframes on active UV coordinates",
        default=False)

    # Curve and surface attributes
    key_radius: BoolProperty(
        name="Radius",
        description="Insert keyframes on point radius (Shrink/Fatten)",
        default=False)
    key_tilt: BoolProperty(
        name="Tilt",
        description="Insert keyframes on point tilt",
        default=False)


# Utility functions

def refresh_ui_keyframes():
    try:
        for area in bpy.context.screen.areas:
            if area.type in ('TIMELINE', 'GRAPH_EDITOR', 'DOPESHEET_EDITOR'):
                area.tag_redraw()
    except:
        pass


def insert_key(data: bpy.types.bpy_struct, key, group=None):
    try:
        if group is not None:
            data.keyframe_insert(key, group=group)
        else:
            data.keyframe_insert(key)
    except Exception as e:
        print('key didnt insert for', e)
        pass


def delete_key(data, key):
    try:
        data.keyframe_delete(key)
    except:
        pass


def is_selected_vert_loop(data, loop_i):
    """Get selection status of vertex corresponding to a loop"""
    vertex_index = data.loops[loop_i].vertex_index
    return data.vertices[vertex_index].select


# GUI (Panel)

class VIEW3D_PT_animall(Panel):
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = "Animate"
    bl_label = 'AnimAll'
    bl_idname = "VIEW3D_PT_animall"

    @classmethod
    def poll(self, context):
        return context.active_object and context.active_object.type in {'MESH', 'LATTICE', 'CURVE', 'SURFACE'}

    def draw(self, context):
        obj = context.active_object
        animall_properties = context.scene.animall_properties

        layout = self.layout

        layout.use_property_split = True
        layout.use_property_decorate = False

        split = layout.split(factor=0.4, align=True)
        split.label(text='')
        split.label(text='     Key:')

        if obj.type == 'LATTICE':
            col = layout.column(align=True)
            col.prop(animall_properties, "key_point_location")
            col.prop(animall_properties, "key_shape_key")

        elif obj.type == 'MESH':
            col = layout.column(heading="Points", align=True)
            col.prop(animall_properties, "key_point_location")
            col.prop(animall_properties, "key_vertex_bevel", text="Bevel")
            col.prop(animall_properties, "key_vertex_group",
                     text="Vertex Groups")

            col = layout.column(heading="Edges", align=True)
            col.prop(animall_properties, "key_edge_bevel", text="Bevel")
            col.prop(animall_properties, "key_edge_crease", text="Crease")

            col = layout.column(heading="Faces", align=True)
            col.prop(animall_properties, "key_material_index")

            col = layout.column(heading="Others", align=True)
            col.prop(animall_properties, "key_attribute")
            col.prop(animall_properties, "key_uvs")
            col.prop(animall_properties, "key_shape_key")

            # Vertex group update operator
            if (obj.data.animation_data is not None
                    and obj.data.animation_data.action is not None):
                for fcurve in context.active_object.data.animation_data.action.fcurves:
                    if fcurve.data_path.startswith("vertex_colors"):
                        col = layout.column(align=True)
                        col.label(
                            text="Object includes old-style vertex colors. Consider updating them.", icon="ERROR")
                        col.operator(
                            "anim.update_vertex_color_animation_animall", icon="FILE_REFRESH")
                        break

        elif obj.type in {'CURVE', 'SURFACE'}:
            col = layout.column(align=True)
            col.prop(animall_properties, "key_point_location")
            col.prop(animall_properties, "key_radius")
            col.prop(animall_properties, "key_tilt")
            col.prop(animall_properties, "key_material_index")
            col.prop(animall_properties, "key_shape_key")

        if animall_properties.key_shape_key:
            shape_key = obj.active_shape_key
            shape_key_index = obj.active_shape_key_index

            if shape_key_index > 0:
                col = layout.column(align=True)
                row = col.row(align=True)
                row.prop(shape_key, "value", text=shape_key.name,
                         icon="SHAPEKEY_DATA")
                row.prop(obj, "show_only_shape_key", text="")
                if shape_key.value < 1:
                    col.label(text='Maybe set "%s" to 1.0?' %
                              shape_key.name, icon="INFO")
            elif shape_key is not None:
                col = layout.column(align=True)
                col.label(text="Cannot key on Basis Shape", icon="ERROR")
            else:
                col = layout.column(align=True)
                col.label(text="No active Shape Key", icon="ERROR")

            if animall_properties.key_point_location:
                col.label(
                    text='"Location" and "Shape Key" are redundant?', icon="INFO")

        col = layout.column(align=True)
        col.prop(animall_properties, "key_selected")
        col.prop(animall_properties, "key_autokey")

        # row = layout.row(align=True)
        # row.operator("anim.insert_keyframe_animall", icon="KEY_HLT")
        # row.operator("anim.delete_keyframe_animall", icon="KEY_DEHLT")
        # row = layout.row()
        # row.operator("anim.clear_animation_animall", icon="CANCEL")


def getSelectedObjects(context):
    # a little more robust object selection to support different modes by Anthony Aragues
    # arrObjects = getSelectedObjects(context)
    arrObjects = []
    if context.mode == 'OBJECT':
        if hasattr(context, 'selected_objects'):
            arrObjects = context.selected_objects
        if len(arrObjects) == 0 and hasattr(context, 'active_object'):
            arrObjects.append(context.active_object)
        if len(arrObjects) == 0:
            for obj in context.scene.objects:
                if obj.select_get() == True:
                    arrObjects.append(obj)
    else:
        arrObjects = context.objects_in_mode_unique_data[:]
    if len(arrObjects) == 0:
        print('no objects found to work with for animall+autokey')
    return arrObjects


def insert_keyframe_animall_execute(context, skip_shapekeys=False):
    bpy.context.window_manager.KEY_state = 'ANIMALL'
    animall_properties = context.scene.animall_properties

    if context.mode == 'OBJECT':
        objects = context.selected_objects
    else:
        objects = context.objects_in_mode_unique_data[:]
    mode = context.object.mode

    for obj in [o for o in objects if o.type in {'CURVE', 'SURFACE', 'LATTICE'}]:
        data = obj.data
        if obj.type == 'LATTICE':
            if animall_properties.key_shape_key:
                if obj.active_shape_key_index > 0:
                    sk_name = obj.active_shape_key.name
                    for p_i, point in enumerate(obj.active_shape_key.data):
                        if not animall_properties.key_selected or data.points[p_i].select:
                            insert_key(point, 'co', group="%s Point %s" %
                                       (sk_name, p_i))
            if animall_properties.key_point_location:
                for p_i, point in enumerate(data.points):
                    if not animall_properties.key_selected or point.select:
                        insert_key(point, 'co_deform',
                                   group="Point %s" % p_i)
        else:
            if animall_properties.key_material_index:
                for s_i, spline in enumerate(data.splines):
                    if (not animall_properties.key_selected
                            or any(point.select for point in spline.points)
                            or any(point.select_control_point for point in spline.bezier_points)):
                        insert_key(spline, 'material_index',
                                   group="Spline %s" % s_i)
            for s_i, spline in enumerate(data.splines):
                if spline.type == 'BEZIER':
                    for v_i, CV in enumerate(spline.bezier_points):
                        if (not animall_properties.key_selected
                                or CV.select_control_point
                                or CV.select_left_handle
                                or CV.select_right_handle):
                            if animall_properties.key_point_location:
                                # print('insert key for curve')
                                insert_key(
                                    CV, 'co', group="Spline %s CV %s" % (s_i, v_i))
                                insert_key(CV, 'handle_left',
                                           group="Spline %s CV %s" % (s_i, v_i))
                                insert_key(CV, 'handle_right',
                                           group="Spline %s CV %s" % (s_i, v_i))
                            if animall_properties.key_radius:
                                insert_key(
                                    CV, 'radius', group="Spline %s CV %s" % (s_i, v_i))
                            if animall_properties.key_tilt:
                                insert_key(
                                    CV, 'tilt', group="Spline %s CV %s" % (s_i, v_i))
                elif spline.type in ('POLY', 'NURBS'):
                    for v_i, CV in enumerate(spline.points):
                        if not animall_properties.key_selected or CV.select:
                            if animall_properties.key_point_location:
                                insert_key(
                                    CV, 'co', group="Spline %s CV %s" % (s_i, v_i))
                            if animall_properties.key_radius:
                                insert_key(
                                    CV, 'radius', group="Spline %s CV %s" % (s_i, v_i))
                            if animall_properties.key_tilt:
                                insert_key(
                                    CV, 'tilt', group="Spline %s CV %s" % (s_i, v_i))
    bpy.ops.object.mode_set(mode='OBJECT')
    for obj in [o for o in objects if o.type in {'MESH', 'CURVE', 'SURFACE'}]:
        data = obj.data
        if obj.type == 'MESH':
            if animall_properties.key_point_location:
                for v_i, vert in enumerate(data.vertices):
                    if not animall_properties.key_selected or vert.select:
                        insert_key(vert, 'co', group="Vertex %s" % v_i)
            if animall_properties.key_vertex_bevel:
                for v_i, vert in enumerate(data.vertices):
                    if not animall_properties.key_selected or vert.select:
                        insert_key(vert, 'bevel_weight',
                                   group="Vertex %s" % v_i)
            if animall_properties.key_vertex_group:
                for v_i, vert in enumerate(data.vertices):
                    if not animall_properties.key_selected or vert.select:
                        for group in vert.groups:
                            insert_key(group, 'weight',
                                       group="Vertex %s" % v_i)
            if animall_properties.key_edge_bevel:
                for e_i, edge in enumerate(data.edges):
                    if not animall_properties.key_selected or edge.select:
                        insert_key(edge, 'bevel_weight',
                                   group="Edge %s" % e_i)
            if animall_properties.key_edge_crease:
                for e_i, edge in enumerate(data.edges):
                    if not animall_properties.key_selected or edge.select:
                        insert_key(edge, 'crease',
                                   group="Edge %s" % e_i)
            if animall_properties.key_material_index:
                for p_i, polygon in enumerate(data.polygons):
                    if not animall_properties.key_selected or polygon.select:
                        insert_key(polygon, 'material_index',
                                   group="Face %s" % p_i)
            if animall_properties.key_attribute:
                if data.attributes.active is not None:
                    attribute = data.attributes.active
                    if attribute.data_type != 'STRING':
                        # Cannot animate string attributes?
                        if attribute.data_type in {'FLOAT', 'INT', 'BOOLEAN', 'INT8'}:
                            attribute_key = "value"
                        elif attribute.data_type in {'FLOAT_COLOR', 'BYTE_COLOR'}:
                            attribute_key = "color"
                        elif attribute.data_type in {'FLOAT_VECTOR', 'FLOAT2'}:
                            attribute_key = "vector"
                        if attribute.domain == 'POINT':
                            group = "Vertex %s"
                        elif attribute.domain == 'EDGE':
                            group = "Edge %s"
                        elif attribute.domain == 'FACE':
                            group = "Face %s"
                        elif attribute.domain == 'CORNER':
                            group = "Loop %s"
                        for e_i, _attribute_data in enumerate(attribute.data):
                            if (not animall_properties.key_selected
                                    or attribute.domain == 'POINT' and data.vertices[e_i].select
                                    or attribute.domain == 'EDGE' and data.edges[e_i].select
                                    or attribute.domain == 'FACE' and data.polygons[e_i].select
                                    or attribute.domain == 'CORNER' and is_selected_vert_loop(data, e_i)):
                                insert_key(data, f'attributes["{attribute.name}"].data[{e_i}].{attribute_key}',
                                           group=group % e_i)
            if animall_properties.key_uvs:
                if data.uv_layers.active is not None:
                    for uv_i, uv in enumerate(data.uv_layers.active.data):
                        if not animall_properties.key_selected or uv.select:
                            insert_key(uv, 'uv', group="UV layer %s" % uv_i)
            if animall_properties.key_shape_key:
                if obj.active_shape_key_index > 0:
                    sk_name = obj.active_shape_key.name
                    for v_i, vert in enumerate(obj.active_shape_key.data):
                        if not animall_properties.key_selected or data.vertices[v_i].select:
                            insert_key(vert, 'co', group="%s Vertex %s" %
                                       (sk_name, v_i))
        elif obj.type in {'CURVE', 'SURFACE'}:
            # Shape key keys have to be inserted in object mode for curves...
            if animall_properties.key_shape_key:
                sk_name = obj.active_shape_key.name
                global_spline_index = 0  # numbering for shape keys, which have flattened indices
                for s_i, spline in enumerate(data.splines):
                    if spline.type == 'BEZIER':
                        for v_i, CV in enumerate(spline.bezier_points):
                            if (not animall_properties.key_selected
                                    or CV.select_control_point
                                    or CV.select_left_handle
                                    or CV.select_right_handle):
                                if obj.active_shape_key_index > 0:
                                    CV = obj.active_shape_key.data[global_spline_index]
                                    insert_key(CV, 'co', group="%s Spline %s CV %s" % (
                                        sk_name, s_i, v_i))
                                    insert_key(CV, 'handle_left', group="%s Spline %s CV %s" % (
                                        sk_name, s_i, v_i))
                                    insert_key(CV, 'handle_right', group="%s Spline %s CV %s" % (
                                        sk_name, s_i, v_i))
                                    insert_key(CV, 'radius', group="%s Spline %s CV %s" % (
                                        sk_name, s_i, v_i))
                                    insert_key(CV, 'tilt', group="%s Spline %s CV %s" % (
                                        sk_name, s_i, v_i))
                            global_spline_index += 1
                    elif spline.type in ('POLY', 'NURBS'):
                        for v_i, CV in enumerate(spline.points):
                            if not animall_properties.key_selected or CV.select:
                                if obj.active_shape_key_index > 0:
                                    CV = obj.active_shape_key.data[global_spline_index]
                                    insert_key(CV, 'co', group="%s Spline %s CV %s" % (
                                        sk_name, s_i, v_i))
                                    insert_key(CV, 'radius', group="%s Spline %s CV %s" % (
                                        sk_name, s_i, v_i))
                                    insert_key(CV, 'tilt', group="%s Spline %s CV %s" % (
                                        sk_name, s_i, v_i))
                            global_spline_index += 1
    bpy.ops.object.mode_set(mode=mode)
    refresh_ui_keyframes()
    bpy.context.window_manager.KEY_state = ''


class ANIM_OT_insert_keyframe_animall(Operator):
    bl_label = "Insert Key"
    bl_idname = "anim.insert_keyframe_animall"
    bl_description = "Insert a Keyframe"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        insert_keyframe_animall_execute(context)
        return {'FINISHED'}


class ANIM_OT_delete_keyframe_animall(Operator):
    bl_label = "Delete Key"
    bl_idname = "anim.delete_keyframe_animall"
    bl_description = "Delete a Keyframe"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(op, context):
        animall_properties = context.scene.animall_properties

        objects = getSelectedObjects(context)

        mode = context.object.mode

        for obj in objects:
            if mode == 'EDIT':
                obj.update_from_editmode()
            data = obj.data
            if obj.type == 'MESH':
                if animall_properties.key_point_location:
                    for vert in data.vertices:
                        if not animall_properties.key_selected or vert.select:
                            delete_key(vert, 'co')

                if animall_properties.key_vertex_bevel:
                    for vert in data.vertices:
                        if not animall_properties.key_selected or vert.select:
                            delete_key(vert, 'bevel_weight')

                if animall_properties.key_vertex_group:
                    for vert in data.vertices:
                        if not animall_properties.key_selected or vert.select:
                            for group in vert.groups:
                                delete_key(group, 'weight')

                # if animall_properties.key_vcrease:
                #     for vert in data.vertices:
                #         if not animall_properties.key_selected or vert.select:
                #             delete_key(vert, 'crease')

                if animall_properties.key_edge_bevel:
                    for edge in data.edges:
                        if not animall_properties.key_selected or edge.select:
                            delete_key(edge, 'bevel_weight')

                if animall_properties.key_edge_crease:
                    for edge in data.edges:
                        if not animall_properties.key_selected or vert.select:
                            delete_key(edge, 'crease')

                if animall_properties.key_shape_key:
                    if obj.active_shape_key:
                        for v_i, vert in enumerate(obj.active_shape_key.data):
                            if not animall_properties.key_selected or data.vertices[v_i].select:
                                delete_key(vert, 'co')

                if animall_properties.key_uvs:
                    if data.uv_layers.active is not None:
                        for uv in data.uv_layers.active.data:
                            if not animall_properties.key_selected or uv.select:
                                delete_key(uv, 'uv')

                if animall_properties.key_attribute:
                    if data.attributes.active is not None:
                        attribute = data.attributes.active
                        if attribute.data_type != 'STRING':
                            # Cannot animate string attributes?
                            if attribute.data_type in {'FLOAT', 'INT', 'BOOLEAN', 'INT8'}:
                                attribute_key = "value"
                            elif attribute.data_type in {'FLOAT_COLOR', 'BYTE_COLOR'}:
                                attribute_key = "color"
                            elif attribute.data_type in {'FLOAT_VECTOR', 'FLOAT2'}:
                                attribute_key = "vector"

                            for e_i, _attribute_data in enumerate(attribute.data):
                                if (not animall_properties.key_selected
                                        or attribute.domain == 'POINT' and data.vertices[e_i].select
                                        or attribute.domain == 'EDGE' and data.edges[e_i].select
                                        or attribute.domain == 'FACE' and data.polygons[e_i].select
                                        or attribute.domain == 'CORNER' and is_selected_vert_loop(data, e_i)):
                                    delete_key(
                                        data, f'attributes["{attribute.name}"].data[{e_i}].{attribute_key}')

            elif obj.type == 'LATTICE':
                if animall_properties.key_shape_key:
                    if obj.active_shape_key:
                        for point in obj.active_shape_key.data:
                            delete_key(point, 'co')

                if animall_properties.key_point_location:
                    for point in data.points:
                        if not animall_properties.key_selected or point.select:
                            delete_key(point, 'co_deform')

            elif obj.type in {'CURVE', 'SURFACE'}:
                # run this outside the splines loop (only once)
                if animall_properties.key_shape_key:
                    if obj.active_shape_key_index > 0:
                        for CV in obj.active_shape_key.data:
                            delete_key(CV, 'co')
                            delete_key(CV, 'handle_left')
                            delete_key(CV, 'handle_right')

                for spline in data.splines:
                    if spline.type == 'BEZIER':
                        for CV in spline.bezier_points:
                            if (not animall_properties.key_selected
                                    or CV.select_control_point
                                    or CV.select_left_handle
                                    or CV.select_right_handle):
                                if animall_properties.key_point_location:
                                    delete_key(CV, 'co')
                                    delete_key(CV, 'handle_left')
                                    delete_key(CV, 'handle_right')
                                if animall_properties.key_radius:
                                    delete_key(CV, 'radius')
                                if animall_properties.key_tilt:
                                    delete_key(CV, 'tilt')

                    elif spline.type in ('POLY', 'NURBS'):
                        for CV in spline.points:
                            if not animall_properties.key_selected or CV.select:
                                if animall_properties.key_point_location:
                                    delete_key(CV, 'co')
                                if animall_properties.key_radius:
                                    delete_key(CV, 'radius')
                                if animall_properties.key_tilt:
                                    delete_key(CV, 'tilt')

        refresh_ui_keyframes()

        return {'FINISHED'}


class ANIM_OT_clear_animation_animall(Operator):
    bl_label = "Clear Animation"
    bl_idname = "anim.clear_animation_animall"
    bl_description = ("Delete all keyframes for this object\n"
                      "If in a specific case it doesn't work\n"
                      "try to delete the keys manually")
    bl_options = {'REGISTER', 'UNDO'}

    def invoke(self, context, event):
        wm = context.window_manager
        return wm.invoke_confirm(self, event)

    def execute(self, context):
        objects = getSelectedObjects(context)

        for obj in objects:
            try:
                data = obj.data
                data.animation_data_clear()
            except:
                self.report(
                    {'WARNING'}, "Clear Animation could not be performed")
                return {'CANCELLED'}

        refresh_ui_keyframes()

        return {'FINISHED'}


class ANIM_OT_update_vertex_color_animation_animall(Operator):
    bl_label = "Update Vertex Color Animation"
    bl_idname = "anim.update_vertex_color_animation_animall"
    bl_description = "Update old vertex color channel formats from pre-3.3 versions"
    bl_options = {'REGISTER', 'UNDO'}

    @classmethod
    def poll(self, context):
        if (context.active_object is None
                or context.active_object.type != 'MESH'
                or context.active_object.data.animation_data is None
                or context.active_object.data.animation_data.action is None):
            return False
        for fcurve in context.active_object.data.animation_data.action.fcurves:
            if fcurve.data_path.startswith("vertex_colors"):
                return True

    def execute(self, context):
        for fcurve in context.active_object.data.animation_data.action.fcurves:
            if fcurve.data_path.startswith("vertex_colors"):
                fcurve.data_path = fcurve.data_path.replace(
                    "vertex_colors", "attributes")
        return {'FINISHED'}

# Add-ons Preferences Update Panel


# Define Panel classes for updating
panels = [
    VIEW3D_PT_animall
]


# ====|| AUTOKEY FUNCTIONALITY by Anthony Aragues, Adam Earle ||====#
@bpy.app.handlers.persistent
def onAutoKey_handler(scene, depsgraph):
    context = bpy.context
    if scene.animall_properties.key_autokey == True and bpy.context.window_manager.KEY_state == '' and scene.tool_settings.use_keyframe_insert_auto and context.mode.startswith('EDIT_'):
        if hasattr(depsgraph, 'updates'):
            for upd in depsgraph.updates:
                if upd.is_updated_geometry == True:
                    # check whether we're interested in this mesh
                    debounce_action(context)
                    return


DEBOUNCE_TIME = 0.3  # 1/3 second
debounced_action = None


def debounce_action(context):
    """ Print the last message to be invoked within a certain amount of time """
    global debounced_action

    def doWork():
        # autokey feature
        insert_keyframe_animall_execute(context, skip_shapekeys=True)
    if debounced_action:
        debounced_action.cancel()

    debounced_action = Timer(DEBOUNCE_TIME, doWork)
    debounced_action.start()


def register():
    bpy.utils.register_class(AnimallProperties)
    bpy.types.Scene.animall_properties = bpy.props.PointerProperty(
        type=AnimallProperties)
    bpy.utils.register_class(VIEW3D_PT_animall)
    bpy.utils.register_class(ANIM_OT_insert_keyframe_animall)
    bpy.utils.register_class(ANIM_OT_delete_keyframe_animall)
    bpy.utils.register_class(ANIM_OT_clear_animation_animall)
    bpy.utils.register_class(ANIM_OT_update_vertex_color_animation_animall)
    bpy.app.handlers.depsgraph_update_post.append(onAutoKey_handler)


def unregister():
    bpy.app.handlers.depsgraph_update_post.remove(onAutoKey_handler)
    del bpy.types.Scene.animall_properties
    bpy.utils.unregister_class(AnimallProperties)
    bpy.utils.unregister_class(VIEW3D_PT_animall)
    bpy.utils.unregister_class(ANIM_OT_insert_keyframe_animall)
    bpy.utils.unregister_class(ANIM_OT_delete_keyframe_animall)
    bpy.utils.unregister_class(ANIM_OT_clear_animation_animall)
    bpy.utils.unregister_class(ANIM_OT_update_vertex_color_animation_animall)


if __name__ == "__main__":
    register()
