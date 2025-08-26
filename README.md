# Latency-Nodes

<div align="center">

<!-- Main Project Badges -->
[![GitHub release (latest SemVer)](https://img.shields.io/github/v/release/worv-ai/LatencyNodes?style=for-the-badge&logo=github&color=brightgreen)](https://github.com/worv-ai/LatencyNodes/releases)
[![GitHub license](https://img.shields.io/github/license/worv-ai/LatencyNodes?style=for-the-badge&color=blue)](https://github.com/worv-ai/LatencyNodes/blob/main/LICENSE)
[![GitHub stars](https://img.shields.io/github/stars/worv-ai/LatencyNodes?style=for-the-badge&logo=github&color=yellow)](https://github.com/worv-ai/LatencyNodes/stargazers)

<!-- Development Status -->
[![GitHub issues](https://img.shields.io/github/issues/worv-ai/LatencyNodes?style=flat&logo=github)](https://github.com/worv-ai/LatencyNodes/issues)
[![GitHub pull requests](https://img.shields.io/github/issues-pr/worv-ai/LatencyNodes?style=flat&logo=github)](https://github.com/worv-ai/LatencyNodes/pulls)
[![GitHub forks](https://img.shields.io/github/forks/worv-ai/LatencyNodes?style=flat&logo=github)](https://github.com/worv-ai/LatencyNodes/network/members)
[![GitHub last commit](https://img.shields.io/github/last-commit/worv-ai/LatencyNodes?style=flat&logo=github)](https://github.com/worv-ai/LatencyNodes/commits/main)

<!-- Technology Stack -->
[![Python](https://img.shields.io/badge/Python-3.10+-3776ab?style=flat&logo=python&logoColor=white)](https://www.python.org/)
[![Isaac Sim](https://img.shields.io/badge/Isaac%20Sim-4.5.0+-76B900?style=flat&logo=nvidia&logoColor=white)](https://developer.nvidia.com/isaac-sim)
[![OmniGraph](https://img.shields.io/badge/OmniGraph-Compatible-00D4AA?style=flat&logo=nvidia&logoColor=white)](https://docs.omniverse.nvidia.com/dev-guide/latest/programmer_ref/omni_graph.html)
[![Extension](https://img.shields.io/badge/ExtVersion-v0.1.1-orange?style=flat&logo=nvidia)](https://github.com/worv-ai/LatencyNodes)

</div>

---

<div align="center">
  <h3>
    An Isaac Sim extension providing latency simulation nodes for OmniGraph to model realistic communication delays in robotic simulations.
  </h3>
</div>

## Preview


<div align="center">

  ![Preview](./sources/preview_video_compressed.gif)

  _Users could reproduce the preview simulation using examples of the `worvai.nodes.latency_nodes`!_

  _Welcome for diverse and refined examples contributing to the community!_

</div>

## Overview

The Latency-Nodes extension provides a set of `OmniGraph nodes` for Isaac Sim that enable __realistic latency simulation__ in robotic systems. These nodes allow developers to model __communication delays__, __sensor latencies__, and __network-induced delays__ that are common in real-world robotic applications.

Users could apply latency to your robotic systems using the provided nodes with `Latency Controller` and various `Latency Samplers`. Also, they can easily add their own distribution samplers by inheriting from the base class.

![Latency Nodes Preview](/exts/worvai.nodes.latency_nodes/data/preview.png)

### Key Benefits

- Simulate realistic communication latencies in robotic systems
- Model variable delays using statistical distributions
- Easy integration with existing Isaac Sim workflows
- Performance-optimized queue-based delay implementation

## Features

- **Latency Controller**: Implements time-based delay queues for data flow
- **Multiple Distribution Samplers**: Generate variable latencies using different statistical distributions:
  - **Normal Distribution Sampler**: Gaussian distribution for typical scenarios
  - **GEV Distribution Sampler**: Generalized Extreme Value for modeling extreme latency events
  - **Exponential Distribution Sampler**: Exponential distribution for network-like delays
- **Extensible Architecture**: Abstract base class (ABC) design for easy addition of new distributions
- **Configurable Parameters**: Adjustable delay times and distribution parameters
- **Statistical Tracking**: Built-in statistics (min, max, count, history) for all samplers
- **Isaac Sim Integration**: Native OmniGraph nodes for seamless workflow integration

## Version

| Isaac Sim Version | Support Status   | Notes                          |
|-------------------|------------------|--------------------------------|
| 4.2.0             | ![Not Supported](https://img.shields.io/badge/Not%20Supported-red?style=flat) | Older release, APIs incompatible |
| 4.5.0             | ![Supported](https://img.shields.io/badge/Supported-brightgreen?style=flat)      | Fully tested and verified       |
| 5.0.0             | ![Planned](https://img.shields.io/badge/Planned-orange?style=flat)       | Compatibility under development |

## Installation

### Prerequisites
- NVIDIA Isaac Sim 4.5.0+ (2025.02 or later)
- Python 3.10+
- OmniGraph support

### Method 1: Extension Manager (Recommended)
1. Open Isaac Sim
2. Navigate to `Window > Extensions`
3. Search for "Latency Nodes"
4. Click "Install"

### Method 2: Manual Installation
1. Clone this repository:
   ```bash
   git clone https://github.com/worv-ai/LatencyNodes.git
   ```

2. Copy the extension to your Isaac Sim extensions directory:
   ```bash
   cp -r exts/worvai.nodes.latency_nodes ~/path/to/isaac-sim/extsUser
   ```

3. Enable the extension in Isaac Sim Extension Manager

## Quick Start

1. **Create a new scene** in Isaac Sim
2. **Open Action Graph** (`Window > Visual Scripting > Action Graph`)
3. **Add Latency Nodes**:
   - Right-click in the graph
   - Navigate to `Add Node > Latency Nodes`
   - Select your desired node

## Available Nodes

Users could find [Detailed Node Descriptions](/exts/README.md).

## Architecture

### Abstract Base Class Design
All distribution samplers inherit from `BaseLatencySampler`, which provides:

- **Common Interface**: Standardized methods across all samplers
- **Statistics Tracking**: Built-in min/max/count/history tracking
- **Error Handling**: Robust error handling and validation
- **Extensibility**: Easy to add new distributions

### Adding New Distributions
To add a new distribution sampler:

1. Create a new class inheriting from `BaseLatencySampler`
2. Implement the `internal_state()` method
3. Implement the `sample_distribution()` method with your distribution logic
4. Implement the `compute()` method to handle input/output specific to your distribution

Example:
```python
class OgnMyDistSampler(BaseLatencySampler):
    @staticmethod
    def sample_distribution(**kwargs) -> float:
        # Your distribution sampling logic here
        return your_random_value
```

## Contributing

We welcome contributions! Please see our contributing guidelines [Contribution Guideline](docs/contributions/README.md).

## License

This project is licensed under the Apache-2.0 License - see the [LICENSE](LICENSE) file for details.

## Changelog

See [CHANGELOG.md](exts/worvai.nodes.latency_nodes/docs/CHANGELOG.md) for version history and updates.

## Acknowledgements

We would like to express our gratitude to the following:

- **NVIDIA Corporation** for `Isaac Sim` and the `Omniverse` platform that makes this extension possible
- **Pixar Animation Studios** for the `Universal Scene Description (USD)` framework
- **OmniGraph** for providing the visual scripting framework that enables our latency simulation nodes

---

**Author:** kickthemoon0817 (kickthemoon0817@gmail.com)  
**Version:** 0.1.0  
**Isaac Sim Compatibility:** 4.5.0 (2025.02+)