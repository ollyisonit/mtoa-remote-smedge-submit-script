import pymel.core as pm
import os.path as Path
import maya.cmds as cmds
from typing import Callable


class RenderLayer:
    name: str = ""
    enabled: bool = False
    packet_size: int = 1

    def __init__(self, name: str, enabled: bool, packet_size: int):
        self.name = name
        self.enabled = enabled
        self.packet_size = packet_size


class SubmitUIState:
    render_layers: list[RenderLayer] = []
    generate_tx: bool = False
    force_tx: bool = True
    network_project_location: Path = None
    network_render_location: Path = None
    exclude_directories: list[str] = ["autosave", "incrementalSave", "images"]
    start_frame: int = 0
    end_frame: int = 0

    def save_bool():
        pass

    def load_render_layers() -> list[RenderLayer]:
        pass

    def saveState():
        pass

    def loadState():
        pass

    def defaultState():
        pass


class SubmitUI:
    main_window = None
    state: SubmitUIState = None
    WINDOW_ID = "dninoSmedgeSubmit"
    LABEL_WIDTH = 200
    TICKBOX_WIDTH = 30
    MARGIN=4
    apply_state_to_ui: Callable[[SubmitUIState], None]

    def __init__(self, state: SubmitUIState):
        self.state = state
        self.build_ui()

    def build_ui(self):
        if pm.window(self.WINDOW_ID, exists=True):
            cmds.deleteUI(self.WINDOW_ID, window=True)

        self.main_window = pm.window(
            self.WINDOW_ID,
            title="Submit Smedge Job",
            resizeToFitChildren=True,
        )
        cmds.setUITemplate("OptionsTemplate", pushTemplate=True)
        main_layout_form = pm.formLayout(parent=self.main_window)
        main_layout = pm.columnLayout(parent=main_layout_form, adjustableColumn=True)
        pm.formLayout(main_layout_form, edit=True, attachForm=[[main_layout, "left", self.MARGIN], 
                                                               [main_layout, "right", self.MARGIN], 
                                                               [main_layout, "top", self.MARGIN],
                                                               [main_layout, "bottom", self.MARGIN]])
        render_options_frame = pm.frameLayout(
            "Render Options",
            collapsable=False,
            marginHeight=5,
            parent=main_layout,
            annotation="",
        )
        render_options_layout = pm.columnLayout(parent=render_options_frame)
        generate_tx_check = pm.checkBoxGrp(
            label="Generate TX Files",
            columnWidth=[1, self.LABEL_WIDTH],
            parent=render_options_layout,
            annotation=(
                "(Arnold) Whether TX files should be generated. Turn off "
                "if there are multiple render nodes, as multiple machines generating "
                "TX files at once can cause conflicts"
            ),
        )
        force_tx_check = pm.checkBoxGrp(
            label="Force TX Files",
            columnWidth=[1, self.LABEL_WIDTH],
            parent=render_options_layout,
            annotation=("(Arnold) Errors if TX files are missing. Generate "
                        "TX files in Arnold>Utilities>TX Manager")
        )
        frame_range_row = pm.rowLayout(
            numberOfColumns=4,
            columnWidth=[1, self.LABEL_WIDTH],
            parent=render_options_layout,
        )
        frame_range_label = pm.text(label="Frame Range", parent=frame_range_row)
        start_frame_field = pm.textField(width=30, parent=frame_range_row)
        end_frame_field = pm.textField(width=30, parent=frame_range_row)

        render_layers_frame = pm.frameLayout(
            "Enabled Render Layers",
            collapsable=False,
            marginHeight=5,
            parent=render_options_layout,
        )
        render_layers_layout = pm.columnLayout(parent=render_layers_frame)
        for layer in self.state.render_layers:
            render_layers_row = pm.rowLayout(
                numberOfColumns=4,
                columnWidth=[
                    [1, self.TICKBOX_WIDTH],
                    [2, self.LABEL_WIDTH - self.TICKBOX_WIDTH],
                ],
                parent=render_layers_layout,
            )
            render_layer_check = pm.checkBox(label="", parent=render_layers_row)
            render_layer_label = pm.text(label=layer.name, parent=render_layers_row)
            render_layer_packet_label = pm.text(
                label="Packet Size", parent=render_layers_row
            )
            render_layer_packet_entry = pm.textField(parent=render_layers_row)

        output_options_frame = pm.frameLayout(
            "Output Options", collapsable=False, marginHeight=5, parent=main_layout
        )
        output_options_layout = pm.columnLayout(parent=output_options_frame)
        project_dir_input = self.createFilepathUI(
            "Network Project Directory", parent=output_options_layout
        )
        render_dir_input = self.createFilepathUI(
            "Network Render Output Directory", parent=output_options_layout
        )
        exclude_dir_input = pm.textFieldGrp(
            label="Exclude Directories",
            columnWidth=[1, self.LABEL_WIDTH],
            parent=output_options_layout,
            annotation=("Comma separated list of directories to exclude when "
                        "syncing project to network directory.")
        )
        confirm_buttons_form = pm.formLayout(parent=main_layout)
        close_button = pm.button(label="Close", parent=confirm_buttons_form)
        generate_config = pm.button(label="Generate Config and Sync", parent=confirm_buttons_form)
        pm.formLayout(confirm_buttons_form, edit=True, attachForm=[[close_button,"left", 0], 
                                                                   [close_button, "top", self.MARGIN], 
                                                                   [generate_config, "right", 0],
                                                                   [generate_config, "top", self.MARGIN]],
                                                        attachPosition=[[close_button, "right", self.MARGIN, 50],
                                                                        [generate_config, "left", self.MARGIN, 50]])

        def apply_state_to_ui(state: SubmitUIState):
            
            pass

        self.apply_state_to_ui = apply_state_to_ui
            

        
    def createFilepathUI(self, label, parent):
        filepath_row_layout = pm.rowLayout(
            numberOfColumns=3,
            adjustableColumn=2,
            columnWidth=[[1, self.LABEL_WIDTH], [3, self.TICKBOX_WIDTH]],
            parent=parent,
        )
        filepath_label = pm.text(label=label, parent=filepath_row_layout)
        filepath_input = pm.textField(parent=filepath_row_layout)
        filepath_button = pm.symbolButton(
            image="navButtonBrowse.xpm", parent=filepath_row_layout
        )
        return filepath_input

    def show(self):
        pm.showWindow(self.main_window)


test_state = SubmitUIState()
test_state.render_layers = [
    RenderLayer("noCarliarBackLayer", True, 12),
    RenderLayer("TEST2", False, 12),
]
submit_ui = SubmitUI(test_state)
submit_ui.show()
