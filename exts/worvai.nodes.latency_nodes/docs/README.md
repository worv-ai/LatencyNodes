# Latency Nodes Extension for Isaac Sim

## Overview

The **Latency Nodes** extension provides realistic latency simulation for robotic systems in Isaac Sim. This extension includes both **core latency nodes** for general data delays and **specialized camera nodes** for visual sensor latency simulation.

## Enabling the Extension

To enable this extension:
1. Go to **Window > Extensions** menu
2. Search for "**worvai.nodes.latency_nodes**"
3. Enable the extension

## Core Components

### Latency Controller
The **enhanced Latency Controller** applies time-based delays to data with precise timestamp control. It now includes **ForEach loop integration** for efficient processing of multiple delayed elements.

**Key Features:**
- Time-based delay queue with chronological ordering
- Automatic type resolution for any input data type
- ForEach integration for batch processing
- Precise timestamp control for realistic simulation

### Latency Samplers
Generate variable latency values using statistical distributions:
- **Normal Distribution Sampler**: Gaussian distribution for typical scenarios
- **GEV Distribution Sampler**: Generalized Extreme Value for extreme events
- **Exponential Distribution Sampler**: Network-style delays

### Camera Nodes
Specialized nodes for camera and visual sensor latency simulation:
- **Camera Data Capture**: Captures actual rendered image data
- **ROS1 Camera Helper with Latency**: Built-in camera latency for ROS publishing
- **ROS1 Publish Rendered Image**: Publishes delayed images to ROS topics
- **Render Product Latency Controller**: Specialized render product delays

## Quick Start

### Basic Latency Setup
1. Add a **Latency Controller** node to your Action Graph
2. Connect your data source to the `dataIn` input
3. Add a **Normal Distribution Sampler** for variable latency
4. Connect the sampler output to the `latency` input
5. Use the `element` output for individual delayed data

### Camera Latency Setup
1. Create a camera with render product in your scene
2. Add **Camera Data Capture** node
3. Connect **Latency Controller** for delay processing
4. Add **ROS1 Publish Rendered Image** for ROS publishing
5. Configure topic names and latency parameters

## Important Notes

- The Latency Controller outputs individual elements through ForEach integration
- Camera nodes work with actual rendered image data, not just paths
- All nodes support precise timestamp control for realistic simulation
- Examples are available in the extension's examples directory

## Version Information

**Current Version:** 0.3.0
**Isaac Sim Compatibility:** 4.5.0+ (2025.02 or later)
**Key Updates:** Enhanced Latency Controller, Camera nodes, ROS integration
