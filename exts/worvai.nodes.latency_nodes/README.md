# Latency Nodes Extension

This document provides detailed information on the **Latency Nodes** extension for Isaac Sim, including **installation instructions**, **usage examples**, and **API references**.

---

## Table of Contents

- [Overview](#overview)
- [Available Nodes](#available-nodes)
  - [Latency Controller](#latency-controller)
  - [Normal Distribution Sampler](#normal-distribution-sampler)
  - [GEV Distribution Sampler](#gev-distribution-sampler)
  - [Exponential Distribution Sampler](#exponential-distribution-sampler)
  - [Updated Soon](#updated-soon)
- [Use Cases](#use-cases)
- [Contributing](#contributing)
- [License](#license)

---

## Overview

The **Latency Nodes** extension provides a set of custom [OmniGraph](https://docs.omniverse.nvidia.com/dev-guide/latest/programmer_ref/omni_graph.html) nodes for **Isaac Sim**, enabling simulation of realistic communication and sensor delays.  

With these nodes, developers can:
- Model **communication latency**
- Simulate **sensor timing variations**
- Explore **network-induced delays**
- Perform **stochastic latency analysis**  

This is especially useful for testing **robotics pipelines** where real-time communication and network delays are critical.

---

## Available Nodes

### Latency Controller

Implements a **time-based delay queue** that buffers input data and releases it after a specified latency.

**Inputs**
- `execIn`: Execution trigger
- `data`: Input data to be delayed
- `latency`: Delay time in seconds

**Outputs**
- `execOut`: Execution output
- `delayedData`: Data output after latency delay

**Use Cases**
- Sensor delay simulation  
- Communication latency modeling  
- Network delay simulation  

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

### Updated Soon

This section is reserved for **upcoming nodes and features** that will be added to the Latency Nodes extension.  

Stay tuned for announcements in the [changelog](../docs/CHANGELOG.md) and GitHub releases.

---

## Contributing

We welcome community contributions! 🎉  

- Fork the repo  
- Create a feature branch  
- Submit a Pull Request  

See our [Contribution Guidelines](../../docs/contributions/README.md) for details.

---

## License

This project is licensed under the **MIT License**.  
See the [LICENSE](../../LICENSE) file for details.
