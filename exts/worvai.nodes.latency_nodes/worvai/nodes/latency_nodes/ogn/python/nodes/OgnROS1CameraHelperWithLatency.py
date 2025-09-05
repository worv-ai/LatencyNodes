"""
ROS1 Camera Helper with Latency - A modified version of ROS1CameraHelper that includes built-in latency control
"""
import traceback
from collections import deque
from copy import deepcopy

import carb
import omni
import omni.replicator.core as rep
import omni.syntheticdata
import omni.syntheticdata._syntheticdata as sd
import omni.graph.core as og
from isaacsim.core.nodes import BaseWriterNode, WriterRequest
from omni.kit.viewport.utility import get_viewport_from_window_name
from pxr import Usd


class LatencyData:
    """Container for latency data"""
    def __init__(self, image_data, timestamp, metadata=None):
        self.image_data = image_data
        self.timestamp = timestamp
        self.metadata = metadata or {}


class OgnROS1CameraHelperWithLatencyInternalState(BaseWriterNode):
    def __init__(self):
        self.viewport = None
        self.viewport_name = ""
        self.rv = ""
        self.resetSimulationTimeOnStop = False
        self.publishStepSize = 1
        
        # Latency-specific attributes
        self.latency_queue = deque()
        self.annotator = None
        self.current_render_product_path = ""
        self.current_sensor_type = ""
        self.latency_initialized = False

        super().__init__(initialize=False)

    def initialize_latency_annotator(self, render_product_path: str, sensor_type: str):
        """Initialize the annotator for latency data capture"""
        try:
            if sensor_type == "rgb":
                self.annotator = rep.AnnotatorRegistry.get_annotator("LdrColor")
            elif sensor_type == "depth":
                self.annotator = rep.AnnotatorRegistry.get_annotator("DistanceToImagePlane")
            elif sensor_type == "depth_pcl":
                self.annotator = rep.AnnotatorRegistry.get_annotator("DistanceToImagePlane")
            elif sensor_type == "normals":
                self.annotator = rep.AnnotatorRegistry.get_annotator("Normals")
            elif sensor_type == "semantic_segmentation":
                self.annotator = rep.AnnotatorRegistry.get_annotator("SemanticSegmentation")
            elif sensor_type == "instance_segmentation":
                self.annotator = rep.AnnotatorRegistry.get_annotator("InstanceSegmentation")
            else:
                carb.log_warn(f"Latency capture not supported for sensor type: {sensor_type}")
                return False

            # Attach the annotator to the render product
            self.annotator.attach([render_product_path])
            self.current_render_product_path = render_product_path
            self.current_sensor_type = sensor_type
            self.latency_initialized = True
            return True

        except Exception as e:
            carb.log_error(f"Failed to initialize latency annotator: {e}")
            return False

    def capture_current_data(self, timestamp):
        """Capture the current rendered data for latency processing"""
        if not self.latency_initialized or not self.annotator:
            return None

        try:
            data = self.annotator.get_data()
            if data is None:
                return None

            return LatencyData(
                image_data=data,
                timestamp=timestamp,
                metadata={
                    'sensor_type': self.current_sensor_type,
                    'render_product_path': self.current_render_product_path
                }
            )

        except Exception as e:
            carb.log_error(f"Failed to capture latency data: {e}")
            return None

    def add_to_latency_queue(self, current_time, latency, timestamp):
        """Add data to the latency queue"""
        latency_data = self.capture_current_data(timestamp)
        if latency_data is None:
            return False

        delayed_time = current_time + latency

        # If the queue is empty, append the new data
        if not self.latency_queue:
            self.latency_queue.append((delayed_time, latency_data))
            return True
        
        # If the delayed time is smaller than the last item, skip it
        if self.latency_queue[-1][0] >= delayed_time:
            return True

        # Otherwise, append the new data
        self.latency_queue.append((delayed_time, latency_data))
        return True

    def get_from_latency_queue(self, current_time):
        """Get data from latency queue that should be released"""
        results = []
        while self.latency_queue and self.latency_queue[0][0] <= current_time:
            results.append(self.latency_queue.popleft())
        return results

    def cleanup_latency(self):
        """Clean up latency-related resources"""
        if self.annotator:
            try:
                self.annotator.detach()
            except:
                pass
            self.annotator = None
        self.latency_initialized = False
        self.latency_queue.clear()

    def post_attach(self, writer, render_product):
        try:
            if self.rv != "":
                omni.syntheticdata.SyntheticData.Get().set_node_attributes(
                    self.rv + "IsaacSimulationGate", {"inputs:step": self.publishStepSize}, render_product
                )

            omni.syntheticdata.SyntheticData.Get().set_node_attributes(
                "IsaacReadSimulationTime", {"inputs:resetOnStop": self.resetSimulationTimeOnStop}, render_product
            )

        except:
            pass


class OgnROS1CameraHelperWithLatency:
    @staticmethod
    def internal_state():
        return OgnROS1CameraHelperWithLatencyInternalState()

    @staticmethod
    def compute(db) -> bool:
        if db.inputs.enabled is False:
            if db.per_instance_state.initialized is False:
                return True
            else:
                db.per_instance_state.custom_reset()
                return True

        sensor_type = db.inputs.type
        latency = db.inputs.latency
        timestamp_in = db.inputs.timestampIn
        
        if db.per_instance_state.initialized is False:
            db.per_instance_state.initialized = True
            stage = omni.usd.get_context().get_stage()
            with Usd.EditContext(stage, stage.GetSessionLayer()):
                render_product_path = db.inputs.renderProductPath
                if not render_product_path:
                    carb.log_warn("Render product not valid")
                    db.per_instance_state.initialized = False
                    return False
                if stage.GetPrimAtPath(render_product_path) is None:
                    carb.log_warn("Render product not created yet, retrying on next call")
                    db.per_instance_state.initialized = False
                    return False

                db.per_instance_state.resetSimulationTimeOnStop = False  # Can be made configurable
                db.per_instance_state.publishStepSize = 1

                # Initialize latency annotator
                if latency > 0:
                    if not db.per_instance_state.initialize_latency_annotator(render_product_path, sensor_type):
                        carb.log_warn("Failed to initialize latency annotator, proceeding without latency")

                writer = None
                time_type = ""
                if db.inputs.useSystemTime:
                    time_type = "SystemTime"

                db.per_instance_state.rv = ""

                try:
                    # Create the appropriate writer based on sensor type
                    if sensor_type == "rgb":
                        db.per_instance_state.rv = omni.syntheticdata.SyntheticData.convert_sensor_type_to_rendervar(
                            sd.SensorType.Rgb.name
                        )
                        writer = rep.writers.get(db.per_instance_state.rv + f"ROS1{time_type}PublishImage")
                        writer.initialize(
                            frameId=db.inputs.frameId,
                            nodeNamespace=db.inputs.nodeNamespace,
                            queueSize=db.inputs.queueSize,
                            topicName=db.inputs.topicName,
                        )
                    elif sensor_type == "depth":
                        db.per_instance_state.rv = omni.syntheticdata.SyntheticData.convert_sensor_type_to_rendervar(
                            sd.SensorType.DistanceToImagePlane.name
                        )
                        writer = rep.writers.get(db.per_instance_state.rv + f"ROS1{time_type}PublishImage")
                        writer.initialize(
                            frameId=db.inputs.frameId,
                            nodeNamespace=db.inputs.nodeNamespace,
                            queueSize=db.inputs.queueSize,
                            topicName=db.inputs.topicName,
                        )
                    # Add other sensor types as needed...
                    else:
                        carb.log_error("type is not supported")
                        db.per_instance_state.initialized = False
                        return False

                    if writer is not None:
                        db.per_instance_state.append_writer(writer)

                    # Apply latency if specified
                    if latency > 0 and db.per_instance_state.latency_initialized:
                        # Add current data to latency queue
                        db.per_instance_state.add_to_latency_queue(timestamp_in, latency, timestamp_in)
                        
                        # Check if any latency data is ready to be published
                        ready_data = db.per_instance_state.get_from_latency_queue(timestamp_in)
                        if ready_data:
                            # Attach writers only when latency data is ready
                            db.per_instance_state.attach_writers(render_product_path)
                    else:
                        # No latency, attach writers immediately
                        db.per_instance_state.attach_writers(render_product_path)

                except Exception as e:
                    print(traceback.format_exc())
                    pass
        else:
            # Handle latency processing for subsequent frames
            if latency > 0 and db.per_instance_state.latency_initialized:
                db.per_instance_state.add_to_latency_queue(timestamp_in, latency, timestamp_in)
                
                # Check if any latency data is ready
                ready_data = db.per_instance_state.get_from_latency_queue(timestamp_in)
                if not ready_data:
                    # No data ready yet, disable execution
                    db.outputs.execOut = og.ExecutionAttributeState.DISABLED
                    return False

        db.outputs.execOut = og.ExecutionAttributeState.ENABLED
        return True

    @staticmethod
    def release_instance(node, graph_instance_id):
        try:
            from worvai.nodes.latency_nodes.ogn.OgnROS1CameraHelperWithLatencyDatabase import OgnROS1CameraHelperWithLatencyDatabase
            state = OgnROS1CameraHelperWithLatencyDatabase.per_instance_state(node)
        except Exception:
            state = None
            pass

        if state is not None:
            state.cleanup_latency()
            state.reset()
