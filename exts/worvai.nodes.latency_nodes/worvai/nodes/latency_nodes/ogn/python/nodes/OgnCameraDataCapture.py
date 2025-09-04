"""
Camera Data Capture Node - Captures actual rendered data from render products
"""
import carb
import numpy as np
import omni
import omni.graph.core as og
import omni.replicator.core as rep
import omni.syntheticdata._syntheticdata as sd
from omni.syntheticdata import SyntheticData


class OgnCameraDataCaptureInternalState:
    """Convenience class for maintaining per-node state information"""

    def __init__(self):
        """Instantiate the per-node state information"""
        self.annotator = None
        self.render_product_path = ""
        self.data_type = ""
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
            self.render_product_path = render_product_path
            self.data_type = data_type
            self.initialized = True
            return True

        except Exception as e:
            carb.log_error(f"Failed to initialize annotator: {e}")
            return False

    def _get_ros_encoding(self, data_type: str, dtype, channels: int) -> str:
        """Get the appropriate ROS encoding for the data type"""
        if data_type == "rgb":
            if channels == 3:
                return "rgb8"
            elif channels == 4:
                return "rgba8"
            else:
                return "mono8"
        elif data_type == "depth":
            return "32FC1"  # 32-bit float, 1 channel
        elif data_type in ["semantic_segmentation", "instance_segmentation"]:
            return "32SC1"  # 32-bit signed int, 1 channel (or could be 32UC1 for unsigned)
        elif data_type == "normals":
            return "32FC4"  # 32-bit float, 4 channels
        else:
            # Default to 8-bit formats
            if channels == 1:
                return "mono8"
            elif channels == 3:
                return "rgb8"
            elif channels == 4:
                return "rgba8"
            else:
                return "mono8"

    def get_data(self):
        """Get the current data from the annotator"""
        if not self.initialized or not self.annotator:
            return None, 0, 0, 0, "", ""

        try:
            data = self.annotator.get_data()

            if data is None or data.size == 0:
                return None, 0, 0, 0, "", ""

            # Convert to numpy array if needed
            if not isinstance(data, np.ndarray):
                data = np.array(data)

            height, width = data.shape[:2]
            channels = data.shape[2] if len(data.shape) > 2 else 1

            # Determine encoding and data type based on the annotator type and original data
            original_dtype = str(data.dtype)
            encoding = self._get_ros_encoding(self.data_type, data.dtype, channels)

            # Handle different data types appropriately
            if self.data_type == "rgb":
                # LdrColor returns RGBA uint8, convert to RGB if needed
                if channels == 4:
                    data = data[:, :, :3]  # Remove alpha channel
                    channels = 3
                    encoding = "rgb8"
                flattened_data = data.flatten()

            elif self.data_type == "depth":
                # DistanceToImagePlane returns float32, keep as is for ROS
                # ROS encoding: 32FC1 (32-bit float, 1 channel)
                flattened_data = data.flatten()

            elif self.data_type in ["semantic_segmentation", "instance_segmentation"]:
                # These return uint32, keep as is for ROS
                # ROS encoding: 32SC1 (32-bit signed int, 1 channel) or TYPE_32UC1
                flattened_data = data.flatten()

            elif self.data_type == "normals":
                # Normals return float32, keep as is
                flattened_data = data.flatten()

            else:
                # Default: convert to uint8
                if data.dtype != np.uint8:
                    if data.dtype == np.float32 or data.dtype == np.float64:
                        # Normalize float data to 0-255 range
                        data = ((data - data.min()) / (data.max() - data.min()) * 255).astype(np.uint8)
                    else:
                        data = data.astype(np.uint8)
                flattened_data = data.flatten()

            return flattened_data, width, height, channels, encoding, original_dtype

        except Exception as e:
            carb.log_error(f"Failed to get data from annotator: {e}")
            return None, 0, 0, 0, "", ""

    def cleanup(self):
        """Clean up the annotator"""
        if self.annotator:
            try:
                self.annotator.detach()
            except:
                pass
            self.annotator = None
        self.initialized = False


class OgnCameraDataCapture:
    """The Ogn node class"""

    @staticmethod
    def internal_state():
        """Returns an object that contains per-node state information"""
        return OgnCameraDataCaptureInternalState()

    @staticmethod
    def compute(db) -> bool:
        """Compute the output based on inputs and internal state"""
        state = db.per_instance_state

        # Get inputs
        exec_in = db.inputs.execIn
        render_product_path = db.inputs.renderProductPath
        data_type = db.inputs.dataType
        timestamp_in = db.inputs.timestampIn

        if exec_in == og.ExecutionAttributeState.DISABLED:
            return False

        # Check if we need to reinitialize
        if (not state.initialized or 
            state.render_product_path != render_product_path or 
            state.data_type != data_type):
            
            # Clean up previous annotator
            state.cleanup()
            
            # Initialize new annotator
            if not state.initialize_annotator(render_product_path, data_type):
                db.outputs.execOut = og.ExecutionAttributeState.DISABLED
                return False

        # Get the current data
        image_data, width, height, channels, encoding, data_type_str = state.get_data()

        if image_data is None:
            # No data available yet
            db.outputs.execOut = og.ExecutionAttributeState.DISABLED
            return False

        # Set outputs
        db.outputs.imageData = image_data
        db.outputs.width = width
        db.outputs.height = height
        db.outputs.channels = channels
        db.outputs.encoding = encoding
        db.outputs.dataType = data_type_str
        db.outputs.timestampOut = timestamp_in
        db.outputs.execOut = og.ExecutionAttributeState.ENABLED

        return True

    @staticmethod
    def release(node):
        """Release the node, cleaning up any resources"""
        try:
            # Get the internal state properly
            from worvai.nodes.latency_nodes.ogn.OgnCameraDataCaptureDatabase import OgnCameraDataCaptureDatabase
            state = OgnCameraDataCaptureDatabase.per_instance_state(node)
            if state:
                state.cleanup()
        except:
            pass
