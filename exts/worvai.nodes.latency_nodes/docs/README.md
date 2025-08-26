# Usage

## Enabling the Extension

To enable this extension, go to Windows > Extensions menu and enable worvai.nodes.latency_nodes extension.

## Latency Nodes

This extension using **Latency Controller** to apply latency at the data with timestamp, and using **Latency Sampler** to sample the latency data.

Users should be aware that the data out from latency controller node is array, so it is recommended to use **ForEach** node in native Isaac Sim node. Recommend to follow the example in github or the preview image below.

## Latency Samplers

In current version(0.1.0, 2025-07-31), this extension provides two latency samplers:
- **OgnNormDistSampler**: Samples latency data from normal distribution.
- **OgnGEVDistSampler**: Samples latency data from generalized extreme value distribution.
