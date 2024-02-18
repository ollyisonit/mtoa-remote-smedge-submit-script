import subprocess
from pathlib import Path, WindowsPath, PurePath
import shutil
import argparse
import tempfile
import sys
import zipfile
import os
import maya.cmds
import maya.mel
import winsound
import glob

INPUT_LOCATION = r"W:\WhittledDown\WhittledDownMaya"
OUTPUT_LOCATION = r'R:\_RENDERING\ProjectMirror'
OUTPUT_PROJECT_LOCATION = r'R:\_RENDERING\ProjectMirror\WhittledDownMaya'
RENDER_STORE_LOCATION = r'R:\_RENDERING\ProjectMirror\RENDER_OUT'
ALERT_SOUND = r'R:\_RENDERING\RENDERSOUND.wav'
MAYA_PATH = WindowsPath(r'C:\Program Files\Autodesk\Maya2023\bin\mayabatch.exe')
RENDER_LAYERS = ["Carliar_Reference", "Scene_3D_Beauty", "Scene_3D_AOVs"]

def find_project(start_dir: Path) -> Path:
    cur_dir = start_dir
    while len(cur_dir.parents) > 0:
        if cur_dir.joinpath('workspace.mel').exists():
            return cur_dir
        cur_dir = cur_dir.parent
    raise Exception("Maya project not found!")

def find(f, seq):
  """Return first item in sequence where f(item) == True."""
  for item in seq:
    if f(item): 
      return item

def package_project(SCENE_PATH: Path, OUTPUT_PATH: Path, replace: bool):
    PROJECT_PATH = find_project(SCENE_PATH)

    print('Updating project...')
    os.system(fr'robocopy "{INPUT_LOCATION}" "{OUTPUT_PROJECT_LOCATION}" /XO /MIR /xd autosave /xd incrementalSave /xd images')
    #subprocess.Popen(fr'"{INPUT_LOCATION}" "{OUTPUT_PROJECT_LOCATION}" /XO /MIR /xd autosave /xd incrementalSave /xd images').wait()

    #final_output = OUTPUT_PATH.joinpath(SCENE_PATH.name)

    # output_scene = find(lambda path: path.is_file(), list(OUTPUT_PATH.glob(f"**/{SCENE_PATH.name}")))
    # if output_scene == None:
    #     raise Exception("Couldn't find output scene!")

    scene_path_from_project = os.path.relpath(SCENE_PATH, PROJECT_PATH)
    
    start_frame = int(maya.cmds.getAttr('defaultRenderGlobals.startFrame'))
    end_frame = int(maya.cmds.getAttr('defaultRenderGlobals.endFrame'))
    render_prefix = maya.cmds.getAttr('defaultRenderGlobals.imageFilePrefix')
    rendername = render_prefix
    if rendername == None:
        rendername = ""
    rendername = rendername.replace('<Scene>', SCENE_PATH.name)
    if rendername == "":
        rendername = SCENE_PATH.name
    
    for render_layer in RENDER_LAYERS:
        packetsize = 1
        if render_layer == "Carliar_Reference":
            packetsize = 10
        if render_layer == "Scene_3D_AOVs":
            packetsize = 20
        
        with open(OUTPUT_PATH.joinpath(f'{rendername}_{render_layer.upper()}_SmedgeSettings.sj'), 'w') as smedge_config:
            config_contents = f'''[4c8e3273-5d60-4d68-af28-23799ab7134c]
            ID = 4c8e3273-5d60-4d68-af28-23799ab7134c
            Type = 833c1fa9-fc0b-46da-920a-c4b74b92d5c1
            Name = {rendername}_{render_layer.upper()}
            Project = {OUTPUT_PROJECT_LOCATION}
            Scene = {os.path.join(OUTPUT_PROJECT_LOCATION, scene_path_from_project)}
            RenderDir = {Path(RENDER_STORE_LOCATION).joinpath(f'{rendername}_render').absolute()}
            Range = {start_frame}-{end_frame}
            Status = 0
            PacketSize = {packetsize}
            FailureLimit = 0
            OvertimeKill = 0
            DistributeMode = 1
            Extra = -ai:txamm no -ai:txaum no -ai:txaun no -ai:txett yes -rl {render_layer}'''
            smedge_config.write(config_contents)
            print(f"Output smedge config: {rendername}_{render_layer.upper()}_SmedgeSettings.sj \n {config_contents}")
    
    print("Done! Good luck with your render, you're gonna need it.")
    if ALERT_SOUND != None:
        winsound.PlaySound(ALERT_SOUND, winsound.SND_FILENAME | winsound.SND_ASYNC)


package_project(Path(cmds.file(q=True, sn=True)).absolute(), Path(OUTPUT_LOCATION).absolute(), True)

