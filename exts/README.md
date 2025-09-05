# LatencyNodes Extension

This document provides detailed technical information on the **LatencyNodes** extension for Isaac Sim, including comprehensive documentation of all nodes, **camera integration**, **installation instructions**, **usage examples**, and **API references**.

---

## Table of Contents

- [Overview](#overview)
- [Core Latency Nodes](#core-latency-nodes)
  - [Latency Controller](#latency-controller)
  - [Normal Distribution Sampler](#normal-distribution-sampler)
  - [GEV Distribution Sampler](#gev-distribution-sampler)
  - [Exponential Distribution Sampler](#exponential-distribution-sampler)
- [Camera & Visual Sensor Nodes](#camera--visual-sensor-nodes)
  - [Camera Data Capture](#camera-data-capture)
  - [ROS1 Camera Helper with Latency](#ros1-camera-helper-with-latency)
  - [ROS1 Publish Rendered Image](#ros1-publish-rendered-image)
  - [Render Product Latency Controller](#render-product-latency-controller)
- [Integration Examples](#integration-examples)
- [Use Cases](#use-cases)
- [Contributing](#contributing)
- [License](#license)

---

## Overview

The **LatencyNodes** extension provides a comprehensive set of custom **OmniGraph** nodes for **Isaac Sim**, enabling simulation of realistic communication, sensor, and camera delays.

With these nodes, developers can:
- Model **communication latency** in robotic systems
- Simulate **sensor timing variations** and delays
- Apply **camera latency** with actual image data processing
- Explore **network-induced delays** in ROS environments
- Perform **stochastic latency analysis** using various distributions
- **Publish camera data** with realistic latency to ROS topics

This is especially useful for testing **robotics pipelines** where real-time communication, camera processing, and network delays are critical for system validation.

---

## Core Latency Nodes

### Latency Controller

Implements an **enhanced time-based delay queue** that buffers input data and releases it after a specified latency. The controller now includes **ForEach loop integration** for efficient batch processing of delayed elements.

**Inputs**
- `execIn`: Execution trigger
- `dataIn`: Input data to be delayed (supports any data type)
- `timestampIn`: Current timestamp for timing calculations
- `latency`: Delay time in seconds

**Outputs**
- `element`: Individual delayed data element (ForEach output)
- `elementIndex`: Index of current element being processed
- `elementTimestamp`: Timestamp when element should be released
- `loopBody`: ForEach loop body execution trigger
- `finished`: Triggered when all elements are processed

**Key Features**
- **Type Resolution**: Automatically resolves input data types for outputs
- **Queue Management**: Maintains chronological order of delayed data
- **Batch Processing**: Processes multiple delayed elements efficiently
- **Timestamp Accuracy**: Precise timing control for realistic latency simulation

**Use Cases**
- Sensor delay simulation with actual data
- Communication latency modeling for robotic systems
- Network delay simulation with timing precision
- Camera data latency for visual sensors

---

### Normal Distribution Sampler

Generates latency values using a **normal (Gaussian) distribution**, ideal for realistic stochastic delays.

**Inputs**
- `execIn`: Execution trigger  
- `average`: Mean latency value  
- `standardDeviation`: Standard deviation of latency  

**Outputs**
- `execOut`: Execution output  
- `latencyOut`: Generated latency value  

**State**
- `latencyHistory`: Historical latency values  
- `latencyCount`: Number of samples generated  
- `min`: Minimum latency observed  
- `max`: Maximum latency observed  

**Use Cases**
- Variable network delays  
- Realistic sensor timing variations  
- Stochastic system modeling  

---

### GEV Distribution Sampler

Generates latency values using a **Generalized Extreme Value distribution**, suitable for modeling rare and extreme latency events.

**Inputs**
- `execIn`: Execution trigger  
- `location`: Location parameter (μ)  
- `scale`: Scale parameter (σ > 0)  
- `shape`: Shape parameter (ξ)  

**Outputs**
- `execOut`: Execution output  
- `latencyOut`: Generated latency value  

**State**
- `latencyHistory`: Historical latency values  
- `latencyCount`: Number of samples generated  
- `min`: Minimum latency observed  
- `max`: Maximum latency observed  

---

### Exponential Distribution Sampler

Generates latency values using an **exponential distribution**, commonly used for **waiting times** and **network transmission delays**.

**Inputs**
- `execIn`: Execution trigger  
- `rate`: Rate parameter (λ > 0)  

**Outputs**
- `execOut`: Execution output  
- `latencyOut`: Generated latency value  

**State**
- `latencyHistory`: Historical latency values  
- `latencyCount`: Number of samples generated  
- `min`: Minimum latency observed  
- `max`: Maximum latency observed  

---

---

## Camera & Visual Sensor Nodes

### Camera Data Capture

Captures **actual rendered image data** from Isaac Sim render products for latency processing.

**Inputs**
- `execIn`: Execution trigger
- `renderProductPath`: Path to the render product to capture from
- `dataType`: Type of data to capture ("rgb", "depth", etc.)
- `timestampIn`: Current timestamp

**Outputs**
- `imageData`: Captured image data as flattened array
- `width`: Image width in pixels
- `height`: Image height in pixels
- `channels`: Number of color channels
- `encoding`: ROS-compatible encoding format
- `dataType`: Original data type information
- `timestampOut`: Output timestamp
- `execOut`: Execution output

**Key Features**
- **Multiple Data Types**: Support for RGB, depth, and other sensor data
- **Automatic Encoding**: ROS-compatible encoding detection
- **Dynamic Initialization**: Automatic annotator setup based on data type
- **Error Handling**: Robust error handling for missing or invalid data

---

### ROS1 Camera Helper with Latency

A **modified version of ROS1CameraHelper** that includes built-in latency control for camera data publishing.

**Inputs**
- `execIn`: Execution trigger
- `renderProductPath`: Path to camera render product
- `topicName`: ROS topic name for publishing
- `frameId`: Camera frame identifier
- `nodeNamespace`: ROS node namespace
- `queueSize`: ROS publisher queue size
- `latency`: Latency to apply in seconds
- `sensorType`: Type of sensor data

**Outputs**
- `execOut`: Execution output

**Key Features**
- **Built-in Latency**: Integrated latency queue for camera data
- **ROS Integration**: Direct ROS publishing with latency simulation
- **Multiple Sensor Types**: Support for various camera sensor types
- **Metadata Preservation**: Maintains sensor metadata through latency processing

---

### ROS1 Publish Rendered Image

Publishes **image data with applied latency** to ROS topics, designed to work with the Latency Controller output.

**Inputs**
- `execIn`: Execution trigger
- `imageData`: Image data array (from Latency Controller element output)
- `width`: Image width
- `height`: Image height
- `channels`: Number of channels
- `encoding`: Image encoding format
- `frameId`: Camera frame identifier
- `topicName`: ROS topic name
- `nodeNamespace`: ROS node namespace
- `queueSize`: Publisher queue size
- `timestampIn`: Image timestamp
- `useSystemTime`: Whether to use system time for ROS header

**Outputs**
- `execOut`: Execution output

**Key Features**
- **Latency Integration**: Designed to work with Latency Controller element outputs
- **ROS Compatibility**: Full ROS Image message support
- **Flexible Encoding**: Support for various image encodings (rgb8, 32FC1, etc.)
- **Timestamp Control**: Option for system time or simulation time

---

### Render Product Latency Controller

**Specialized latency controller** for render products that captures and delays actual rendered data.

**Inputs**
- `execIn`: Execution trigger
- `renderProductPath`: Path to render product
- `dataType`: Type of data to capture and delay
- `timestampIn`: Current timestamp
- `latency`: Latency to apply in seconds

**Outputs**
- `imageData`: Delayed image data
- `width`: Image width
- `height`: Image height
- `channels`: Number of channels
- `encoding`: Image encoding
- `timestampOut`: Delayed timestamp
- `execOut`: Execution output

**Key Features**
- **Integrated Capture**: Built-in data capture from render products
- **Latency Queue**: Time-based delay queue for rendered data
- **Data Preservation**: Maintains image quality through latency processing
- **Automatic Cleanup**: Proper resource management for annotators

---

## Integration Examples

### Basic Camera Latency Pipeline

```
OnPlaybackTick → CameraDataCapture → LatencyController → ROS1PublishRenderedImage
                      ↓                    ↑
                 NormalDistSampler ────────┘
```

**Workflow:**
1. **CameraDataCapture** captures actual rendered image data
2. **NormalDistSampler** generates variable latency values
3. **LatencyController** applies latency to the image data
4. **ROS1PublishRenderedImage** publishes delayed images to ROS topics

### Advanced Camera Setup with Multiple Data Types

```
Camera → RenderProduct → CameraDataCapture (RGB) → LatencyController → ROS1Publish (/rgb_latency)
                      → CameraDataCapture (Depth) → LatencyController → ROS1Publish (/depth_latency)
```

### Direct Camera Helper with Built-in Latency

```
OnPlaybackTick → ROS1CameraHelperWithLatency → ROS Topic
                           ↑
                    Latency Parameters
```

---

## Use Cases

### Robotics Applications
- **Autonomous Navigation**: Simulate camera processing delays in SLAM systems
- **Object Detection**: Model inference latency in computer vision pipelines
- **Multi-Robot Systems**: Test communication delays between robots
- **Sensor Fusion**: Simulate timing misalignment between different sensors

### Research & Development
- **Algorithm Testing**: Validate robotic algorithms under realistic latency conditions
- **Performance Analysis**: Study system behavior with variable communication delays
- **Network Simulation**: Model real-world network conditions in robotic systems
- **Latency Tolerance**: Test system robustness to timing variations

### Camera & Vision Systems
- **Image Processing Pipelines**: Simulate camera capture and processing delays
- **Stereo Vision**: Model synchronization issues between camera pairs
- **Visual Servoing**: Test control systems with camera feedback delays
- **ROS Integration**: Validate ROS-based vision systems with realistic latency

---

## Contributing

We welcome community contributions! 🎉  

- Fork the repo  
- Create a feature branch  
- Submit a Pull Request  

See our [Contribution Guidelines](../docs/contributions/README.md) for details.

---

## License

This project is licensed under the **Apache-2.0 License**.  
See the [LICENSE](../LICENSE) file for details.
