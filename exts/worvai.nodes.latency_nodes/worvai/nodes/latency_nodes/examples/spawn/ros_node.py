import threading
import time
from copy import deepcopy
import rospy
from geometry_msgs.msg import Twist


class TwistPublisher:
    def __init__(self):
        """Initialize the publisher with thread-safe message storage"""
        self._msg_lock = threading.Lock()
        self._msg_list: list[Twist] = [Twist()]
        self._msg_list[0].linear.x = 0.0
        self._msg_list[0].linear.y = 0.0
        self._msg_list[0].linear.z = 0.0
        self._msg_list[0].angular.x = 0.0
        self._msg_list[0].angular.y = 0.0
        self._msg_list[0].angular.z = 0.0

        self._publisher_thread = None
        self._is_running = False
        self._publisher = None
        
    def set_twist(
        self,
        idx=0,
        linear_x=None, linear_y=None, linear_z=None, 
        angular_x=None, angular_y=None, angular_z=None
    ):
        """
        Update the Twist message that will be published.
        
        Args:
            linear_x, linear_y, linear_z: Linear velocities
            angular_x, angular_y, angular_z: Angular velocities
        """
        with self._msg_lock:
            while idx >= len(self._msg_list):
                self._msg_list.append(Twist())

            msg = self._msg_list[idx]
            if linear_x is not None: msg.linear.x = linear_x
            if linear_y is not None: msg.linear.y = linear_y
            if linear_z is not None: msg.linear.z = linear_z
            if angular_x is not None: msg.angular.x = angular_x
            if angular_y is not None: msg.angular.y = angular_y
            if angular_z is not None: msg.angular.z = angular_z

    def reset_twist_all(self):
        """
        For convenience, reset all Twist msg to zero
        """
        with self._msg_lock:
            for msg in self._msg_list:
                msg.linear.x = 0.0
                msg.linear.y = 0.0
                msg.linear.z = 0.0
                msg.angular.x = 0.0
                msg.angular.y = 0.0
                msg.angular.z = 0.0

    def get_twist_by_index(self, idx):
        """
        Get a copy of the Twist message at a specific index.

        Args:
            idx (int): Index of the Twist message to retrieve

        Returns:
            Twist: Copy of the Twist message at the specified index
        """
        with self._msg_lock:
            if 0 <= idx < len(self._msg_list):
                return self._msg_list[idx]
            else:
                raise IndexError(f"No Twist message at index {idx}")

    def start_publisher(self, topic="/cmd_vel", rate_hz=30):
        """
        Starts a background thread that publishes the current Twist message.
        
        Args:
            topic (str): Topic name to publish to
            rate_hz (int): Publishing frequency in Hz
        """
        if self._is_running:
            print("Publisher already running!")
            return self._publisher_thread
        
        def _publisher_loop():
            try:
                rospy.init_node(
                    "cmd_vel_publisher", anonymous=True, disable_signals=True
                )
                print("ROS node initialized")
            except rospy.ROSException as e:
                print(f"ROS node already initialized: {e}")

            self._publisher = rospy.Publisher(topic, Twist, queue_size=10)
            rate = rospy.Rate(rate_hz)

            rospy.loginfo(f"Publishing on {topic} at {rate_hz} Hz")

            rospy.sleep(0.5)

            current_index = 0
            while not rospy.is_shutdown() and self._is_running:
                # Get a thread-safe copy of the message list to iterate over
                with self._msg_lock:
                    list_copy = list(self._msg_list)
                
                if not list_copy:
                    rate.sleep()
                    continue

                # Cycle through the index
                current_index %= len(list_copy)
                
                # Publish the message at the current index
                msg_to_publish = list_copy[current_index]
                self._publisher.publish(msg_to_publish)
                
                current_index += 1
                rate.sleep()
            
            rospy.loginfo("Publisher loop has ended.")

        self._is_running = True
        self._publisher_thread = threading.Thread(
            target=_publisher_loop, daemon=True
        )
        self._publisher_thread.start()
        return self._publisher_thread
    
    def stop_publisher(self):
        """Stop the publishing thread"""
        self._is_running = False
        if self._publisher_thread and self._publisher_thread.is_alive():
            self._publisher_thread.join(timeout=2.0)
        print("Publisher stopped")
    
    def is_running(self):
        """Check if publisher is running"""
        return (
            self._is_running and
            self._publisher_thread and
            self._publisher_thread.is_alive()
        )

