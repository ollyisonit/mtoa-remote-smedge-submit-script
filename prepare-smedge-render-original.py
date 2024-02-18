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

OUTPUT_LOCATION = r'R:\_RENDERING'

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

    MAYA_PATH = WindowsPath(r'C:\Program Files\Autodesk\Maya2023\bin\mayabatch.exe')

    final_output = OUTPUT_PATH.joinpath(SCENE_PATH.name)

    if final_output.exists():
        if replace:
            print("Deleting old output directory")
            shutil.rmtree(final_output)
        else:
            print(f"Output directory {final_output} already exists! Run with --replace flag to replace it.")

    print("Archiving Maya scene")
    # Archive the scene
    
    #subprocess.run([MAYA_PATH,'-file', SCENE_PATH, '-proj', PROJECT_PATH,'-command', 'ArchiveScene']).check_returncode()
    maya.mel.eval('ArchiveScene')
    archive_path = SCENE_PATH.parent.joinpath(f"{SCENE_PATH.name}.zip")

    print("Moving archived scene to output location")
    moved_archive = shutil.move(archive_path, OUTPUT_PATH)

    print(f"Unzipping output archive")
    with zipfile.ZipFile(moved_archive, 'r') as zip_ref:
        zip_ref.extractall(final_output)
    
    print(f"Deleting zip")
    os.remove(moved_archive)

    print(f"Scene prepared for rendering! Saved to {final_output.absolute()}")

    print(f"Generating Smedge config")

    output_scene = find(lambda path: path.is_file(), list(final_output.glob(f"**/{SCENE_PATH.name}")))
    if output_scene == None:
        raise Exception("Couldn't find output scene!")
    output_proj = find_project(output_scene)

    start_frame = int(maya.cmds.getAttr('defaultRenderGlobals.startFrame'))
    end_frame = int(maya.cmds.getAttr('defaultRenderGlobals.endFrame'))

    with open(final_output.joinpath('SmedgeSettings.sj'), 'w') as smedge_config:
        config_contents = f'''[4c8e3273-5d60-4d68-af28-23799ab7134c]
        ID = 4c8e3273-5d60-4d68-af28-23799ab7134c
        Type = 833c1fa9-fc0b-46da-920a-c4b74b92d5c1
        Name = {SCENE_PATH.name}
        Project = {output_proj.absolute()}
        Scene = {output_scene.absolute()}
        RenderDir = {final_output.joinpath(f'RENDER_OUT/{SCENE_PATH.name}_render').absolute()}
        Range = {start_frame}-{end_frame}
        Status = 0
        FailureLimit = 0
        OvertimeKill = 0'''
        smedge_config.write(config_contents)
        print(f"Output smedge config: \n{config_contents}")
    
    print("Done! Good luck with your render, you're gonna need it.")


package_project(Path(cmds.file(q=True, sn=True)).absolute(), Path(OUTPUT_LOCATION).absolute(), True)

