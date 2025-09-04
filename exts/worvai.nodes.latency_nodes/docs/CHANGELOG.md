# Changelog

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.3.0] - Released, 2025-09-03

### Added

- Build **OgnCameraDataCapture** node to capture data from render product.

- Build **OgnROS1CameraHelperWithLatency** node to publish data with latency to ROS1.

- Build **OgnROS1PublishRenderedImage** node to publish image data with latency to ROS1

- Build **OgnRenderProductLatencyController** node to control latency for render product.

### Changed
- Update **Latency Controller**, incorporating the following features:
    - Incorporate the ForEach Node into the latency controller.
    - Fix the type resolve.

- Update **Preview & Example** to use the new nodes.

## [0.2.0] - Unreleased, 2025-08-22
- Provide **Preview & Example** for latency controller.

- Add **main README.md** for latency nodes extension in github main page.

## [0.1.0] - Unreleased, 2025-07-31

### Added
- Build **Core Extension Infrastructure** for latency Controller and Sampler.

- Build **Latency Controller** as Latency Controller node.

- Build **Base Sampler** for various latency samplers.

- Build **OgnNormDistSampler** and **OgnGEVDistSampler** as example latency samplers.

- Add temporal **icon** and **preview** for extension tab in Isaac Sim.

- Add temporal **icon** for nodes in Latency Nodes.

### Changed


### Fixed
