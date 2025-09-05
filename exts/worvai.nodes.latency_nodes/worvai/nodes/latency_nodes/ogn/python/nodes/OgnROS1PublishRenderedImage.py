"""
ROS1 Publish Rendered Image - Publishes image data from latency controllers to ROS1
"""
import carb
import numpy as np
import omni.graph.core as og

try:
    import rospy
    from sensor_msgs.msg import Image
    from std_msgs.msg import Header
    ROS_AVAILABLE = True
except ImportError:
    ROS_AVAILABLE = False
    carb.log_warn("ROS1 not available. ROS1 Publish Rendered Image will not function.")


class OgnROS1PublishRenderedImageInternalState:
    """Convenience class for maintaining per-node state information"""

    def __init__(self):
        """Instantiate the per-node state information"""
        self.publisher = None
        self.topic_name = ""
        self.node_namespace = ""
        self.queue_size = 10
        self.initialized = False
        self.ros_node_initialized = False

    def initialize_ros_node(self):
        """Initialize ROS node if not already initialized"""
        if not ROS_AVAILABLE:
            return False
            
        try:
            if not rospy.get_node_uri():
                rospy.init_node('isaac_sim_custom_image_publisher', anonymous=True)
            self.ros_node_initialized = True
            return True
        except Exception as e:
            carb.log_error(f"Failed to initialize ROS node: {e}")
            return False

    def initialize_publisher(self, topic_name: str, node_namespace: str, queue_size: int):
        """Initialize the ROS publisher"""
        if not ROS_AVAILABLE:
            carb.log_error("ROS1 not available")
            return False

        try:
            if not self.ros_node_initialized:
                if not self.initialize_ros_node():
                    return False

            # Create full topic name with namespace
            full_topic_name = topic_name
            if node_namespace:
                full_topic_name = f"{node_namespace}/{topic_name}"

            # Create publisher
            self.publisher = rospy.Publisher(full_topic_name, Image, queue_size=queue_size)
            
            self.topic_name = topic_name
            self.node_namespace = node_namespace
            self.queue_size = queue_size
            self.initialized = True
            
            carb.log_info(f"Initialized ROS1 Image Publisher on topic: {full_topic_name}")
            return True

        except Exception as e:
            carb.log_error(f"Failed to initialize ROS publisher: {e}")
            return False

    def publish_image(self, image_data, width, height, channels, encoding, frame_id, timestamp, use_system_time):
        """Publish image data to ROS"""
        if not self.initialized or not self.publisher:
            return False

        try:
            # Determine the appropriate numpy dtype based on encoding
            if encoding in ["rgb8", "bgr8", "rgba8", "mono8"]:
                dtype = np.uint8
                bytes_per_pixel = 1
            elif encoding in ["32FC1", "32FC3", "32FC4"]:
                dtype = np.float32
                bytes_per_pixel = 4
            elif encoding in ["32SC1", "32SC3", "32SC4"]:
                dtype = np.int32
                bytes_per_pixel = 4
            elif encoding in ["32UC1", "32UC3", "32UC4"]:
                dtype = np.uint32
                bytes_per_pixel = 4
            elif encoding in ["16UC1", "16UC3", "16UC4"]:
                dtype = np.uint16
                bytes_per_pixel = 2
            elif encoding in ["16SC1", "16SC3", "16SC4"]:
                dtype = np.int16
                bytes_per_pixel = 2
            else:
                # Default to uint8
                dtype = np.uint8
                bytes_per_pixel = 1

            # Reshape the flattened image data
            if channels == 1:
                image_array = np.array(image_data, dtype=dtype).reshape((height, width))
            else:
                image_array = np.array(image_data, dtype=dtype).reshape((height, width, channels))

            # Create ROS Image message
            ros_image = Image()
            ros_image.header = Header()
            ros_image.header.frame_id = frame_id

            # Set timestamp
            if use_system_time:
                ros_image.header.stamp = rospy.Time.now()
            else:
                # Convert simulation timestamp to ROS time
                ros_image.header.stamp = rospy.Time.from_sec(timestamp)

            ros_image.width = width
            ros_image.height = height
            ros_image.encoding = encoding

            # Handle different encodings
            if encoding == "rgb8" and channels == 3:
                ros_image.data = image_array.tobytes()
                ros_image.step = width * 3 * bytes_per_pixel
            elif encoding == "bgr8" and channels == 3:
                # Convert RGB to BGR if we have cv2 available
                try:
                    import cv2
                    bgr_image = cv2.cvtColor(image_array, cv2.COLOR_RGB2BGR)
                    ros_image.data = bgr_image.tobytes()
                except ImportError:
                    # Fallback: manual BGR conversion
                    bgr_image = image_array[:, :, [2, 1, 0]]  # Swap R and B channels
                    ros_image.data = bgr_image.tobytes()
                ros_image.step = width * 3 * bytes_per_pixel
            elif encoding == "mono8" and channels == 1:
                ros_image.data = image_array.tobytes()
                ros_image.step = width * bytes_per_pixel
            elif encoding == "rgba8" and channels == 4:
                ros_image.data = image_array.tobytes()
                ros_image.step = width * 4 * bytes_per_pixel
            elif encoding in ["32FC1", "32SC1", "32UC1", "16UC1", "16SC1"] and channels == 1:
                # Single channel non-8-bit data
                ros_image.data = image_array.tobytes()
                ros_image.step = width * bytes_per_pixel
            elif encoding in ["32FC3", "32SC3", "32UC3", "16UC3", "16SC3"] and channels == 3:
                # Three channel non-8-bit data
                ros_image.data = image_array.tobytes()
                ros_image.step = width * 3 * bytes_per_pixel
            elif encoding in ["32FC4", "32SC4", "32UC4", "16UC4", "16SC4"] and channels == 4:
                # Four channel non-8-bit data
                ros_image.data = image_array.tobytes()
                ros_image.step = width * 4 * bytes_per_pixel
            else:
                # Default: assume the data is already in the correct format
                ros_image.data = image_array.tobytes()
                ros_image.step = width * channels * bytes_per_pixel

            # Publish the message
            self.publisher.publish(ros_image)
            return True

        except Exception as e:
            carb.log_error(f"Failed to publish image: {e}")
            return False

    def cleanup(self):
        """Clean up ROS resources"""
        if self.publisher:
            try:
                self.publisher.unregister()
            except:
                pass
            self.publisher = None
        self.initialized = False


class OgnROS1PublishRenderedImage:
    """The Ogn node class"""

    @staticmethod
    def internal_state():
        """Returns an object that contains per-node state information"""
        return OgnROS1PublishRenderedImageInternalState()

    @staticmethod
    def compute(db) -> bool:
        """Compute the output based on inputs and internal state"""
        state = db.per_instance_state

        # Get inputs
        exec_in = db.inputs.execIn
        image_data = db.inputs.imageData
        width = db.inputs.width
        height = db.inputs.height
        channels = db.inputs.channels
        encoding = db.inputs.encoding
        frame_id = db.inputs.frameId
        topic_name = db.inputs.topicName
        node_namespace = db.inputs.nodeNamespace
        queue_size = db.inputs.queueSize
        timestamp_in = db.inputs.timestampIn
        use_system_time = db.inputs.useSystemTime

        if exec_in == og.ExecutionAttributeState.DISABLED:
            return False

        # Check if we need to initialize or reinitialize
        if (not state.initialized or 
            state.topic_name != topic_name or 
            state.node_namespace != node_namespace or 
            state.queue_size != queue_size):
            
            state.cleanup()
            if not state.initialize_publisher(topic_name, node_namespace, queue_size):
                db.outputs.execOut = og.ExecutionAttributeState.DISABLED
                return False

        # Validate inputs
        if image_data is None or width <= 0 or height <= 0 or channels <= 0:
            carb.log_warn("Invalid image data or dimensions")
            db.outputs.execOut = og.ExecutionAttributeState.DISABLED
            return False

        # Check if image data size matches expected size
        expected_size = width * height * channels
        if len(image_data) != expected_size:
            carb.log_warn(f"Image data size mismatch. Expected: {expected_size}, Got: {len(image_data)}")
            db.outputs.execOut = og.ExecutionAttributeState.DISABLED
            return False

        # Publish the image
        if not state.publish_image(image_data, width, height, channels, encoding, 
                                 frame_id, timestamp_in, use_system_time):
            db.outputs.execOut = og.ExecutionAttributeState.DISABLED
            return False

        db.outputs.execOut = og.ExecutionAttributeState.ENABLED
        return True

    @staticmethod
    def release(node):
        """Release the node, cleaning up any resources"""
        try:
            from worvai.nodes.latency_nodes.ogn.OgnCustomROS1ImagePublisherDatabase import OgnCustomROS1ImagePublisherDatabase
            state = OgnCustomROS1ImagePublisherDatabase.per_instance_state(node)
            if state:
                state.cleanup()
        except:
            pass
