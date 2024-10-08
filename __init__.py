bl_info = {
    "name": "InstanceHarvestor",
    "author": "BlockyBard",
    "version": (0, 4),
    "blender": (2, 90, 0),
    "location": "View3D > Object > Relink Duplicates",
    "description": "Relinks duplicated objects based on mesh signature",
    "category": "Object",
}

import bpy
from collections import defaultdict

def get_mesh_signature(mesh):
    return (len(mesh.vertices), len(mesh.edges), len(mesh.polygons))

def get_material_signature(obj):
    """Return a tuple representing the materials of the object."""
    return tuple(obj.data.materials)

def relink_duplicates(operate_on_selected=False, match_material=True):
    signature_groups = defaultdict(list)
    relinked_count = 0
    
    # Filter objects based on the selected option
    objects = bpy.context.selected_objects if operate_on_selected else bpy.context.scene.objects
    
    # Group objects by their mesh signature and optionally materials
    for obj in objects:
        if obj.type == 'MESH':
            mesh_signature = get_mesh_signature(obj.data)
            if match_material:
                # Add material signature to the group key
                material_signature = get_material_signature(obj)
                signature_groups[(mesh_signature, material_signature)].append(obj)
            else:
                signature_groups[mesh_signature].append(obj)
    
    # Process each group
    for group_key, objects in signature_groups.items():
        if len(objects) > 1:
            # Sort objects by name
            sorted_objects = sorted(objects, key=lambda obj: obj.name)
            
            reference_obj = sorted_objects[0]
            
            # Relink all other objects in the group to the reference object
            for obj in sorted_objects[1:]:
                if obj.data != reference_obj.data:
                    obj.data = reference_obj.data
                    relinked_count += 1
                    print(f"Relinked {obj.name} to use {reference_obj.name}'s data")

    return relinked_count

class OBJECT_OT_relink_duplicates(bpy.types.Operator):
    bl_idname = "object.relink_duplicates"
    bl_label = "Relink Duplicates"
    bl_options = {'REGISTER', 'UNDO'}
    
    # Property for selected objects only option
    operate_on_selected: bpy.props.BoolProperty(
        name="Operate on Selected",
        description="Only relink duplicates among selected objects",
        default=False
    )

    # Property for matching materials option
    match_material: bpy.props.BoolProperty(
        name="Match Materials",
        description="Check if materials match before relinking",
        default=True
    )

    def execute(self, context):
        relinked_count = relink_duplicates(self.operate_on_selected, self.match_material)
        self.report({'INFO'}, f"Relinked {relinked_count} duplicate objects.")
        return {'FINISHED'}

def menu_func(self, context):
    self.layout.operator(OBJECT_OT_relink_duplicates.bl_idname)

def register():
    bpy.utils.register_class(OBJECT_OT_relink_duplicates)
    bpy.types.VIEW3D_MT_object.append(menu_func)

def unregister():
    bpy.utils.unregister_class(OBJECT_OT_relink_duplicates)
    bpy.types.VIEW3D_MT_object.remove(menu_func)

if __name__ == "__main__":
    register()
