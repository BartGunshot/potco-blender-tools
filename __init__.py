bl_info = {
    "name": "POTCO Blender Tools",
    "author": "Bart Gunshot",
    "version": (0, 3),
    "blender": (2, 80, 0),
    "location": "",
    "description": "Various tooling for working with POTCO model files.",
    "warning": "Early development. Use with caution",
    "category": "General",
}

import bpy
import importlib, os, sys, math

from bpy_extras.io_utils import ImportHelper
from . import compatibility

blender_path = os.path.realpath(__file__).removesuffix('\__init__.py')
sys.path.append(os.path.join(blender_path))

@compatibility.make_annotations
class IMPORT_OT_worlddata(bpy.types.Operator, ImportHelper):
    """Operator to import POTCO worlddata should be .py"""
    # Setup some generic blender fields
    bl_idname = "import_scene.worldata"
    bl_label = "Import worlddata.py"
    bl_description = "Import a POTCO WorldData file (.py)"
    bl_options = {'REGISTER', 'UNDO'}
    
    # This makes sure by default can only import .py
    filename_ext = ".py"
    filter_glob = bpy.props.StringProperty(default="*.py", options={'HIDDEN'})
    
    # Two fields for setting up directory and files that were selected
    directory = bpy.props.StringProperty(name="Directory", options={'HIDDEN'})
    files = bpy.props.CollectionProperty(type=bpy.types.OperatorFileListElement, options={'HIDDEN'})
    
    # This will check for he blender egg importer by rdb, if it is found then we add option to import models from .egg
    #       if not found then we will notify the user. Should then try and find .blend files instead.

    load_egg = bpy.props.BoolProperty(name="Load from .egg", description="Loads model files from .egg extentions. Requires blender-egg-importer.")
    use_uid = bpy.props.BoolProperty(name="Use uid", description="Names objects based on UID instead of what they are")

    # This runs after files are selected and opened
    def execute(self, context):
        # Executes a function recursively on every object of the objectStruct
        def traverseWDObjects(root: dict, func, *args, **kwargs):
            for obj in root:
                root[obj] = func(obj, root[obj], *args, **kwargs)

                # get and traverse an object tree if it exists
                subroot = root[obj].get('Objects')
                if subroot:
                    subroot = traverseWDObjects(subroot, func, *args, **kwargs)
                    root[obj]['Objects'] = subroot
            return root

        def loadObjectBlender(name: str, obj: dict):
            # Load models into blender 
            if self.load_egg and obj.get('Visual') and obj.get('Visual').get('Model'):
                # Setup some variables to store parts of the path
                modelpath = ""
                dis_model_path = str(obj['Visual']['Model']).split("/")
                modelname = dis_model_path[-1] 
                
                # The disney model path is stored badly, fix this. 
                for part in dis_model_path[:-1]:
                    modelpath = os.path.join(modelpath, part)
                
                # Setup the variables to pass to the egg importer
                fp = os.path.join(self.directory, modelpath, modelname + ".egg")
                dr = os.path.join(self.directory, modelpath)
                fs=[{"name":modelname+ ".egg", "name":modelname + ".egg"}]
                
                # Search for file in phase_2-5
                phase = 2
                while (not os.path.isfile(fp) and phase < 6):
                    fp = os.path.join(self.directory, "phase_" + str(phase), modelpath, modelname + ".egg")
                    dr =  os.path.join(self.directory, "phase_" + str(phase), modelpath)
                    phase += 1
                
                # Try and run the egg importer to import the model, if failure create a empty as a placeholder
                try:
                    bpy.ops.import_scene.egg(filepath=fp, directory=dr, files=fs)
                except:
                    o = bpy.data.objects.new(name if self.use_uid else modelname + " ERROR!! DID NOT IMPORT", None)
                    bpy.context.scene.collection.objects.link(o)
                    bpy.data.objects[name if self.use_uid else modelname + " ERROR!! DID NOT IMPORT"].select_set(True)
                
                # Iterate over imported model
                for o in bpy.context.selected_objects:
                    o.select_set(False)
                    # Skip if has parent (not root)
                    if o.parent:
                        continue
                    # Apply the transformations
                    if obj.get('Pos'):
                        o.location[0] = obj['Pos'].x
                        o.location[1] = obj['Pos'].y
                        o.location[2] = obj['Pos'].z
                    if obj.get('Scale'):
                        o.scale[0] = obj['Scale'].x
                        o.scale[1] = obj['Scale'].y
                        o.scale[2] = obj['Scale'].z
                    if obj.get('Hpr'):
                        o.rotation_euler[0] = (obj['Hpr'].z / 360) * (2 * math.pi)
                        o.rotation_euler[1] = (obj['Hpr'].y / 360) * (2 * math.pi)
                        o.rotation_euler[2] = (obj['Hpr'].x / 360) * (2 * math.pi)
            else:
                o = bpy.data.objects.new(name if self.use_uid else obj.get('Type') + " No model data given.", None)
                if obj.get('Pos'):
                    o.location[0] = obj['Pos'].x
                    o.location[1] = obj['Pos'].y
                    o.location[2] = obj['Pos'].z
                if obj.get('Scale'):
                    o.scale[0] = obj['Scale'].x
                    o.scale[1] = obj['Scale'].y
                    o.scale[2] = obj['Scale'].z
                if obj.get('Hpr'):
                    o.rotation_euler[0] = (obj['Hpr'].z / 360) * (2 * math.pi)
                    o.rotation_euler[1] = (obj['Hpr'].y / 360) * (2 * math.pi)
                    o.rotation_euler[2] = (obj['Hpr'].x / 360) * (2 * math.pi)
                bpy.context.scene.collection.objects.link(o)
            
            return obj

        for file in self.files:
            sys.path.append(self.directory)
            data = importlib.import_module(file.name.replace('.py', ''))
            sys.path.pop()
            traverseWDObjects(data.objectStruct.get('Objects'), loadObjectBlender)

        return {'FINISHED'}
    
    # This runs when the import option is selected
    def invoke(self, context, event):
        wm = context.window_manager
        wm.fileselect_add(self)
        return {'RUNNING_MODAL'}
    
    # This sets up the options frame in the import window 
    def draw(self, context):
        layout = self.layout
        row = layout.row()
        row.prop(self, "load_egg")
        row.prop(self, "use_uid")

# This is called when the plugin is ran, registers operators
def menu_func(self, context):
    self.layout.operator(IMPORT_OT_worlddata.bl_idname, text="POTCO WorldData (.py) [EXPERIMENTAL]")

# This is called when the plugin is activated
def register():
    bpy.utils.register_class(IMPORT_OT_worlddata)
    
    if bpy.app.version >= (2, 80):
        bpy.types.TOPBAR_MT_file_import.append(menu_func)
    else:
        bpy.types.INFO_MT_file_import.append(menu_func)

# This is called when the plugin is deactivated 
def unregister():
    if bpy.app.version >= (2, 80):
        bpy.types.TOPBAR_MT_file_import.remove(menu_func)
    else:
        bpy.types.INFO_MT_file_import.remove(menu_func)
    
    bpy.utils.unregister_class(IMPORT_OT_worlddata)

if __name__ == "__main__":
    register()
