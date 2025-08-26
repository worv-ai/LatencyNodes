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
from copy import deepcopy
from collections import deque

import carb
import omni
import omni.graph.core as og


class OgnLatencyControllerInternalState:
    """Convenience class for maintaining per-node state information"""

    def __init__(self):
        """Instantiate the per-node state information"""
        # (Current time + latency, data)
        self.latency_queue = deque()
    
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
    
    def get_from_queue(self, current_time):
        while self.latency_queue and self.latency_queue[0][0] <= current_time:
            # Pop the first item from the queue
            # and return it.
            yield self.latency_queue.popleft()


class OgnLatencyController:
    """The Ogn node class"""

    @staticmethod
    def initialize(graph_context, node):
        """
        Initialize the node
        """
        try:
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

            # === Resolve the type for output of the LatencyController ===
            # Make sure the declared type of attribute is not UNKNOWN
            upstream_attr_type = upstream_attr.get_resolved_type()

            if upstream_attr_type.base_type == og.BaseDataType.UNKNOWN:
                return
            
            downstream_attr.set_resolved_type(upstream_attr_type)

            output_type = og.Type(
                base_type=upstream_attr_type.base_type,
                array_depth=upstream_attr_type.array_depth + 1,
                role=upstream_attr_type.role,
                tuple_count=upstream_attr_type.tuple_count
            )

            output_attr = downstream_node.get_attribute("outputs:dataOut")
            output_attr.set_resolved_type(output_type)
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

            # === Reset the type for output of the LatencyController ===
            output_attr = downstream_node.get_attribute("outputs:dataOut")
            output_attr.set_resolved_type(og.Type(og.BaseDataType.UNKNOWN))
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
        state = db.per_instance_state

        # === Get the inputs ===
        exec_in = db.inputs.execIn
        data_in = db.inputs.dataIn
        timestamp_in = db.inputs.timestampIn # current time
        latency = db.inputs.latency

        if exec_in == og.ExecutionAttributeState.DISABLED:
            return False
        
        # TODO: Debug whether the needed connection is connected

        state.add_to_queue(
            timestamp_in, latency, data_in.value
        )
        
        results = list(state.get_from_queue(timestamp_in))
         
        if not results:
            db.outputs.execOut = og.ExecutionAttributeState.DISABLED
            return False

        timestamps = []
        data_values = []
        
        for delayed_time, delayed_data in results:
            timestamps.append(delayed_time)
            data_values.append(delayed_data)

        # === write outputs ===
        db.outputs.timestampOut = timestamps
        db.outputs.dataOut = data_values

        db.outputs.execOut = og.ExecutionAttributeState.ENABLED

        return True
 