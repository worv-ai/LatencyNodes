from abc import ABC, abstractmethod
from typing import Any, Dict, Optional

import carb
import omni.graph.core as og


class LatencySamplerInternalState:
    """Base internal state class for latency samplers"""
    
    def __init__(self):
        """Initialize per-node state information"""
        self.sample_count = 0

        self.min_latency = float('inf')
        self.max_latency = float('-inf')

        self.history = []
        self.history_size = 1000

    def update_statistics(
        self,
        latency_value: float,
    ):
        """Update internal statistics with new latency value"""
        self.sample_count += 1
        self.min_latency = min(self.min_latency, latency_value)
        self.max_latency = max(self.max_latency, latency_value)
        
        # Maintain rolling history
        self.history.append(latency_value)
        if len(self.history) > self.history_size:
            self.history.pop(0)
            
    def reset_statistics(self):
        """Reset all statistics to initial state"""
        self.sample_count = 0
        self.min_latency = float('inf')
        self.max_latency = float('-inf')
        self.history.clear()


class BaseLatencySampler(ABC):
    """Abstract base class for latency distribution samplers"""
    
    VERBOSE = True

    @staticmethod
    @abstractmethod
    def internal_state() -> 'LatencySamplerInternalState':
        """Returns an object that contains per-node state information"""
        pass

    @staticmethod
    @abstractmethod
    def compute(db) -> bool:
        """
        Compute the output based on inputs and internal state.
        
        Args:
            db: Database containing node inputs and outputs
            
        Returns:
            bool: True if computation was successful, False otherwise
        """
        pass
    
    @staticmethod
    def on_value_changed_callback_verbose(attr: og.Attribute):
        """Callback for when verbose mode changes"""
        try:
            prim_path = attr.get_node().get_prim_path()
            node_name = prim_path.split('/')[-1]

            value = attr.get()

            BaseLatencySampler.VERBOSE = value

            if BaseLatencySampler.VERBOSE:
                carb.log_info(f"[{node_name}] Verbose mode enabled")
            else:
                carb.log_info(f"[{node_name}] Verbose mode disabled")
        except Exception as e:
            print(f"[{node_name}] Error in on_value_changed_callback_verbose: {e}")

    @staticmethod
    def _update_state_outputs(
        db,
        state: LatencySamplerInternalState,
        latency_value: float
    ):
        """Update state outputs if they exist in the node definition"""
        try:
            if hasattr(db.state, 'latencyHistory'):
                # Convert history to appropriate format for output
                db.state.latencyHistory = state.history[-100:]  # Last 100 samples
                
            if hasattr(db.state, 'latencyCount'):
                db.state.latencyCount = state.sample_count
                
        except AttributeError:
            # Some state attributes might not exist in all node definitions
            pass

    ### === Utility Methods for Clamping=== ###
    @staticmethod
    def clamp_non_negative(
        value: float,
        name: Optional[str] = None,
        verbose: bool = False
    ) -> float:
        """Clamp a value to be non-negative"""
        if value < 0:
            if verbose:
                log_name = name if name else "A value"
                carb.log_warn(
                    f"{log_name} was negative ({value}),"
                    "clamping to 0.0."
                )
            return 0.0
        return value

    @staticmethod
    def clamp_min(
        value: float,
        min_value: float,
        name: Optional[str] = None,
        verbose: bool = False
    ) -> float:
        """Clamp a value to be at least min_value"""
        if value < min_value:
            if verbose:
                log_name = name if name else "A value"
                carb.log_warn(
                    f"{log_name} ({value}) was less than"
                    f"min ({min_value}), clamping."
                )
            return min_value
        return value
    
    @staticmethod
    def clamp_max(
        value: float,
        max_value: float,
        name: Optional[str] = None,
        verbose: bool = False
    ) -> float:
        """Clamp a value to be at most max_value"""
        if value > max_value:
            if verbose:
                log_name = name if name else "A value"
                carb.log_warn(
                    f"{log_name} ({value}) was greater than"
                    f"max ({max_value}), clamping."
                )
            return max_value
        return value
    
    @staticmethod
    def clamp_min_max(
        value: float,
        min_val: float,
        max_val: float,
        name: Optional[str] = None,
        verbose: bool = False
    ) -> float:
        """Clamp a value to be within [min_val, max_val]"""
        clamped_val = value
        if clamped_val < min_val:
            clamped_val = min_val
        if clamped_val > max_val:
            clamped_val = max_val
        
        if verbose and clamped_val != value:
            log_name = name if name else "Sampled value"
            carb.log_warn(
                f"{log_name} ({value}) was outside range"
                f"[{min_val}, {max_val}], clamped to {clamped_val}."
            )
        return clamped_val
