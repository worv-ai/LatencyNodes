import random
import math

import scipy.stats as stats
import carb
import omni.graph.core as og

from .base.base_sampler import (
	BaseLatencySampler,
	LatencySamplerInternalState
)


class OgnGEVDistInternalState(LatencySamplerInternalState):
	"""Internal state for Generalized Extreme Value Distribution sampler"""

	def __init__(self):
		"""Instantiate the per-node state information"""
		super().__init__()


class OgnGEVDistSampler(BaseLatencySampler):
	"""Generalized Extreme Value (GEV) Distribution Latency Sampler node"""

	# Why this code is dirty:
	# 1. Using "try ... except" is for handling errors.
	# 	-> If not, the errors will not be shown on the console.
	# 2. Using the sampling attribute names like "_locationParameter"
	# 	-> The node aligned the attributes order using attributes names.

	@staticmethod
	def initialize(graph_context: og.GraphContext, node: og.Node):
		"""Initialize any static resources or configurations"""
		try:
			# Base attributes
			min_attr = node.get_attribute("inputs:min")
			max_attr = node.get_attribute("inputs:max")
			verbose_attr = node.get_attribute("inputs:verbose")

			# GEV distribution attributes
			location_attr = node.get_attribute("inputs:_locationParameter")
			scale_attr = node.get_attribute("inputs:_scaleParameter")
			shape_attr = node.get_attribute("inputs:_shapeParameter")

			# === Set default values ===
			min_attr.set(0.0)
			max_attr.set(float('inf'))

			# === Register callbacks for value changes ===
			min_attr.register_value_changed_callback(
				OgnGEVDistSampler.on_value_changed_callback
			)
			max_attr.register_value_changed_callback(
				OgnGEVDistSampler.on_value_changed_callback
			)
			
			# Among "location", "scale", and "shape" parameters,
			# use callbacks to ensure non-negative values
			# for "location" and "scale" parameters.
			# "shape" can be any real number.
			location_attr.register_value_changed_callback(
				OgnGEVDistSampler.on_value_changed_callback
			)
			scale_attr.register_value_changed_callback(
				OgnGEVDistSampler.on_value_changed_callback
			)

			# This is for verbose mode.
			# The callback function is defined in the BaseLatencySampler.
			verbose_attr.register_value_changed_callback(
				OgnGEVDistSampler.on_value_changed_callback_verbose
			)

		except Exception as e:
			prim_path = node.get_prim_path()
			node_name = prim_path.split('/')[-1]
			print(f"[{node_name}] Error in initialize: {e}")

	@staticmethod
	def on_value_changed_callback(attr: og.Attribute) -> None:
		"""Callback for when input values change"""
		try:
			node = attr.get_node()
			is_verbose = node.get_attribute("inputs:verbose").get()

			value = attr.get()

			# Early stop if value is already valid
			if value >= 0:
				return

			# Clamp negative values to zero.
			# This method is for clamping + logging.
			clamped_value = OgnGEVDistSampler.clamp_non_negative(
				value=value,
				name=attr.get_name(),
				verbose=is_verbose
			)

			# Simply using 'set' method is okay,
			#  even if it triggers value change callback twice
			# De-registering and re-registering the callback
			#  could be more complex and error-prone
			# >>> attr.register_value_changed_callback(None)
			# >>> attr.set(clamped_value)
			# >>> attr.register_value_changed_callback(
			# ...	OgnGEVDistSampler.on_value_changed_callback
			# ... )
			attr.set(clamped_value)
		except Exception as e:
			prim_path = attr.get_node().get_prim_path()
			node_name = prim_path.split('/')[-1]
			print(f"[{node_name}] Error in on_value_changed_callback: {e}")

	@staticmethod
	def internal_state() -> OgnGEVDistInternalState:
		"""Returns an object that contains per-node state information"""
		return OgnGEVDistInternalState()

	@staticmethod
	def sample_distribution(**kwargs) -> float:
		"""
		Sample a value from Generalized Extreme Value distribution.
		
		The GEV distribution is useful for modeling extreme events and 
		has applications in network latency modeling where occasional
		large delays occur.
		
		Args:
			location (float): Location parameter (μ)
			scale (float): Scale parameter (σ > 0)
			shape (float): Shape parameter (ξ)
			
		Returns:
			float: Sampled latency value from GEV distribution
		"""
		# === Get sampling parameters ===
		required = ("location", "scale", "shape")
		missing = [k for k in required if k not in kwargs]
		if missing:
			raise ValueError(f"Missing parameter(s): {', '.join(missing)}")

		location = kwargs['location']
		scale = kwargs['scale']
		shape = kwargs['shape']

		# === Get basic parameters ===
		min = kwargs.get('min', 0.0)
		max = kwargs.get('max', float('inf'))

		is_verbose = kwargs.get('verbose', False)

		# === Sample from GEV distribution ===
		# Used scipy.stats.genextreme to sample from GEV distribution
		sample = stats.genextreme.rvs(
			c=shape,
			loc=location,
			scale=scale
		)

		clamped_sample = OgnGEVDistSampler.clamp_min_max(
			value=sample,
			min_val=min,
			max_val=max,
			name="GEV distribution sampled latency value",
			verbose=is_verbose
		)

		return clamped_sample

	@staticmethod
	def compute(db) -> bool:
		"""Compute the output based on inputs and internal state"""
		# === Check execution state ===
		exec_in = db.inputs.execIn
		if exec_in == og.ExecutionAttributeState.DISABLED:
			return False

		# === Get internal state for 'this' node ===
		# The internal state is used for per-node.
		state = db.per_instance_state
		
		try:
			# === Extract GEV distribution parameters ===
			location = db.inputs._locationParameter
			scale = db.inputs._scaleParameter
			shape = db.inputs._shapeParameter
			min = db.inputs.min
			max = db.inputs.max
			verbose = db.inputs.verbose

			# === Sample from GEV distribution ===
			latency_value = OgnGEVDistSampler.sample_distribution(
				location=location,
				scale=scale,
				shape=shape,
				min=min,
				max=max,
				verbose=verbose,
			)

			# === Update internal statistics ===
			state.update_statistics(latency_value)
			BaseLatencySampler._update_state_outputs(db, state, latency_value)
			
			# === Write outputs ===
			db.outputs.latencyOut = latency_value
			db.outputs.execOut = og.ExecutionAttributeState.ENABLED
			
			return True
			
		except Exception as e:
			# Log error and disable output
			prim_path = db.abi_node.get_prim_path()
			node_name = prim_path.split('/')[-1]
			print(f"[{node_name}] Error in compute: {e}")
			db.outputs.execOut = og.ExecutionAttributeState.DISABLED
			return False
