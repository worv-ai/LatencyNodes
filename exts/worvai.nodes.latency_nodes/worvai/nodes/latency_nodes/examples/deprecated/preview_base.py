from isaacsim.simulation_app import SimulationApp

app = SimulationApp({"headless": False})

from isaacsim.core.utils.extensions import enable_extension

enable_extension("omni.kit.widget.graph")
enable_extension("omni.graph.core")
enable_extension("omni.graph.action")
enable_extension("omni.graph.action_nodes")
enable_extension("omni.graph.bundle.action")
enable_extension("omni.graph.window.core")
enable_extension("omni.graph.window.action")
enable_extension("worvai.nodes.latency_nodes")
enable_extension("isaacsim.ros1.bridge")

import sys

import omni
import omni.usd
import carb
from pxr import Sdf, UsdLux, UsdGeom, Gf
import numpy as np

# from isaacsim import SimulationApp
from isaacsim.core.api import World
from isaacsim.storage.native import get_assets_root_path
from isaacsim.core.utils.viewports import set_camera_view

import worvai.nodes.latency_nodes.examples.spawn as spawner

ASSET_ROOT_PATH = get_assets_root_path()
print(f"Asset root path is {ASSET_ROOT_PATH}")

stage = omni.usd.get_context().get_stage()
timeline = omni.timeline.get_timeline_interface()

world = World(
    physics_dt = 1.0 / 500.0,
    stage_units_in_meters = 1.0,
    rendering_dt = 1.0 / 100.0
)

set_camera_view(
    eye=[-5, 0, 2],
    target=[0.0, 0.0, 0.2],
    camera_prim_path="/OmniverseKit_Persp"
)

print("=== Setting Background ===")
spawner.spawn_ground_plane(world)
spawner.spawn_light(world)

spawner.create_test_graph()

world.play()

for _ in range(1000000):
    world.step()


