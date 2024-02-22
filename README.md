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

The ui has methods that sync it to the state and vice-versa. I'm not using callbacks because they're too complicated and messy. Instead, I'm going to make it apply the state to the UI on open and the UI to the state on close. This also means the state needs to load itself from its special node when it opens. When generate is clicked, it should validate the state, then save the state, then run the script I wrote. 