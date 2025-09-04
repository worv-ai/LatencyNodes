from isaacsim.simulation_app import SimulationApp

app = SimulationApp({"headless": False})

import os
import random
import numpy as np
import torch

SEED = 777
os.environ["PYTHONHASHSEED"] = str(SEED)
random.seed(SEED)
np.random.seed(SEED)
torch.manual_seed(SEED) # CPU
if torch.cuda.is_available():
    torch.cuda.manual_seed(SEED) # GPU
    torch.cuda.manual_seed_all(SEED) # Multi-GPU

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


from pxr import UsdGeom
import omni
import omni.usd

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
    rendering_dt = 1.0 / 250.0
)

set_camera_view(
    eye=[-2, 0, 0.5],
    target=[0.0, 0.0, 0.2],
    camera_prim_path="/OmniverseKit_Persp"
)

print("=== Setting Background ===")
spawner.spawn_ground_plane(world)
spawner.spawn_light(world)

# === Make ROS1 Subscriber Node ===
# Twist as '/cmd_vel'
spawner.create_nolatency_graph(
    prim_path="/World/controller_graph",
)

spawner.spawn_background_objects(world, num=100)

world.play()

publisher_controller = spawner.TwistPublisher()
publisher_controller.set_twist(idx=0, linear_x=0.0)
publisher_controller.start_publisher()

# === Scenario ===
for _ in range(300):
    world.step()

# === Part 1 ===
# Turn Right
for i in range(8):
    publisher_controller.set_twist(idx=i, angular_z=-1.0)
publisher_controller.set_twist(idx=8)
publisher_controller.set_twist(idx=9)

for _ in range(300):
    world.step()

# Idle
publisher_controller.reset_twist_all()
for _ in range(200):
    world.step()

# === Part 2 ===
# Turn Left
publisher_controller.reset_twist_all()
for i in range(8):
    publisher_controller.set_twist(idx=i, angular_z=1.0)
publisher_controller.set_twist(idx=8)
publisher_controller.set_twist(idx=9)

for _ in range(600):
    world.step()

# Idle
publisher_controller.reset_twist_all()
for _ in range(200):
    world.step()

# === Part 3 ===
# Turn Right
publisher_controller.reset_twist_all()
for i in range(8):
    publisher_controller.set_twist(idx=i, angular_z=-1.0)
publisher_controller.set_twist(idx=8)
publisher_controller.set_twist(idx=9)

for _ in range(250):
    world.step()

# Idle
publisher_controller.reset_twist_all()
for _ in range(150):
    world.step()

# Turn Right
publisher_controller.reset_twist_all()
for i in range(8):
    publisher_controller.set_twist(idx=i, angular_z=-1.0)
publisher_controller.set_twist(idx=8)
publisher_controller.set_twist(idx=9)

for _ in range(40):
    world.step()

# === Final Part ===
# Go Straight
publisher_controller.reset_twist_all()
for i in range(8):
    publisher_controller.set_twist(idx=i, linear_x=2.0, angular_z=0.0)
publisher_controller.set_twist(idx=8, linear_x=0.0, angular_z=0.0)
publisher_controller.set_twist(idx=9, linear_x=0.0, angular_z=0.0)

for _ in range(500):
    world.step()

set_camera_view(
    eye=[8, 0, 0.2],
    target=[0.0, 0.0, 0.3],
    camera_prim_path="/OmniverseKit_Persp"
)

for _ in range(600):
    world.step()

set_camera_view(
    eye=[9, 5, 2],
    target=[10.0, 0.0, 0.1],
    camera_prim_path="/OmniverseKit_Persp"
)

for _ in range(30000):
    world.step()
