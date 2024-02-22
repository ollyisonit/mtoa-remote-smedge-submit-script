import pymel.core as pm
import os.path as Path
import maya.cmds as cmds
from typing import Callable, Optional


class RenderLayer:
    """Tracks state of render layer"""
    name: str = ""
    enabled: bool = False
    packet_size: int = 1

    def __init__(self, name: str, enabled: bool, packet_size: int):
        self.name = name
        self.enabled = enabled
        self.packet_size = packet_size

    def set_enabled(self, value: bool):
        self.enabled = value
        return self

    def set_packet_size(self, packet_size: int):
        self.packet_size = 1
        return self


class SubmitUIState:
    """Tracks state of UI and saves/loads state to the necessary nodes."""
    render_layers: dict[str, RenderLayer] = []
    generate_tx: bool = False
    force_tx: bool = True
    network_project_location: str = None
    network_render_location: str = None
    exclude_directories: list[str] = ["autosave", "incrementalSave", "images"]
    start_frame: int = 0
    end_frame: int = 0

    def save_to_file(self):
        pass

    def load_from_file(self):
        pass


class SubmitUI:
    """Visual component of UI. Responds to user input and updates internal state as necessary."""
    WINDOW_ID = "dninoSmedgeSubmit"
    LABEL_WIDTH = 200
    TICKBOX_WIDTH = 30
    MARGIN = 4
    main_window = None
    state: SubmitUIState = None

    current_render_layers: dict[str, 'RenderLayerUI'] = {}
    render_layers_layout = None
    generate_tx_check = None
    force_tx_check = None
    start_frame_field = None
    end_frame_field = None
    project_dir_input = None
    render_dir_input = None
    exclude_dir_input = None
    close_button = None
    generate_config = None

    class RenderLayerUI:
        render_layers_row = None
        render_layer_checkbox = None
        render_layer_label = None
        render_layer_packet_label = None
        render_layer_packet_input = None

        def __init__(self, parent):
            self.render_layers_row = pm.rowLayout(
                numberOfColumns=4,
                columnWidth=[
                    [1, SubmitUI.TICKBOX_WIDTH],
                    [2, SubmitUI.LABEL_WIDTH - SubmitUI.TICKBOX_WIDTH],
                ],
                parent=parent,
            )
            self.render_layer_checkbox = pm.checkBox(
                label="", parent=self.render_layers_row, changeCommand=lambda _: self.update_disabled())
            self.render_layer_label = pm.text(parent=self.render_layers_row)
            self.render_layer_packet_label = pm.text(
                label="Packet Size", parent=self.render_layers_row
            )
            self.render_layer_packet_input = pm.intField(
                parent=self.render_layers_row)

        def update_disabled(self):
            is_enabled = pm.checkBox(
                self.render_layer_checkbox, query=True, value=True)
            pm.text(self.render_layer_label, edit=True, enable=is_enabled)
            pm.text(self.render_layer_packet_label,
                    edit=True, enable=is_enabled)
            pm.intField(self.render_layer_packet_input,
                        edit=True, enable=is_enabled)

        def update(self, layer: RenderLayer):
            pm.checkBox(self.render_layer_checkbox,
                        edit=True, value=layer.enabled)
            pm.text(self.render_layer_label, edit=True, label=layer.name)
            pm.intField(self.render_layer_packet_input,
                        edit=True, value=layer.packet_size)
            self.update_disabled()
            return self

        def delete(self):
            pm.delete(self.render_layers_row)

    def __init__(self, state: SubmitUIState,
                 onClose: Callable[[SubmitUIState], None],
                 validate: Callable[[SubmitUIState], Optional[str]],
                 submit: Callable[[SubmitUIState], None]):
        self.state = state
        self.build_ui(onClose, validate, submit)

    def build_ui(self, onClose: Callable[[SubmitUIState], None], validate: Callable[[SubmitUIState], Optional[str]],
                 submit: Callable[[SubmitUIState], None]):
        if pm.window(self.WINDOW_ID, exists=True):
            cmds.deleteUI(self.WINDOW_ID, window=True)

        self.main_window = pm.window(
            self.WINDOW_ID, title="Submit Smedge Job",
            resizeToFitChildren=True,
        )
        cmds.setUITemplate("OptionsTemplate", pushTemplate=True)
        main_layout_form = pm.formLayout(parent=self.main_window)
        main_layout = pm.columnLayout(
            parent=main_layout_form, adjustableColumn=True)
        pm.formLayout(main_layout_form, edit=True, attachForm=[[main_layout, "left", self.MARGIN],
                                                               [main_layout, "right",
                                                                   self.MARGIN],
                                                               [main_layout, "top",
                                                                   self.MARGIN],
                                                               [main_layout, "bottom", self.MARGIN]])
        render_options_frame = pm.frameLayout(
            "Render Options",
            collapsable=False,
            marginHeight=5,
            parent=main_layout,
            annotation="",
        )
        render_options_layout = pm.columnLayout(parent=render_options_frame)
        self.generate_tx_check = pm.checkBoxGrp(
            label="Generate TX Files",
            columnWidth=[1, self.LABEL_WIDTH],
            parent=render_options_layout,
            annotation=(
                "(Arnold) Whether TX files should be generated. Turn off "
                "if there are multiple render nodes, as multiple machines generating "
                "TX files at once can cause conflicts"
            )
        )
        self.force_tx_check = pm.checkBoxGrp(
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
        frame_range_label = pm.text(
            label="Frame Range", parent=frame_range_row)
        self.start_frame_field = pm.intField(width=30, parent=frame_range_row)
        self.end_frame_field = pm.intField(width=30, parent=frame_range_row)

        render_layers_frame = pm.frameLayout(
            "Enabled Render Layers",
            collapsable=False,
            marginHeight=5,
            parent=render_options_layout,
        )
        self.render_layers_layout = pm.columnLayout(parent=render_layers_frame)

        output_options_frame = pm.frameLayout(
            "Output Options", collapsable=False, marginHeight=5, parent=main_layout
        )
        output_options_layout = pm.columnLayout(parent=output_options_frame)
        self.project_dir_input = self.createFilepathUI(
            "Network Project Directory", parent=output_options_layout
        )
        self.render_dir_input = self.createFilepathUI(
            "Network Render Output Directory", parent=output_options_layout
        )
        self.exclude_dir_input = pm.textFieldGrp(
            label="Exclude Directories",
            columnWidth=[1, self.LABEL_WIDTH],
            parent=output_options_layout,
            annotation=("Comma separated list of directories to exclude when "
                        "syncing project to network directory.")
        )
        confirm_buttons_form = pm.formLayout(parent=main_layout)
        self.close_button = pm.button(
            label="Close", parent=confirm_buttons_form)
        self.generate_config = pm.button(
            label="Generate Config and Sync", parent=confirm_buttons_form)
        pm.formLayout(confirm_buttons_form, edit=True, attachForm=[[self.close_button, "left", 0],
                                                                   [self.close_button,
                                                                       "top", self.MARGIN],
                                                                   [self.generate_config,
                                                                       "right", 0],
                                                                   [self.generate_config, "top", self.MARGIN]],
                      attachPosition=[[self.close_button, "right", self.MARGIN, 50],
                                      [self.generate_config, "left", self.MARGIN, 50]])

        self.apply_state_to_ui(self.state)

    def apply_state_to_ui(self, state: SubmitUIState):
        pm.checkBoxGrp(self.generate_tx_check, edit=True,
                       value1=state.generate_tx)
        pm.checkBoxGrp(self.force_tx_check, edit=True, value1=state.force_tx)
        pm.intField(self.start_frame_field, edit=True, value=state.start_frame)
        pm.intField(self.end_frame_field, edit=True, value=state.end_frame)
        self.update_render_layers(state, self.render_layers_layout)
        pm.textField(self.project_dir_input, edit=True,
                     text=state.network_project_location)
        pm.textField(self.render_dir_input, edit=True,
                     text=state.network_render_location)
        pm.textFieldGrp(self.exclude_dir_input, edit=True,
                        text=",".join(state.exclude_directories))
        return self

    def apply_ui_to_state(self) -> SubmitUIState:
        self.state.generate_tx = pm.checkBoxGrp(
            self.generate_tx_check, query=True, value1=True)
        self.state.force_tx = pm.checkBoxGrp(
            self.force_tx_check, query=True, value1=True)

        return self.state

    def update_render_layers(self, state: SubmitUIState, parent):
        for layer_name, layer_ui in self.current_render_layers.items():
            if not layer_name in [l.name for l in state.render_layers]:
                layer_ui.delete()
                self.current_render_layers.pop(layer_name)

        for layer in state.render_layers:
            if not layer.name in self.current_render_layers.keys():
                self.current_render_layers[layer.name] = self.RenderLayerUI(
                    parent)
            self.current_render_layers[layer.name].update(layer)

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
test_state.generate_tx = True
test_state.force_tx = False
test_state.start_frame = 10
test_state.end_frame = 20
test_state.render_layers = [
    RenderLayer("noCarliarBackLayer", True, 12),
    RenderLayer("TEST2", False, 143),
]
submit_ui = SubmitUI(test_state, lambda x: None,
                     lambda x: None, lambda x: None)
submit_ui.show()
