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

def create_latency_graph(prim_path):
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
                ("ForEach", "omni.graph.action.ForEach"),
            ],
            keys.SET_VALUES: [
                ("NormDistLatency.inputs:_average", 0.02),
                ("NormDistLatency.inputs:_standardDeviation", 0.01),
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

                ("LatencyController.outputs:execOut", "ForEach.inputs:execIn"),
                ("LatencyController.outputs:dataOut", "ForEach.inputs:arrayIn"),

                ("ForEach.outputs:loopBody", "ExampleSpot.inputs:execIn"),
                ("ForEach.outputs:element", "ExampleSpot.inputs:command"),
            ],
        },
    )
