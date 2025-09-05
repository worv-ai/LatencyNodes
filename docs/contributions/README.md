# Contributing to LatencyNodes

Thank you for your interest in contributing to LatencyNodes! This guide will help you get started with contributing to our Isaac Sim extension for latency simulation.

## Ways to Contribute

We welcome contributions in various forms:

- **Bug Reports**: Found a bug? Let us know!
- **Feature Requests**: Have an idea for improvement? Share it!
- **Documentation**: Help improve our docs and examples
- **Code Contributions**: Fix bugs, add features, or optimize performance
- **Testing**: Help test new features and report issues
- **New Distribution Samplers**: Add new statistical distributions
- **Example Scenarios**: Create interesting simulation examples

## Getting Started

### Prerequisites

Before contributing, ensure you have:

- **NVIDIA Isaac Sim 2023.1+** installed
- **Python 3.10+** with development tools
- **Git** for version control
- **VS Code** (recommended) with Python extensions

### Development Setup

1. **Fork and Clone the Repository**
   ```bash
   git clone https://github.com/worv-ai/LatencyNodes.git
   cd LatencyNodes
   ```

2. **Install Extension in Development Mode**
   ```bash
   # Copy extension to Isaac Sim extensions directory
   cp -r exts/worvai.nodes.latency_nodes ~/.local/share/ov/pkg/isaac_sim-*/extsUser/
   
   # Or add path in Extension Manager for development
   ```

3. **Verify Installation**
   - Open Isaac Sim
   - Navigate to `Window > Extensions`
   - Enable "LatencyNodes" extension
   - Test basic functionality

## Contribution Process

### 1. Before You Start

- **Check existing issues** to avoid duplicate work
- **Open an issue** to discuss major changes before implementing
- **Review the codebase** to understand the architecture

### 2. Development Workflow

1. **Create a Feature Branch**
   ```bash
   git checkout -b feature/your-feature-name
   # or
   git checkout -b bugfix/issue-description
   ```

2. **Make Your Changes**
   - Follow our coding standards (see below)
   - Write clear, documented code
   - Add tests for new functionality
   - Update documentation as needed

3. **Test Your Changes**
   - __Not developed yet, but the test codes would be added soon!!!__
   ```bash
   # Run any existing tests
   python -m pytest tests/  # If test suite exists
   
   # Test in Isaac Sim environment
   # Verify nodes work correctly in OmniGraph
   ```

4. **Push and Create Pull Request**
   ```bash
   git push origin feature/your-feature-name
   ```
   Then create a PR on GitHub with a clear description.

## Coding Standards

### Python Code Style

- **Follow PEP 8** for Python code formatting
- **Use type hints** for function parameters and return values
- **Write docstrings** for all public methods and classes
- **Keep functions focused** and reasonably sized

Example:
```python
def sample_distribution(self, mean: float, std_dev: float) -> float:
    """
    Sample from normal distribution with given parameters.
    
    Args:
        mean: The mean of the distribution
        std_dev: The standard deviation (must be > 0)
        
    Returns:
        A random sample from the normal distribution
        
    Raises:
        ValueError: If std_dev <= 0
    """
    if std_dev <= 0:
        raise ValueError("Standard deviation must be positive")
    return np.random.normal(mean, std_dev)
```

### OmniGraph Node Development

- **Inherit from BaseLatencySampler** for distribution oor other kinds of latency samplers
- **Use clear input/output attribute names**
- **Implement proper error handling**
- **Add comprehensive node documentation**

Example node structure:
```python
class OgnNewDistSampler(BaseLatencySampler):
    """A new distribution sampler for specific use cases."""
    
    @staticmethod
    def internal_state():
        return og.Database("worvai.nodes.latency_nodes.OgnNewDistSampler", {
            # Define internal state attributes
        })
    
    def sample_distribution(self, **kwargs) -> float:
        # Implement your distribution logic
        pass
    
    def compute(self, db) -> bool:
        # Handle computation and I/O
        pass
```

### Documentation Standards

- **Clear and concise explanations**
- **Include usage examples**
- **Document all parameters and outputs**
- **Add images/diagrams where helpful**

## Specific Contribution Areas

### Adding New Distribution Samplers

To add a new statistical distribution:

1. **Create the sampler class** in `ogn/python/nodes/`
2. **Inherit from BaseLatencySampler**
3. **Implement required methods**: `compute()` for core logics of omni graph
4. **Add proper documentation and examples**
5. **Create an OGN definition file** (.ogn)
6. **Add to CategoryDefinition.json**

### Example Contributions

We especially welcome:

- **Real-world robotics scenarios** with latency modeling
- **Integration examples** with ROS/ROS2
- **Performance benchmarks** and optimizations
- **New distribution types** for specific use cases
- **Educational tutorials** and guides

### Testing Guidelines

- **Test in Isaac Sim environment** with actual OmniGraph workflows
- **Verify node behavior** with various input parameters
- **Check error handling** for edge cases
- **Test performance** with large datasets or long simulations

## Bug Reports

When reporting bugs, please include:

- **Isaac Sim version** and operating system
- **Extension version** you're using
- **Clear steps to reproduce** the issue
- **Expected vs actual behavior**
- **Error messages or logs** if available
- **Screenshots or videos** if helpful

Use this template:
```markdown
**Environment:**
- Isaac Sim Version: 2025.02+ (4.5.0)
- OS: Ubuntu 22.04
- Extension Version: 0.1.0

**Steps to Reproduce:**
1. Open Isaac Sim
2. Create new Action Graph
3. Add Normal Distribution Sampler
4. Set mean=100, std_dev=-1

**Expected Behavior:**
Should show validation error

**Actual Behavior:**
Extension crashes

**Additional Context:**
Error occurs only when std_dev is negative
```

## Feature Requests

For feature requests, please:

- **Describe the use case** and why it's needed
- **Explain the expected behavior** in detail
- **Consider implementation complexity**
- **Provide examples** of how it would be used

## 📞 Getting Help

Need help or have questions?

- **GitHub Issues**: For bugs and feature requests
- **GitHub Discussions**: For questions and community chat
- **Email**: kickthemoon0817@gmail.com for direct contact

## Recognition

Contributors will be:
- **Listed in [CHANGELOG](../../exts/worvai.nodes.latency_nodes/docs/CHANGELOG.md)** for their contributions
- **Mentioned in release notes** for significant features
- **Added to contributors list** in the main README

---

Thank you for helping make LatencyNodes better!