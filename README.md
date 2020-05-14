# POTCO Blender Tools
This is a Blender addon which provides a number of tools for working with POTCO files in blender. Tested with 2.8, will probably work with 2.79.

## POTCO WorldData Importer
This addon adds in a rudimentary WorldData importer for POTCO WorldData files. These files store the placements of props, scenery, etc. on the various world spaces of POTCO. As of now, the importer will attempt to import Panda3D .egg files located in the same directory as the imported WorldData file. The importer expects the user to have installed: https://github.com/rdb/blender-egg-importer 

*File > Import > POTCO WorldData (.py)*

The worldData files are found in any src rip of POTCO. I recommend this one for this instance:
https://github.com/PiratesOnlineRewritten/Pirates-Online-Rewritten/tree/master/pirates/leveleditor/worldData

#### Issues:
- Caves don't load properly
- The larger worlddata files take a very long time to import

#### TODO:
- Write a proper parser for reading worlddata
- Preserve object properties 
- Preserve object hierarchy
- Support links
- Performance improvements
