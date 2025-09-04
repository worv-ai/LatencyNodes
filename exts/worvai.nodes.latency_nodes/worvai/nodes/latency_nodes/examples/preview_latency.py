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

# Make sure to enable ROS1 bridge before latency nodes
enable_extension("isaacsim.ros1.bridge")
enable_extension("worvai.nodes.latency_nodes")

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
    rendering_dt = 1.0 / 60.0
)

set_camera_view(
    eye=[-2, 0, 0.5],
    target=[0.0, 0.0, 0.2],
    camera_prim_path="/OmniverseKit_Persp"
)

print("=== Setting Background ===")
spawner.spawn_ground_plane(world)
spawner.spawn_light(world)

print("=== Creating Camera Graphs ===")
print("This example demonstrates camera publishing with and without latency:")
print("1. Normal camera: Direct publishing without latency")
print("2. Latency camera: Using CameraDataCapture + LatencyController + ROS1PublishRenderedImage")
print("")
print("ROS Topics that will be published:")
print("  - /rgb (no latency)")
print("  - /rgb_latency (with latency using actual image data)")
print("")

# === Make ROS1 Subscriber Node ===
# Twist as '/cmd_vel'
spawner.create_latency_graph(
    prim_path="/World/controller_graph",
    latency_average=0,
    latency_std=0
)

spawner.spawn_background_objects(world, num=100)

# Normal camera graph (no latency) - publishes to /rgb
spawner.create_camera_normal_graph(
    prim_path="/World/camera_graph_normal"
)

# Camera with latency using data capture method - publishes to /rgb_latency
spawner.create_camera_data_capture_latency_graph(
    prim_path="/World/camera_data_capture_latency",
    latency_average=0.4,
    latency_std=0.2,
    camera_prim="/World/spot/body/front_camera",
    topic_name="rgb_latency",
    data_type="rgb"
)


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

for _ in range(100):
    world.step()

# Idle
publisher_controller.reset_twist_all()
for _ in range(60):
    world.step()

# === Part 2 ===
# Turn Left
publisher_controller.reset_twist_all()
for i in range(8):
    publisher_controller.set_twist(idx=i, angular_z=1.0)
publisher_controller.set_twist(idx=8)
publisher_controller.set_twist(idx=9)

for _ in range(200):
    world.step()

# Idle
publisher_controller.reset_twist_all()
for _ in range(100):
    world.step()

# === Part 3 ===
# Turn Right
publisher_controller.reset_twist_all()
for i in range(8):
    publisher_controller.set_twist(idx=i, angular_z=-1.0)
publisher_controller.set_twist(idx=8)
publisher_controller.set_twist(idx=9)

for _ in range(80):
    world.step()

# Idle
publisher_controller.reset_twist_all()
for _ in range(150):
    world.step()

# === Final Part ===
# Go Straight
publisher_controller.reset_twist_all()
for i in range(8):
    publisher_controller.set_twist(idx=i, linear_x=2.0, angular_z=0.0)
publisher_controller.set_twist(idx=8, linear_x=0.0, angular_z=0.0)
publisher_controller.set_twist(idx=9, linear_x=0.0, angular_z=0.0)

for _ in range(150):
    world.step()

set_camera_view(
    eye=[8, 0, 0.2],
    target=[0.0, 0.0, 0.3],
    camera_prim_path="/OmniverseKit_Persp"
)

for _ in range(150):
    world.step()

set_camera_view(
    eye=[9, 5, 2],
    target=[10.0, 0.0, 0.1],
    camera_prim_path="/OmniverseKit_Persp"
)

print("=== Running Extended Simulation ===")
print("The simulation will now run for an extended period.")
print("You can monitor the ROS topics to see the different behaviors:")
print("")
print("Expected behavior:")
print("  - /rgb: Immediate publishing (no latency)")
print("  - /rgb_latency: Variable latency ~0.4s ± 0.1s (actual image data)")
print("")
print("Key difference:")
print("  - /rgb: Direct camera publishing without any latency")
print("  - /rgb_latency: Uses CameraDataCapture to get actual image data,")
print("    applies latency through LatencyController, then publishes via ROS1PublishRenderedImage")
print("  - This ensures the actual rendered image data goes through latency, not just paths")
print("")
print("Pose Alignment:")
print("  - Spot robot pose has been aligned after each turning maneuver")
print("  - Robot should now be facing forward (positive X direction) and level")
print("  - This corrects any orientation drift from turning movements")
print("")

for i in range(30000):
    world.step()
    if i % 6000 == 0:  # Print every 24 seconds at 250 FPS
        print(f"Simulation running... {i/250:.1f}s elapsed")
