"""
Render Product Latency Controller - Applies latency to render product data with actual image capture
"""
from copy import deepcopy
from collections import deque
import carb
import numpy as np
import omni
import omni.graph.core as og
import omni.replicator.core as rep


class RenderProductData:
    """Container for render product data with timestamp"""
    def __init__(self, render_product_path, image_data, width, height, channels, timestamp):
        self.render_product_path = render_product_path
        self.image_data = image_data
        self.width = width
        self.height = height
        self.channels = channels
        self.timestamp = timestamp


class OgnRenderProductLatencyControllerInternalState:
    """Convenience class for maintaining per-node state information"""

    def __init__(self):
        """Instantiate the per-node state information"""
        # (Current time + latency, RenderProductData)
        self.latency_queue = deque()
        self.annotator = None
        self.current_render_product_path = ""
        self.current_data_type = ""
        self.initialized = False

    def initialize_annotator(self, render_product_path: str, data_type: str):
        """Initialize the annotator for the given render product and data type"""
        try:
            if data_type == "rgb":
                self.annotator = rep.AnnotatorRegistry.get_annotator("LdrColor")
            elif data_type == "depth":
                self.annotator = rep.AnnotatorRegistry.get_annotator("DistanceToImagePlane")
            elif data_type == "normals":
                self.annotator = rep.AnnotatorRegistry.get_annotator("Normals")
            elif data_type == "semantic_segmentation":
                self.annotator = rep.AnnotatorRegistry.get_annotator("SemanticSegmentation")
            elif data_type == "instance_segmentation":
                self.annotator = rep.AnnotatorRegistry.get_annotator("InstanceSegmentation")
            else:
                carb.log_error(f"Unsupported data type: {data_type}")
                return False

            # Attach the annotator to the render product
            self.annotator.attach([render_product_path])
            self.current_render_product_path = render_product_path
            self.current_data_type = data_type
            self.initialized = True
            return True

        except Exception as e:
            carb.log_error(f"Failed to initialize annotator: {e}")
            return False

    def capture_current_data(self, render_product_path: str):
        """Capture the current rendered data"""
        if not self.initialized or not self.annotator:
            return None

        try:
            data = self.annotator.get_data()
            if data is None:
                return None

            # Convert to numpy array if needed
            if not isinstance(data, np.ndarray):
                data = np.array(data)

            height, width = data.shape[:2]
            channels = data.shape[2] if len(data.shape) > 2 else 1

            # Convert to uint8 if needed
            if data.dtype != np.uint8:
                if self.current_data_type == "depth":
                    # Normalize depth data to 0-255 range
                    data = ((data - data.min()) / (data.max() - data.min()) * 255).astype(np.uint8)
                elif data.dtype == np.float32 or data.dtype == np.float64:
                    # Assume normalized float data (0-1 range)
                    data = (data * 255).astype(np.uint8)
                else:
                    data = data.astype(np.uint8)

            # Flatten the data
            flattened_data = data.flatten()
            
            return RenderProductData(
                render_product_path=render_product_path,
                image_data=flattened_data,
                width=width,
                height=height,
                channels=channels,
                timestamp=0  # Will be set by caller
            )

        except Exception as e:
            carb.log_error(f"Failed to capture data: {e}")
            return None

    def add_to_queue(self, current_time, latency, render_product_path, data_type):
        """Add data to the latency queue with the current time + latency"""
        # Check if we need to reinitialize annotator
        if (not self.initialized or 
            self.current_render_product_path != render_product_path or 
            self.current_data_type != data_type):
            
            self.cleanup()
            if not self.initialize_annotator(render_product_path, data_type):
                return False

        # Capture current data
        render_data = self.capture_current_data(render_product_path)
        if render_data is None:
            return False

        render_data.timestamp = current_time
        delayed_time = current_time + latency

        # If the queue is empty, append the new data
        if not self.latency_queue:
            self.latency_queue.append((delayed_time, render_data))
            return True
        
        # If the delayed time is smaller than the last item
        # in the queue, skip it.
        if self.latency_queue[-1][0] >= delayed_time:
            return True

        # Otherwise, append the new data
        self.latency_queue.append((delayed_time, render_data))
        return True
    
    def get_from_queue(self, current_time):
        """Get data from queue that should be released at current time"""
        while self.latency_queue and self.latency_queue[0][0] <= current_time:
            # Pop the first item from the queue and return it
            yield self.latency_queue.popleft()

    def cleanup(self):
        """Clean up the annotator"""
        if self.annotator:
            try:
                self.annotator.detach()
            except:
                pass
            self.annotator = None
        self.initialized = False


class OgnRenderProductLatencyController:
    """The Ogn node class"""

    @staticmethod
    def internal_state():
        """Returns an object that contains per-node state information"""
        return OgnRenderProductLatencyControllerInternalState()

    @staticmethod
    def compute(db) -> bool:
        """Compute the output based on inputs and internal state"""
        state = db.per_instance_state

        # === Get the inputs ===
        exec_in = db.inputs.execIn
        render_product_path = db.inputs.renderProductPath
        data_type = db.inputs.dataType
        timestamp_in = db.inputs.timestampIn  # current time
        latency = db.inputs.latency

        if exec_in == og.ExecutionAttributeState.DISABLED:
            return False

        # Add current data to queue
        if not state.add_to_queue(timestamp_in, latency, render_product_path, data_type):
            db.outputs.execOut = og.ExecutionAttributeState.DISABLED
            return False
        
        # Get data that should be released now
        results = list(state.get_from_queue(timestamp_in))
         
        if not results:
            db.outputs.execOut = og.ExecutionAttributeState.DISABLED
            return False

        # Process the most recent result (in case multiple are ready)
        delayed_time, render_data = results[-1]

        # === write outputs ===
        db.outputs.renderProductPathOut = render_data.render_product_path
        db.outputs.imageDataOut = render_data.image_data
        db.outputs.width = render_data.width
        db.outputs.height = render_data.height
        db.outputs.channels = render_data.channels
        db.outputs.timestampOut = [delayed_time]  # Array output
        db.outputs.execOut = og.ExecutionAttributeState.ENABLED

        return True

    @staticmethod
    def release(node):
        """Release the node, cleaning up any resources"""
        try:
            # Get the internal state properly
            from worvai.nodes.latency_nodes.ogn.OgnRenderProductLatencyControllerDatabase import OgnRenderProductLatencyControllerDatabase
            state = OgnRenderProductLatencyControllerDatabase.per_instance_state(node)
            if state:
                state.cleanup()
        except:
            pass
