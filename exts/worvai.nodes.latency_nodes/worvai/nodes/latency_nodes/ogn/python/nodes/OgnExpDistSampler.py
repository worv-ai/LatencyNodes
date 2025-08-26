"""
OmniGraph core Python API:
	https://docs.omniverse.nvidia.com/kit/docs/omni.graph/latest/Overview.html

OmniGraph attribute data types:
	https://docs.omniverse.nvidia.com/kit/docs/omni.graph.docs/latest/dev/ogn/attribute_types.html

Collection of OmniGraph code examples in Python:
	https://docs.omniverse.nvidia.com/kit/docs/omni.graph.docs/latest/dev/ogn/ogn_code_samples_python.html

Collection of OmniGraph tutorials:
	https://docs.omniverse.nvidia.com/kit/docs/omni.graph.tutorials/latest/Overview.html
"""
import random

import omni.graph.core as og

from .base.base_sampler import BaseLatencySampler, LatencySamplerInternalState


class OgnExpDistInternalState(LatencySamplerInternalState):
	"""Internal state for Exponential Distribution sampler"""

	def __init__(self):
		"""Instantiate the per-node state information"""
		super().__init__()


class OgnExpDistSampler(BaseLatencySampler):
	"""Exponential Distribution Latency Sampler node"""

	@staticmethod
	def internal_state() -> OgnExpDistInternalState:
		"""Returns an object that contains per-node state information"""
		return OgnExpDistInternalState()

	@staticmethod
	def sample_distribution(**kwargs) -> float:
		"""
		Sample a value from exponential distribution.
		
		The exponential distribution is useful for modeling waiting times
		and is commonly used in network latency scenarios where most
		delays are small but occasionally large delays occur.
		
		Args:
			rate (float): Rate parameter (λ > 0), also called lambda
			
		Returns:
			float: Sampled latency value from exponential distribution
		"""
		rate = kwargs.get('rate', 1.0)
		
		# Validate parameters
		OgnExpDistSampler.validate_positive(rate, "rate")
		
		# Sample from exponential distribution
		return random.expovariate(rate)

	@staticmethod
	def compute(db) -> bool:
		"""Compute the output based on inputs and internal state"""
		# Check execution state
		exec_in = db.inputs.execIn
		if exec_in == og.ExecutionAttributeState.DISABLED:
			return False
			
		# Get internal state
		state = db.per_instance_state
		
		try:
			# Extract Exponential distribution parameters
			rate = db.inputs.rate
			
			# Sample from exponential distribution
			latency_value = OgnExpDistSampler.sample_distribution(rate=rate)
			
			# Ensure non-negative latency (should always be for exponential)
			latency_value = max(0.0, latency_value)
			
			# Update internal statistics
			state.update_statistics(latency_value)
			
			# Update state outputs if available
			BaseLatencySampler._update_state_outputs(db, state, latency_value)
			
			# Write outputs
			db.outputs.latencyOut = latency_value
			db.outputs.execOut = og.ExecutionAttributeState.ENABLED
			
			return True
			
		except Exception as e:
			# Log error and disable output
			print(f"Error in exponential distribution sampler: {e}")
			db.outputs.execOut = og.ExecutionAttributeState.DISABLED
			return False
