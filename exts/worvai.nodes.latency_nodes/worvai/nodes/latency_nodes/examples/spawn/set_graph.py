import omni.graph.core as og

def create_test_graph():
    keys = og.Controller.Keys

    og.Controller.edit(
        {
            "graph_path": "/World/controller_graph",
            "evaluator_name": "execution"
        },
        {
            keys.CREATE_NODES: [
                ("OnPlaybackTick", "omni.graph.action.OnPlaybackTick"),
                ("ExampleSpot", "worvai.nodes.latency_nodes.ExampleSpot"),
                ("ConstVec3", "omni.graph.nodes.ConstantVector3d")
            ],
            keys.SET_VALUES: [
                ("ConstVec3.inputs:value", [1.0, 0.0, 0.0]),
            ],
            keys.CONNECT: [
                ("OnPlaybackTick.outputs:tick", "ExampleSpot.inputs:execIn"),
                ("ConstVec3.inputs:value", "ExampleSpot.inputs:command"),
            ],
        },
    )

def create_nolatency_graph(prim_path):
    keys = og.Controller.Keys

    graph, nodes, _, _ = og.Controller.edit(
        {
            "graph_path": f"{prim_path}",
            "evaluator_name": "execution"
        },
        {
            keys.CREATE_NODES: [
                ("OnPlaybackTick", "omni.graph.action.OnPlaybackTick"),
                ("ROS1SubscribeTwist", "isaacsim.ros1.bridge.ROS1SubscribeTwist"),
                ("GetAngularZComponent", "omni.graph.nodes.BreakVector3"),
                ("GetLinearXYComponent", "omni.graph.nodes.BreakVector3"),
                ("GetCommand", "omni.graph.nodes.MakeVector3"),
                ("ExampleSpot", "worvai.nodes.latency_nodes.ExampleSpot"),
            ],
            keys.SET_VALUES: [
            ],
            keys.CONNECT: [
                ("OnPlaybackTick.outputs:tick", "ROS1SubscribeTwist.inputs:execIn"),
                ("ROS1SubscribeTwist.outputs:execOut", "ExampleSpot.inputs:execIn"),

                ("ROS1SubscribeTwist.outputs:angularVelocity", "GetAngularZComponent.inputs:tuple"),
                ("ROS1SubscribeTwist.outputs:linearVelocity", "GetLinearXYComponent.inputs:tuple"),
                ("GetAngularZComponent.outputs:z", "GetCommand.inputs:z"),
                ("GetLinearXYComponent.outputs:x", "GetCommand.inputs:x"),
                ("GetLinearXYComponent.outputs:y", "GetCommand.inputs:y"),

                ("GetCommand.outputs:tuple", "ExampleSpot.inputs:command")
            ],
        },
    )

def create_latency_graph(prim_path, latency_average, latency_std):
    keys = og.Controller.Keys

    graph, nodes, _, _ = og.Controller.edit(
        {
            "graph_path": f"{prim_path}",
            "evaluator_name": "execution"
        },
        {
            keys.CREATE_NODES: [
                ("OnPlaybackTick", "omni.graph.action.OnPlaybackTick"),
                ("ROS1SubscribeTwist", "isaacsim.ros1.bridge.ROS1SubscribeTwist"),
                ("GetAngularZComponent", "omni.graph.nodes.BreakVector3"),
                ("GetLinearXYComponent", "omni.graph.nodes.BreakVector3"),
                ("GetCommand", "omni.graph.nodes.MakeVector3"),
                ("ExampleSpot", "worvai.nodes.latency_nodes.ExampleSpot"),
                ("NormDistLatency", "worvai.nodes.latency_nodes.NormalDistributionSampler"),
                ("LatencyController", "worvai.nodes.latency_nodes.LatencyController"),
            ],
            keys.SET_VALUES: [
                ("NormDistLatency.inputs:_average", latency_average),
                ("NormDistLatency.inputs:_standardDeviation", latency_std),
            ],
            keys.CONNECT: [
                ("OnPlaybackTick.outputs:tick", "ROS1SubscribeTwist.inputs:execIn"),

                ("ROS1SubscribeTwist.outputs:execOut", "NormDistLatency.inputs:execIn"),
                ("ROS1SubscribeTwist.outputs:angularVelocity", "GetAngularZComponent.inputs:tuple"),
                ("ROS1SubscribeTwist.outputs:linearVelocity", "GetLinearXYComponent.inputs:tuple"),
                ("GetAngularZComponent.outputs:z", "GetCommand.inputs:z"),
                ("GetLinearXYComponent.outputs:x", "GetCommand.inputs:x"),
                ("GetLinearXYComponent.outputs:y", "GetCommand.inputs:y"),

                ("NormDistLatency.outputs:execOut", "LatencyController.inputs:execIn"),
                ("NormDistLatency.outputs:latencyOut", "LatencyController.inputs:latency"),
                ("GetCommand.outputs:tuple", "LatencyController.inputs:dataIn"),
                ("OnPlaybackTick.outputs:time", "LatencyController.inputs:timestampIn"),

                ("LatencyController.outputs:loopBody", "ExampleSpot.inputs:execIn"),
                ("LatencyController.outputs:element", "ExampleSpot.inputs:command"),
            ],
        },
    )

def create_camera_latency_graph(prim_path, latency_average, latency_std):
    keys = og.Controller.Keys

    graph, nodes, _, _ = og.Controller.edit(
        {
            "graph_path": f"{prim_path}",
            "evaluator_name": "execution"
        },
        {
            keys.CREATE_NODES: [
                ("OnPlaybackTick", "omni.graph.action.OnPlaybackTick"),
                ("RenderCamera", "isaacsim.core.nodes.IsaacCreateRenderProduct"),
                ("ROS1CameraPublisher", "isaacsim.ros1.bridge.ROS1CameraHelper"),
                ("NormDistLatency", "worvai.nodes.latency_nodes.NormalDistributionSampler"),
                ("LatencyController", "worvai.nodes.latency_nodes.LatencyController"),
                ("IsaacTimeReader", "isaacsim.core.nodes.IsaacReadSimulationTime"),
            ],
            keys.SET_VALUES: [
                ("RenderCamera.inputs:height", 1080),
                ("RenderCamera.inputs:width", 1920),
                ("RenderCamera.inputs:cameraPrim", "/World/spot/body/front_camera"),

                ("NormDistLatency.inputs:_average", latency_average),
                ("NormDistLatency.inputs:_standardDeviation", latency_std),

                ("ROS1CameraPublisher.inputs:topicName", "rgb_front_latency"),
            ],
            keys.CONNECT: [
                ("OnPlaybackTick.outputs:tick", "RenderCamera.inputs:execIn"),
                ("RenderCamera.outputs:execOut", "NormDistLatency.inputs:execIn"),
                ("NormDistLatency.outputs:execOut", "LatencyController.inputs:execIn"),
                ("LatencyController.outputs:loopBody", "ROS1CameraPublisher.inputs:execIn"),

                ("RenderCamera.outputs:renderProductPath", "LatencyController.inputs:dataIn"),
                ("NormDistLatency.outputs:latencyOut", "LatencyController.inputs:latency"),
                ("IsaacTimeReader.outputs:simulationTime", "LatencyController.inputs:timestampIn"),
                ("LatencyController.outputs:element", "ROS1CameraPublisher.inputs:renderProductPath"),
            ]
        }
    )

def create_camera_normal_graph(
    prim_path,
    camera_prim="/World/spot/body/front_camera",
    topic_name="rgb"
):
    keys = og.Controller.Keys

    graph, nodes, _, _ = og.Controller.edit(
        {
            "graph_path": f"{prim_path}",
            "evaluator_name": "execution"
        },
        {
            keys.CREATE_NODES: [
                ("OnPlaybackTick", "omni.graph.action.OnPlaybackTick"),
                ("RenderCamera", "isaacsim.core.nodes.IsaacCreateRenderProduct"),
                ("ROS1CameraPublisher", "isaacsim.ros1.bridge.ROS1CameraHelper"),
            ],
            keys.SET_VALUES: [
                ("RenderCamera.inputs:height", 1080),
                ("RenderCamera.inputs:width", 1920),
                ("RenderCamera.inputs:cameraPrim", camera_prim),

                ("ROS1CameraPublisher.inputs:topicName", topic_name),
            ],
            keys.CONNECT: [
                ("OnPlaybackTick.outputs:tick", "RenderCamera.inputs:execIn"),
                ("RenderCamera.outputs:execOut", "ROS1CameraPublisher.inputs:execIn"),

                ("RenderCamera.outputs:renderProductPath", "ROS1CameraPublisher.inputs:renderProductPath"),
            ]
        }
    )

def create_camera_data_capture_latency_graph(
    prim_path,
    latency_average,
    latency_std,
    camera_prim="/World/spot/body/front_camera",
    topic_name="rgb_latency",
    data_type="rgb"
):
    keys = og.Controller.Keys

    graph, nodes, _, _ = og.Controller.edit(
        {
            "graph_path": f"{prim_path}",
            "evaluator_name": "execution"
        },
        {
            keys.CREATE_NODES: [
                ("OnPlaybackTick", "omni.graph.action.OnPlaybackTick"), 
                ("RenderCamera", "isaacsim.core.nodes.IsaacCreateRenderProduct"),
                ("CameraDataCapture", "worvai.nodes.latency_nodes.CameraDataCapture"),
                ("NormDistLatency", "worvai.nodes.latency_nodes.NormalDistributionSampler"),
                ("LatencyController", "worvai.nodes.latency_nodes.LatencyController"),
                ("ROS1PublishRenderedImage", "worvai.nodes.latency_nodes.ROS1PublishRenderedImage"),
                ("IsaacTimeReader", "isaacsim.core.nodes.IsaacReadSimulationTime"),
            ],
            keys.SET_VALUES: [
                # Camera settings
                ("RenderCamera.inputs:height", 720),
                ("RenderCamera.inputs:width", 1280),
                ("RenderCamera.inputs:cameraPrim", camera_prim),

                # Data capture settings
                ("CameraDataCapture.inputs:dataType", data_type),

                # Latency settings
                ("NormDistLatency.inputs:_average", latency_average),
                ("NormDistLatency.inputs:_standardDeviation", latency_std),

                # ROS publisher settings
                ("ROS1PublishRenderedImage.inputs:topicName", topic_name),
                ("ROS1PublishRenderedImage.inputs:frameId", "camera_frame"),
                ("ROS1PublishRenderedImage.inputs:encoding", "rgb8" if data_type == "rgb" else "32FC1"),
                ("ROS1PublishRenderedImage.inputs:queueSize", 10),
            ],
            keys.CONNECT: [
                # Main execution flow
                ("OnPlaybackTick.outputs:tick", "RenderCamera.inputs:execIn"),
                ("RenderCamera.outputs:execOut", "CameraDataCapture.inputs:execIn"),
                ("CameraDataCapture.outputs:execOut", "NormDistLatency.inputs:execIn"),
                ("NormDistLatency.outputs:execOut", "LatencyController.inputs:execIn"),
                ("LatencyController.outputs:loopBody", "ROS1PublishRenderedImage.inputs:execIn"),

                # Data flow
                ("RenderCamera.outputs:renderProductPath", "CameraDataCapture.inputs:renderProductPath"),
                ("IsaacTimeReader.outputs:simulationTime", "CameraDataCapture.inputs:timestampIn"),
                ("IsaacTimeReader.outputs:simulationTime", "LatencyController.inputs:timestampIn"),

                # Latency control
                ("CameraDataCapture.outputs:imageData", "LatencyController.inputs:dataIn"),
                ("NormDistLatency.outputs:latencyOut", "LatencyController.inputs:latency"),

                # Image publishing (direct from LatencyController element output)
                ("LatencyController.outputs:element", "ROS1PublishRenderedImage.inputs:imageData"),
                ("CameraDataCapture.outputs:width", "ROS1PublishRenderedImage.inputs:width"),
                ("CameraDataCapture.outputs:height", "ROS1PublishRenderedImage.inputs:height"),
                ("CameraDataCapture.outputs:channels", "ROS1PublishRenderedImage.inputs:channels"),
                ("CameraDataCapture.outputs:encoding", "ROS1PublishRenderedImage.inputs:encoding"),
                ("LatencyController.outputs:elementTimestamp", "ROS1PublishRenderedImage.inputs:timestampIn"),
            ]
        }
    )

    return graph, nodes

def create_camera_render_product_latency_graph(
    prim_path,
    latency_average,
    latency_std,
    camera_prim="/World/spot/body/front_camera",
    topic_name="rgb",
    data_type="rgb"
):
    keys = og.Controller.Keys

    graph, nodes, _, _ = og.Controller.edit(
        {
            "graph_path": f"{prim_path}",
            "evaluator_name": "execution"
        },
        {
            keys.CREATE_NODES: [
                ("OnPlaybackTick", "omni.graph.action.OnPlaybackTick"),
                ("RenderCamera", "isaacsim.core.nodes.IsaacCreateRenderProduct"),
                ("RenderProductLatencyController", "worvai.nodes.latency_nodes.RenderProductLatencyController"),
                ("ROS1PublishRenderedImage", "worvai.nodes.latency_nodes.ROS1PublishRenderedImage"),
                ("IsaacTimeReader", "isaacsim.core.nodes.IsaacReadSimulationTime"),
            ],
            keys.SET_VALUES: [
                # Camera settings
                ("RenderCamera.inputs:height", 720),
                ("RenderCamera.inputs:width", 1280),
                ("RenderCamera.inputs:cameraPrim", camera_prim),

                # Render product latency controller settings
                ("RenderProductLatencyController.inputs:dataType", data_type),
                ("RenderProductLatencyController.inputs:latency", latency_average),  # Fixed latency for simplicity

                # ROS publisher settings
                ("ROS1PublishRenderedImage.inputs:topicName", topic_name),
                ("ROS1PublishRenderedImage.inputs:frameId", "camera_frame"),
                ("ROS1PublishRenderedImage.inputs:encoding", "rgb8" if data_type == "rgb" else "32FC1"),
                ("ROS1PublishRenderedImage.inputs:queueSize", 10),
            ],
            keys.CONNECT: [
                # Main execution flow
                ("OnPlaybackTick.outputs:tick", "RenderCamera.inputs:execIn"),
                ("RenderCamera.outputs:execOut", "RenderProductLatencyController.inputs:execIn"),
                # Direct connection using integrated ForEach functionality
                ("RenderProductLatencyController.outputs:loopBody", "ROS1PublishRenderedImage.inputs:execIn"),

                # Data flow
                ("RenderCamera.outputs:renderProductPath", "RenderProductLatencyController.inputs:renderProductPath"),
                ("IsaacTimeReader.outputs:simulationTime", "RenderProductLatencyController.inputs:timestampIn"),

                # Latency control and image publishing
                ("RenderProductLatencyController.outputs:element", "ROS1PublishRenderedImage.inputs:imageData"),
                ("RenderProductLatencyController.outputs:width", "ROS1PublishRenderedImage.inputs:width"),
                ("RenderProductLatencyController.outputs:height", "ROS1PublishRenderedImage.inputs:height"),
                ("RenderProductLatencyController.outputs:channels", "ROS1PublishRenderedImage.inputs:channels"),
                ("RenderProductLatencyController.outputs:elementTimestamp", "ROS1PublishRenderedImage.inputs:timestampIn"),
            ]
        }
    )

    return graph, nodes

