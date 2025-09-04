"""
OmniGraph core Python API:
  https://docs.omniverse.nvidia.com/kit/docs/omni.graph/latest/Overview.html

OmniGraph attribute data types:
  https://docs.omniverse.nvidia.com/kit/docs/omni.graph.docs/latest/dev/ogn/attribute_types.html

Collection of OmniGraph code examples in Python:
  https://docs.omniverse.nvidia.com/kit/docs/omni.graph.docs/latest/dev/ogn/ogn_code_samples_python.html

Collection of OmniGraph tutorials:
  https://docs.omniverse.nvidia.com/kit/docs/omni.graph.tutorials/latest/Overview.html
"""
from collections import deque

import carb
import omni.graph.core as og
from omni.graph.action_core import get_interface


class OgnLatencyControllerInternalState:
    """Convenience class for maintaining per-node state information"""

    def __init__(self):
        """Instantiate the per-node state information"""
        # (Current time + latency, data)
        self.latency_queue = deque()
        # State for outputting elements one by one
        self.current_ready_elements = []
        self.element_index = 0  # Current element being processed

    def add_to_queue(self, current_time, latency, data):
        """Add data to the latency queue with the current time + latency"""
        delayed_time = current_time + latency

        # If the queue is empty, append the new data
        if not self.latency_queue:
            self.latency_queue.append((delayed_time, data))
            return

        # If the delayed time is smaller than the last item
        # in the queue, skip it.
        if self.latency_queue[-1][0] >= delayed_time:
            return

        # Otherwise, append the new data
        self.latency_queue.append((delayed_time, data))

    def get_ready_elements(self, current_time):
        """Get all elements that are ready to be output"""
        ready_elements = []
        while self.latency_queue and self.latency_queue[0][0] <= current_time:
            ready_elements.append(self.latency_queue.popleft())
        return ready_elements

    def start_element_processing(self, ready_elements):
        """Start processing a batch of ready elements"""
        self.current_ready_elements = ready_elements
        self.element_index = 0


class OgnLatencyController:
    """The Ogn node class"""

    @staticmethod
    def initialize(graph_context, node):
        """
        Initialize the node
        """
        try:
            # Register type resolution callback for element output
            connected_function_callback = OgnLatencyController.on_connected_callback
            disconnected_function_callback = OgnLatencyController.on_disconnected_callback
            node.register_on_connected_callback(connected_function_callback)
            node.register_on_disconnected_callback(disconnected_function_callback)
        except Exception as e:
            carb.log_error(f"Error initializing OgnLatencyController: {e}")
            raise
    
    @staticmethod
    def release(node):
        """
        Release the node, by resetting the internal state.
        """
        pass

    @staticmethod
    def on_connected_callback(upstream_attr, downstream_attr):
        """
        Callback when the attribute of the node is connected.
        """

        try:
            # === Get the downstream node and attribute ===
            downstream_node = downstream_attr.get_node()
            downstream_attr_name = downstream_attr.get_name()
            downstream_node_name = downstream_node.get_type_name()

            # === Check if the attribute is LatencyController's one ===
            if not downstream_attr_name == "inputs:dataIn":
                return

            if not downstream_node_name == \
                   "worvai.nodes.latency_nodes.LatencyController":
                return

            # === Resolve the type for element output of the LatencyController ===
            # Make sure the declared type of attribute is not UNKNOWN
            upstream_attr_type = upstream_attr.get_resolved_type()

            if upstream_attr_type.base_type == og.BaseDataType.UNKNOWN:
                return

            downstream_attr.set_resolved_type(upstream_attr_type)

            # The element output should have the same type as the input (no array nesting)
            element_output_attr = downstream_node.get_attribute("outputs:element")
            element_output_attr.set_resolved_type(upstream_attr_type)
        except Exception as e:
            carb.log_error(
                "[Latency Controller]",
                f"Error in on_connected_callback: {e}"
            )
            raise

    @staticmethod
    def on_disconnected_callback(upstream_attr, downstream_attr):
        """
        Callback when the attribute of the node is disconnected.
        """
        try:
            # === Get the downstream node and attribute ===
            downstream_node = downstream_attr.get_node()
            downstream_attr_name = downstream_attr.get_name()
            downstream_node_name = downstream_node.get_type_name()

            # === Check if the attribute is LatencyController's one ===
            if not downstream_attr_name == "inputs:dataIn":
                return

            if not downstream_node_name == \
                   "worvai.nodes.latency_nodes.LatencyController":
                return

            # === Reset the type for element output of the LatencyController ===
            element_output_attr = downstream_node.get_attribute("outputs:element")
            element_output_attr.set_resolved_type(og.Type(og.BaseDataType.UNKNOWN))
        except Exception as e:
            carb.log_error(
                "[Latency Controller]",
                f"Error in on_disconnected_callback: {e}"
            )
            raise

    @staticmethod
    def internal_state():
        """Returns an object that contains per-node state information"""
        return OgnLatencyControllerInternalState()

    @staticmethod
    def compute(db) -> bool:
        """Compute the output based on inputs and internal state"""
        try:
            # Get action graph interface for proper execution control
            action_graph = get_interface()
            if not action_graph:
                carb.log_error("LatencyController: Could not get action graph interface")
                return False

            state = db.per_instance_state

            # === Get the inputs ===
            data_in = db.inputs.dataIn
            timestamp_in = db.inputs.timestampIn
            latency = db.inputs.latency

            # If execIn is triggered, start a new processing cycle
            if action_graph.get_execution_enabled("inputs:execIn"):
                # Add new data to the queue
                state.add_to_queue(timestamp_in, latency, data_in.value)

                # Get all ready elements and start processing them
                ready_elements = state.get_ready_elements(timestamp_in)
                state.start_element_processing(ready_elements)

                # Reset element index for new cycle
                state.element_index = 0

            # Check if we have elements to process
            if state.element_index >= len(state.current_ready_elements):
                # All elements processed - trigger finished
                action_graph.set_execution_enabled("outputs:finished")
                state.element_index = 0  # Reset for next cycle
                return True

            # Get current element to output
            current_index = state.element_index
            state.element_index += 1  # Advance for next element

            delayed_time, element_data = state.current_ready_elements[current_index]

            # Set element outputs
            db.outputs.element = element_data
            db.outputs.elementIndex = current_index
            db.outputs.elementTimestamp = delayed_time

            # Use setExecutionEnabledAndPushed to unroll ALL elements at once
            # This leads to compute() being called again immediately for the next element
            action_graph.set_execution_enabled_and_pushed("outputs:loopBody")

            return True

        except Exception as e:
            carb.log_error(f"LatencyController compute error: {e}")
            return False
