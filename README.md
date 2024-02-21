TODO

OK so this script does two things:

1. Syncs Maya project to a network drive
2. Writes out a custom Smedge config

For config settings, it needs a UI with:

- Make UI with:
  - Output Project Location (stored on custom node)
  - Output Render Location (stored on custom node)
  - Render Layer Tickboxes with packet sizes (stored on custom node)
    - actually just do this automatically based on renderable layers, have it generate a config for each one
  - Generate TX (stored on custom node)
  - Force TX (stored on custom node)
  - AutoTX (stored on custom node, explain what this is)
  - List of directory names to exclude (defaults to autosave,incrementalSave,images), just have it be a comma-separated string if you have commas in your file names then you have bigger issues (stored on custom node)
  - Start frame/end frame (use the render globals node)
- These need to be persisted, so store them as custom attributes on a node (seems like usually people use the network node for this), just call it something namespaced with _dnino and i should be fine



SO the steps are:

1. Build the UI
2. Make the UI persist (ie. hook it up to custom nodes/exiting attributes)
3. Tooltips!
4. Add a button to reset config (delete custom node)



**Where I'm At Right Now**

Working on the function that applies the state to the UI. I'm thinking that basically the lifecycle will be this:

- Window is launched
- Load state
- Build UI window
- Apply state
- Each time a control is clicked, update the state and then apply the state (if needed, might not need to apply the state when dealing with the text boxes)
- When the window is closed, save the state

Having trouble with updating the render layers, since they're dynamically generated. I'm thinking of first digging through the children and getting the tooltips of all the currently existing render layer ui elements, then using that information to remove the ones that no longer exist, then loop through the state's list of render layers and update the layer ui if it exists or creating a new one if it doesn't. Also set enable=False to grey out other controls if the render layer is disabled

- Then for the "Generate Config" command it closes, syncs, and generates the file