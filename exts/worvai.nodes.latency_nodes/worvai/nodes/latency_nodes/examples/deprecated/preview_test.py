from isaacsim.simulation_app import SimulationApp

app = SimulationApp({"headless": False})

import sys

import omni
import omni.usd
import carb
from pxr import Sdf, UsdLux, UsdGeom, Gf
import numpy as np

# from isaacsim import SimulationApp
from isaacsim.core.api import World
from isaacsim.core.utils.viewports import set_camera_view
from isaacsim.storage.native import get_assets_root_path
from isaacsim.robot.policy.examples.robots.spot import SpotFlatTerrainPolicy
import isaacsim.core.utils.extensions as extensions_utils

extensions_utils.enable_extension("worvai.nodes.latency_nodes")
extensions_utils.enable_extension("isaacsim.ros1.bridge")

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

set_camera_view(eye=[-5, 0, 2], target=[0.0, 0.0, 0.2], camera_prim_path="/OmniverseKit_Persp")

print("=== Setting Background ===")
spawner.spawn_ground_plane(world)
spawner.spawn_light(world)

for _ in range(60):
    world.step(render=True)

print("=== Setting Robot ===")        

spot_controller = spawner.SpotController()
spot_controller.setup()

spot = spot_controller.robot

print(f"World dt is {world.get_physics_dt()}")
world.play()

# === Warm Up ===
for _ in range(300):
    world.step()

spot_controller.post_setup(world)

for i in range(600):  # ~1 second at 60Hz
    world.step()
    print(f"Current time is {world.current_time}", end="\r")

spot_controller.set_base_command(np.array([1.0, 0.0, 0.0]))  # [v_x, v_y, w_z]

for i in range(30000):  # ~1 second at 60Hz
    world.step()
    print(f"Current time is {world.current_time}, with vel {spot.get_linear_velocity()}", end="\r")

world.stop()
