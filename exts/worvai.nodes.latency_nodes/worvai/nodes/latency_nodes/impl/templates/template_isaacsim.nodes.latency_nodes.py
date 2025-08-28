# from pathlib import Path

# import omni.graph.core as og
# import omni.ui as ui
# from omni.kit.property.usd.custom_layout_helper import (
#     CustomLayoutFrame, CustomLayoutGroup, CustomLayoutProperty
# )
# from omni.kit.window.property.templates import HORIZONTAL_SPACING


# class CustomLayout:
#     def __init__(self, compute_node_widget):
#         self.compute_node_widget = compute_node_widget
#         self.controller = og.Controller()
#         self.node = self.controller.node(compute_node_widget._payload[-1])

#         m_attr = self.node.get_attribute("inputs:method")
#         self.controller.subscribe_to_attribute(
#             m_attr, og.AttributeEventType.VALUE_CHANGED,
#             lambda *_, **__: self.widget.rebuild_window()
#         )

#     def _retrieve_existing_outputs(self):
#         # Retrieve all existing attributes of the form "outputs:output{num}"
#         # Also find the largest suffix among all such attributes
#         # Returned largest suffix = -1 if there are no such attributes
#         output_attribs = [attrib for attrib in self.node.get_attributes() if attrib.get_name()[:14] == "outputs:output"]
#         largest_suffix = -1
#         for attrib in output_attribs:
#             largest_suffix = max(largest_suffix, int(attrib.get_name()[14:]))
#         return (output_attribs, largest_suffix)

#     def _on_click_add(self):
#         (_, largest_suffix) = self._retrieve_existing_outputs()
#         self.controller.create_attribute(
#             self.node,
#             f"outputs:output{largest_suffix+1}",
#             og.Type(og.BaseDataType.UINT, 1, 0, og.AttributeRole.EXECUTION),
#             og.AttributePortType.ATTRIBUTE_PORT_TYPE_OUTPUT,
#         )
#         self.compute_node_widget.rebuild_window()
#         self.remove_button.enabled = True

#     def _on_click_remove(self):
#         (output_attribs, largest_suffix) = self._retrieve_existing_outputs()
#         if not output_attribs:
#             return
#         attrib_to_remove = self.node.get_attribute(f"outputs:output{largest_suffix}")
#         self.controller.remove_attribute(attrib_to_remove)
#         self.compute_node_widget.rebuild_window()
#         self.remove_button.enabled = len(output_attribs) > 1

#     def _controls_build_fn(self, *args):
#         (output_attribs, _) = self._retrieve_existing_outputs()
#         icons_path = Path(__file__).absolute().parent.parent.parent.parent.parent.parent.joinpath("icons")

#         with ui.HStack(height=0, spacing=HORIZONTAL_SPACING):
#             ui.Spacer()
#             self.add_button = ui.Button(
#                 image_url=f"{icons_path.joinpath('add.svg')}",
#                 width=22,
#                 height=22,
#                 style={"Button": {"background_color": 0x1F2124}},
#                 clicked_fn=self._on_click_add,
#                 tooltip_fn=lambda: ui.Label("Add New Output"),
#             )
#             self.remove_button = ui.Button(
#                 image_url=f"{icons_path.joinpath('remove.svg')}",
#                 width=22,
#                 height=22,
#                 style={"Button": {"background_color": 0x1F2124}},
#                 enabled=(len(output_attribs) > 1),
#                 clicked_fn=self._on_click_remove,
#                 tooltip_fn=lambda: ui.Label("Remove Output"),
#             )

#     def apply(self, props):
#         # Called by compute_node_widget to apply UI when selection changes
#         def find_prop(name):
#             try:
#                 return next((p for p in props if p.prop_name == name))
#             except StopIteration:
#                 return None

#         frame = CustomLayoutFrame(hide_extra=True)
#         (output_attribs, _) = self._retrieve_existing_outputs()
#         with frame:
#             with CustomLayoutGroup("Outputs"):
#                 for attrib in output_attribs:
#                     prop = find_prop(attrib.get_name())
#                     CustomLayoutProperty(prop.prop_name)

#                 CustomLayoutProperty(None, None, build_fn=self._controls_build_fn)

#         return frame.apply(props)
