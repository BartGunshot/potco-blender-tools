bl_info = {
    "name": "POTCO Blender Tools",
    "author": "Bart Gunshot",
    "version": (0, 2),
    "blender": (2, 80, 0),
    "location": "",
    "description": "Various tooling for working with POTCO model files.",
    "warning": "Early development. Use with caution",
    "category": "General",
}

import bpy
import imp

import os.path
import bpy.types
from bpy import props
from bpy_extras.io_utils import ImportHelper

class IMPORT_OT_worlddata(bpy.types.Operator, ImportHelper):
    """Operator to import POTCO worlddata should be .py"""
    # Setup some generic blender fields
    bl_idname = "import_scene.worldata"
    bl_label = "Import worlddata.py"
    bl_description = "Import a POTCO WorldData file (.py)"
    bl_options = {'REGISTER', 'UNDO'}
    
    # This makes sure by default can only import .py
    filename_ext = ".py"
    filter_glob = props.StringProperty(default="*.py", options={'HIDDEN'})
    
    # Two fields for setting up directory and files that were selected
    directory = props.StringProperty(name="Directory", options={'HIDDEN'})
    files = props.CollectionProperty(type=bpy.types.OperatorFileListElement, options={'HIDDEN'})
    
    # This will check for he blender egg importer by rdb, if it is found then we add option to import models from .egg
    #       if not found then we will notify the user. Should then try and find .blend files instead.
    try:
        bpy.ops.import_scene.egg()
        load_egg = props.BoolProperty(name="Load from .egg", description="Loads model files from .egg extentions. Requires blender-egg-importer.")
    except AttributeError:
        load_egg = False
        print("blender-egg-importer not installed.")
    
    load_egg = True

    # This runs after files are selected and opened
    def execute(self, context):
        def IterateWorldData(objectStruct):
            """Recusively parses worlddata and loads it in."""
            # I'm sorry this is absolutely disgusting. TODO: remove exec and eval calls and write a proper parser
            for objID in objectStruct['ObjectIds']:
                code = 'objectStruct' + objectStruct['ObjectIds'][objID]
                obj = eval(code)
                
                # AdditionalData has additional worlddata files the object may contain
                if obj.get('AdditionalData'):
                    for filename in obj['AdditionalData']:
                        #OPEN THIS FILE AND ITERATE OVER IT'S OBJECT STRUCT RECURSIVELY
                            path = os.path.join(self.directory, filename + ".py")
                            data = imp.load_source(filename, path)
                            IterateWorldData(data.objectStruct)
                
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
                        o = bpy.data.objects.new(modelname + " ERROR!! DID NOT IMPORT", None)
                        bpy.context.scene.collection.objects.link(o)
                        bpy.data.objects[modelname + " ERROR!! DID NOT IMPORT"].select_set(True)
                    
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
                            pi = 22.0/7.0
                            o.rotation_euler[0] = (obj['Hpr'].z / 360) * (2 * pi)
                            o.rotation_euler[1] = (obj['Hpr'].y / 360) * (2 * pi)
                            o.rotation_euler[2] = (obj['Hpr'].x / 360) * (2 * pi)
                else:
                    o = bpy.data.objects.new(obj.get('Type') + " No model data given.", None)
                    bpy.context.scene.collection.objects.link(o)

        for file in self.files:
            path = os.path.join(self.directory, file.name)
            data = imp.load_source(file.name.replace(".py", ""), path)
            IterateWorldData(data.objectStruct)
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
