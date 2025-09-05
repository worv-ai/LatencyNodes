[] ROS1PublishImage node already exists, but why do we need the ROS1PublishRenderedImage node?
    - To control some issues,
        - since we capture the data using CameraDataCapture node, the data type is uchar[], not string (path)
        - ROS1PublishImage node supports the uchar[], but the channels could be problematic.
        - More testing is needed.
