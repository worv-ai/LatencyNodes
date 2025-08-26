import numpy as np
from pxr import Gf

from isaacsim.core.utils.stage import add_reference_to_stage
from isaacsim.sensors.camera import Camera
import isaacsim.core.utils.rotations as rot_utils
from isaacsim.robot.policy.examples.robots.spot import SpotFlatTerrainPolicy

class SpotController:
	def __init__(self):
		self.initialized = False
		self._base_command = np.array([0.0, 0.0, 0.0])

		self.spot = None        # The spot policy
		self.spot_robot = None  # The spot robot
		self.debug_camera = None

	@property
	def base_command(self):
		return self._base_command
	
	@property
	def robot(self):
		return self.spot_robot

	def setup(self):
		self.spot = SpotFlatTerrainPolicy(
			prim_path="/World/spot",
			name="Spot",
			position=np.array([0, 0, 0.8])
		)

		self.spot_robot = self.spot.robot

		self._attach_camera()

	def post_setup(self, world):
		self.initialized = False
		
		world.add_physics_callback(
			"physics_step",
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

		)
		
		self.debug_camera.prim.GetAttribute('xformOp:orient').Set(
			Gf.Quatd(0.6123724356957947, 0.3535533905932736, -0.3535533905932738, -0.6123724356957944)
		)