import numpy as np
from pxr import Gf
import omni.graph.core as og
from isaacsim.core.api import World
import isaacsim.core.utils.rotations as rot_utils
from isaacsim.sensors.camera import Camera
from isaacsim.core.prims import SingleArticulation
from isaacsim.robot.policy.examples.robots.spot import SpotFlatTerrainPolicy


class OgnExampleSpotInternalState:
	"""Internal state for Exponential Distribution sampler"""

	def __init__(self):
		"""Instantiate the per-node state information"""
		self.world = World()
		self.initialized = False
		self._base_command = np.array([0.0, 0.0, 0.0])

		self.spot = SpotFlatTerrainPolicy(
			prim_path="/World/spot",
			name="Spot",
			position=np.array([0, 0, 0.8])
		)

		self.spot_robot = self.spot.robot

		self.debug_camera = None
		self.front_camera = None
		self._attach_camera()

	def post_setup(self):
		self.world.add_physics_callback(
			"physics_step_spot",
			callback_fn=self.on_physics_step
		)

	def set_base_command(self, command):
		self._base_command = command

	def on_physics_step(self, step_size):
		if self.initialized:
			self.spot.forward(step_size, self._base_command)
		else:
			self.initialized = True
			self.spot.initialize()
			self.spot.post_reset()
			self.spot.robot.set_joints_default_state(self.spot.default_pos)
	
			self.debug_camera.initialize()

	def _attach_camera(self):
		if not self.spot_robot or self.debug_camera:
			return
		
		self.debug_camera = Camera(
			prim_path="/World/spot/body/debug_camera",
			position=np.array([-5, 0, 2.5 + 0.8]),
			resolution=(1280, 720)
		)

		self.debug_camera.prim.GetAttribute('xformOp:orient').Set(
			Gf.Quatd(
				0.6123724356957947, 0.3535533905932736,
				-0.3535533905932738, -0.6123724356957944
			)
		)

		self.front_camera = Camera(
			prim_path="/World/spot/body/front_camera",
			position=np.array([-0.48, 0, 0.8]),
			resolution=(1280, 720)
		)
		
		self.front_camera.prim.GetAttribute('xformOp:orient').Set(
			Gf.Quatd(
				0.48633, 0.51481,
				-0.51326, -0.48479
			)
		)

	def release_setup(self):
		self.initialized = False
		self.world.remove_physics_callback("physics_step")


class OgnExampleSpot:
	"""Exponential Distribution Latency Sampler node"""

	@staticmethod
	def initialize(graph_context: og.GraphContext, node: og.Node):
		SpotFlatTerrainPolicy(
			prim_path="/World/spot",
			name="Spot",
			position=np.array([0, 0, 0.8])
		)

	def release(node: og.Node):
		pass

	@staticmethod
	def internal_state() -> OgnExampleSpotInternalState:
		"""Returns an object that contains per-node state information"""
		return OgnExampleSpotInternalState()

	@staticmethod
	def compute(db) -> bool:
		"""Compute the output based on inputs and internal state"""
		# Check execution state
		exec_in = db.inputs.execIn
		if exec_in == og.ExecutionAttributeState.DISABLED:
			return False
			
		# Get internal state
		state_internal = db.per_instance_state

		try:
			if not state_internal.initialized:
				state_internal.post_setup()
				return False

			# === Setup command ===
			command = db.inputs.command

			state_internal.set_base_command(command)

			# === Update current state ===
			spot_robot = state_internal.spot_robot
			pose = spot_robot.get_world_pose()

			db.state.currentCommand = command
			db.state.currentPosition = pose[0]
			db.state.currentOrientation = pose[1]
			db.state.currentAngularVelocity = spot_robot.get_angular_velocity()
			db.state.currentLinearVelocity = spot_robot.get_linear_velocity()

			return True
			
		except Exception as e:
			# Log error and disable output
			print(f"[Example Spot]: {e}")
			db.outputs.execOut = og.ExecutionAttributeState.DISABLED
			return False
