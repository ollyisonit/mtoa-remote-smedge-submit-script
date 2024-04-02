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


class SubmitUIState:
    """Tracks state of UI and saves/loads state to the necessary nodes."""

    render_layers: list[RenderLayer] = []
    generate_tx: bool = False
    force_tx: bool = True
    network_project_location: str = ""
    network_render_location: str = ""
    exclude_directories: list[str] = ["autosave", "incrementalSave", "images"]
    start_frame: int = 0
    end_frame: int = 1
    NODE_ID = "ollyisonitSmedgeSubmit_config"
    # Render layers are stored as 3 separate arrays where all values with the same index
    # correspond to the same object.
    RENDER_LAYER_NAME_ATTR = "render_layers_names"
    RENDER_LAYER_ENABLED_ATTR = "render_layers_enabled"
    RENDER_LAYER_PACKET_SIZE_ATTR = "render_layers_packet_sizes"
    GENERATE_TX_ATTR = "generate_tx"
    FORCE_TX_ATTR = "force_tx"
    NETWORK_PROJECT_LOCATION_ATTR = "network_project_location"
    NETWORK_RENDER_LOCATION_ATTR = "network_render_location"
    EXCLUDE_DIRECTORIES_LOCATION_ATTR = "exclude_directories"
    START_FRAME_ATTR = "start_frame"
    END_FRAME_ATTR = "end_frame"

    def create_storage_node(self, deleteExisting: bool = False):
        """Creates the Maya node used to store configuration data.
        Args:
            deleteExisting (bool): True deletes existing node, False skips creation if node exists
        """
        if pm.objExists(self.NODE_ID):
            if deleteExisting:
                pm.delete(self.NODE_ID)
            else:
                return self
        pm.createNode("network", name=self.NODE_ID, skipSelect=True)
        pm.addAttr(self.NODE_ID,
                   shortName=self.RENDER_LAYER_NAME_ATTR,
                   dataType="stringArray")
        pm.addAttr(self.NODE_ID,
                   shortName=self.RENDER_LAYER_ENABLED_ATTR,
                   dataType="Int32Array")  # Int32Array otherwise
        pm.addAttr(self.NODE_ID,
                   shortName=self.RENDER_LAYER_PACKET_SIZE_ATTR,
                   dataType="Int32Array")
        pm.addAttr(self.NODE_ID,
                   shortName=self.GENERATE_TX_ATTR,
                   attributeType="bool")
        pm.addAttr(self.NODE_ID,
                   shortName=self.FORCE_TX_ATTR,
                   attributeType="bool")
        pm.addAttr(self.NODE_ID,
                   shortName=self.NETWORK_PROJECT_LOCATION_ATTR,
                   dataType="string")
        pm.addAttr(self.NODE_ID,
                   shortName=self.NETWORK_RENDER_LOCATION_ATTR,
                   dataType="string")
        pm.addAttr(self.NODE_ID,
                   shortName=self.EXCLUDE_DIRECTORIES_LOCATION_ATTR,
                   dataType="stringArray")
        pm.addAttr(self.NODE_ID,
                   shortName=self.START_FRAME_ATTR,
                   attributeType="long")
        pm.addAttr(self.NODE_ID,
                   shortName=self.END_FRAME_ATTR,
                   attributeType="long")
        self.save_to_node()
        return self

    def save_to_node(self):
        self.create_storage_node(deleteExisting=False)
        pm.setAttr(f"{self.NODE_ID}.{self.RENDER_LAYER_NAME_ATTR}",
                   [l.name for l in self.render_layers])
        pm.setAttr(f"{self.NODE_ID}.{self.RENDER_LAYER_ENABLED_ATTR}",
                   [l.enabled for l in self.render_layers])
        pm.setAttr(f"{self.NODE_ID}.{self.RENDER_LAYER_PACKET_SIZE_ATTR}",
                   [l.packet_size for l in self.render_layers])
        pm.setAttr(f"{self.NODE_ID}.{self.GENERATE_TX_ATTR}", self.generate_tx)
        pm.setAttr(f"{self.NODE_ID}.{self.FORCE_TX_ATTR}", self.force_tx)
        pm.setAttr(f"{self.NODE_ID}.{self.NETWORK_PROJECT_LOCATION_ATTR}",
                   self.network_project_location)
        pm.setAttr(f"{self.NODE_ID}.{self.NETWORK_RENDER_LOCATION_ATTR}",
                   self.network_render_location)
        pm.setAttr(f"{self.NODE_ID}.{self.EXCLUDE_DIRECTORIES_LOCATION_ATTR}",
                   self.exclude_directories)
        pm.setAttr(f"{self.NODE_ID}.{self.START_FRAME_ATTR}", self.start_frame)
        pm.setAttr(f"{self.NODE_ID}.{self.END_FRAME_ATTR}", self.end_frame)
        return self

    def load_from_node(self):
        # Keep default values if loading for the first time
        if not pm.objExists(self.NODE_ID):
            self.create_storage_node(deleteExisting=False)
            return self
        render_layer_names = pm.getAttr(
            f"{self.NODE_ID}.{self.RENDER_LAYER_NAME_ATTR}")
        if render_layer_names == None:
            render_layer_names = []
        render_layer_enableds = pm.getAttr(
            f"{self.NODE_ID}.{self.RENDER_LAYER_ENABLED_ATTR}")
        if render_layer_enableds == None:
            render_layer_enableds = []
        render_layer_packet_sizes = pm.getAttr(
            f"{self.NODE_ID}.{self.RENDER_LAYER_PACKET_SIZE_ATTR}")
        if render_layer_packet_sizes == None:
            render_layer_packet_sizes = []
        self.render_layers = []
        for i in range(len(render_layer_names)):
            self.render_layers.append(
                RenderLayer(render_layer_names[i], render_layer_enableds[i],
                            render_layer_packet_sizes[i]))
        self.generate_tx = pm.getAttr(
            f"{self.NODE_ID}.{self.GENERATE_TX_ATTR}")
        self.force_tx = pm.getAttr(f"{self.NODE_ID}.{self.FORCE_TX_ATTR}")
        self.network_project_location = pm.getAttr(
            f"{self.NODE_ID}.{self.NETWORK_PROJECT_LOCATION_ATTR}")
        self.network_render_location = pm.getAttr(
            f"{self.NODE_ID}.{self.NETWORK_RENDER_LOCATION_ATTR}")
        self.exclude_directories = pm.getAttr(
            f"{self.NODE_ID}.{self.EXCLUDE_DIRECTORIES_LOCATION_ATTR}")
        if self.exclude_directories == None:
            self.exclude_directories = []
        self.start_frame = pm.getAttr(
            f"{self.NODE_ID}.{self.START_FRAME_ATTR}")
        self.end_frame = pm.getAttr(f"{self.NODE_ID}.{self.END_FRAME_ATTR}")

        existing_render_layers = pm.ls(type='renderLayer')
        self.render_layers = list(
            filter(lambda l: l.name in existing_render_layers,
                   self.render_layers))
        for layername in existing_render_layers:
            if not layername in [l.name for l in self.render_layers]:
                self.render_layers.append(RenderLayer(layername, True, 1))
        return self


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
            label="",
            parent=self.render_layers_row,
            changeCommand=lambda _: self.update_disabled())
        self.render_layer_label = pm.text(parent=self.render_layers_row)
        self.render_layer_packet_label = pm.text(label="Packet Size",
                                                 parent=self.render_layers_row)
        self.render_layer_packet_input = pm.intField(
            parent=self.render_layers_row)

    def update_disabled(self):
        is_enabled = pm.checkBox(self.render_layer_checkbox,
                                 query=True,
                                 value=True)
        pm.text(self.render_layer_label, edit=True, enable=is_enabled)
        pm.text(self.render_layer_packet_label, edit=True, enable=is_enabled)
        pm.intField(self.render_layer_packet_input,
                    edit=True,
                    enable=is_enabled)

    def update(self, layer: RenderLayer):
        pm.checkBox(self.render_layer_checkbox, edit=True, value=layer.enabled)
        pm.text(self.render_layer_label, edit=True, label=layer.name)
        pm.intField(self.render_layer_packet_input,
                    edit=True,
                    value=layer.packet_size)
        self.update_disabled()
        return self

    def delete(self):
        pm.delete(self.render_layers_row)


class SubmitUI:
    """Visual component of UI. Responds to user input and updates internal state as necessary."""
    WINDOW_ID = "ollyisonitSmedgeSubmit_UI"
    LABEL_WIDTH = 200
    TICKBOX_WIDTH = 30
    MARGIN = 4
    main_window = None
    state: SubmitUIState = None

    ui_render_layers: dict[str, RenderLayerUI] = {}
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

    def __init__(self, state: SubmitUIState, onClose: Callable[[SubmitUIState],
                                                               None],
                 validate: Callable[[SubmitUIState], Optional[str]],
                 submit: Callable[[SubmitUIState], None]):
        self.state = state
        self.build_ui(onClose, validate, submit)

    def build_ui(self, onClose: Callable[[SubmitUIState], None],
                 validate: Callable[[SubmitUIState], Optional[str]],
                 submit: Callable[[SubmitUIState], None]):

        # Without this extra query the state will not be reported correctly the first time Maya opens
        pm.window(self.WINDOW_ID, exists=True)

        if pm.window(self.WINDOW_ID, exists=True):
            cmds.deleteUI(self.WINDOW_ID, window=True)

        self.main_window = pm.window(
            self.WINDOW_ID,
            title="Submit Smedge Job",
            resizeToFitChildren=True,
        )

        cmds.setUITemplate("OptionsTemplate", pushTemplate=True)

        main_layout_form = pm.formLayout(parent=self.main_window)
        main_layout = pm.columnLayout(parent=main_layout_form,
                                      adjustableColumn=True)
        pm.formLayout(main_layout_form,
                      edit=True,
                      attachForm=[[main_layout, "left", self.MARGIN],
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
        self.generate_tx_check = pm.checkBoxGrp(
            label="Generate TX Files",
            columnWidth=[1, self.LABEL_WIDTH],
            parent=render_options_layout,
            annotation=
            ("(Arnold) Whether TX files should be generated. Turn off "
             "if there are multiple render nodes, as multiple machines generating "
             "TX files at once can cause conflicts"))
        self.force_tx_check = pm.checkBoxGrp(
            label="Force TX Files",
            columnWidth=[1, self.LABEL_WIDTH],
            parent=render_options_layout,
            annotation=("(Arnold) Errors if TX files are missing. Generate "
                        "TX files in Arnold>Utilities>TX Manager"))

        frame_range_row = pm.rowLayout(
            numberOfColumns=4,
            columnWidth=[1, self.LABEL_WIDTH],
            parent=render_options_layout,
        )
        frame_range_label = pm.text(label="Frame Range",
                                    parent=frame_range_row)
        self.start_frame_field = pm.intField(width=30, parent=frame_range_row)
        self.end_frame_field = pm.intField(width=30, parent=frame_range_row)

        render_layers_frame = pm.frameLayout(
            "Enabled Render Layers",
            collapsable=True,
            marginHeight=5,
            parent=render_options_layout,
        )
        self.render_layers_layout = pm.columnLayout(parent=render_layers_frame)

        output_options_frame = pm.frameLayout("Output Options",
                                              collapsable=False,
                                              marginHeight=5,
                                              parent=main_layout)
        output_options_layout = pm.columnLayout(parent=output_options_frame)
        self.project_dir_input = self.createFilepathUI(
            "Network Project Directory", parent=output_options_layout)
        self.render_dir_input = self.createFilepathUI(
            "Network Render Output Directory", parent=output_options_layout)
        self.exclude_dir_input = pm.textFieldGrp(
            label="Exclude Directories",
            columnWidth=[1, self.LABEL_WIDTH],
            parent=output_options_layout,
            annotation=("Comma separated list of directories to exclude when "
                        "syncing project to network directory."))
        confirm_buttons_form = pm.formLayout(parent=main_layout)

        self.close_button = pm.button(label="Close",
                                      parent=confirm_buttons_form,
                                      command=lambda _: self.close())
        self.generate_config = pm.button(label="Generate Config and Sync",
                                         parent=confirm_buttons_form)
        pm.formLayout(
            confirm_buttons_form,
            edit=True,
            attachForm=[[self.close_button, "left", 0],
                        [self.close_button, "top", self.MARGIN],
                        [self.generate_config, "right", 0],
                        [self.generate_config, "top", self.MARGIN]],
            attachPosition=[[self.close_button, "right", self.MARGIN, 50],
                            [self.generate_config, "left", self.MARGIN, 50]])

        self.apply_state_to_ui(self.state)

    def apply_state_to_ui(self, state: SubmitUIState):
        pm.checkBoxGrp(self.generate_tx_check,
                       edit=True,
                       value1=state.generate_tx)
        pm.checkBoxGrp(self.force_tx_check, edit=True, value1=state.force_tx)
        pm.intField(self.start_frame_field, edit=True, value=state.start_frame)
        pm.intField(self.end_frame_field, edit=True, value=state.end_frame)
        for layer_ui in self.ui_render_layers.values():
            layer_ui.delete()
        for layer_state in state.render_layers:
            layer_ui = RenderLayerUI(self.render_layers_layout)
            layer_ui.update(layer_state)
            self.ui_render_layers[layer_state.name] = layer_ui
        pm.textField(self.project_dir_input,
                     edit=True,
                     text=state.network_project_location)
        pm.textField(self.render_dir_input,
                     edit=True,
                     text=state.network_render_location)
        pm.textFieldGrp(self.exclude_dir_input,
                        edit=True,
                        text=",".join(state.exclude_directories))
        return self

    def apply_ui_to_state(self) -> SubmitUIState:
        self.state.generate_tx = pm.checkBoxGrp(self.generate_tx_check,
                                                query=True,
                                                value1=True)
        self.state.force_tx = pm.checkBoxGrp(self.force_tx_check,
                                             query=True,
                                             value1=True)
        print("START FRAME")
        self.state.start_frame = pm.intField(self.start_frame_field,
                                             query=True,
                                             value=True)
        print("END FRAME")
        self.state.end_frame = pm.intField(self.end_frame_field,
                                           query=True,
                                           value=True)
        print("LAYER START")
        render_layers = []
        for layer_name, layer_ui in self.ui_render_layers.items():
            render_layers.append(
                RenderLayer(
                    layer_name,
                    pm.checkBox(layer_ui.render_layer_checkbox,
                                query=True,
                                value=True),
                    pm.intField(layer_ui.render_layer_packet_input,
                                query=True,
                                value=True)))
        print("LAYERS FOUND")
        self.state.render_layers = render_layers
        self.state.network_project_location = pm.textField(
            self.project_dir_input, query=True, text=True)
        self.state.network_render_location = pm.textField(
            self.render_dir_input, query=True, text=True)
        self.state.exclude_directories = pm.textFieldGrp(
            self.exclude_dir_input, query=True, text=True).split(",")
        return self.state

    def apply_and_save(self):
        self.apply_ui_to_state().save_to_node()

    def close(self):
        self.apply_and_save()
        cmds.deleteUI(self.WINDOW_ID, window=True)

    def createFilepathUI(self, label, parent):
        filepath_row_layout = pm.rowLayout(
            numberOfColumns=3,
            adjustableColumn=2,
            columnWidth=[[1, self.LABEL_WIDTH], [3, self.TICKBOX_WIDTH]],
            parent=parent,
        )
        filepath_label = pm.text(label=label, parent=filepath_row_layout)
        filepath_input = pm.textField(parent=filepath_row_layout)

        def choose_file():
            path: str = pm.fileDialog2(caption=label,
                                       dialogStyle=1,
                                       fileMode=3)[0]
            print(path)
            pm.textField(filepath_input, edit=True, text=path)

        filepath_button = pm.symbolButton(image="navButtonBrowse.xpm",
                                          parent=filepath_row_layout,
                                          command=lambda _: choose_file())

        return filepath_input

    def show(self):
        pm.showWindow(self.main_window)


# test_state = SubmitUIState()
# test_state.generate_tx = True
# test_state.force_tx = False
# test_state.start_frame = 10
# test_state.end_frame = 20
# test_state.render_layers = [
#     RenderLayer("noCarliarBackLayer", True, 12),
#     RenderLayer("TEST2", False, 143),
# ]
state = SubmitUIState().load_from_node()
submit_ui = SubmitUI(state, lambda x: None, lambda x: None, lambda x: None)
submit_ui.show()
