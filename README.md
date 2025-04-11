# ComfyUI Enhanced Nodes

A collection of enhanced nodes for [ComfyUI](https://github.com/comfyanonymous/ComfyUI) that provide powerful additional functionality to your workflows.

## Installation

1. Clone this repository into your ComfyUI custom_nodes folder:
   ```bash
   cd /path/to/ComfyUI/custom_nodes
   git clone https://github.com/yourusername/comfyui-enhanced.git
   ```

2. Restart ComfyUI if it's already running.

## Features

- **Range Iterator**: A versatile node for creating sequences with precise control
- **Enhanced UI Interactions**: JavaScript extensions improve the usability of nodes with interdependent controls

## Nodes

### Range Iterator

![Range Iterator Node](https://placeholder-for-screenshot.png)

The Range Iterator node provides robust iteration capabilities with several unique features:

- **Multiple Iteration Modes**:
  - `cycle`: Loop through values, returning to start after reaching the end
  - `bounce`: Reverse direction at boundaries, oscillating between start and end
  - `once`: Iterate once through values, stopping at the end
  
- **Flexible Input Methods**:
  - Numeric ranges with custom step sizes
  - Custom value lists (comma-separated)
  - Direct list inputs from other nodes
  
- **State Persistence**: Maintains its position in sequences between workflow runs
  
- **Dynamic UI**: Input fields adapt based on your selections (e.g., disables numeric inputs when using custom values)

#### Outputs

- `current_value`: The current value in the sequence
- `next_value`: The value that will be generated on the next run
- `cycle_completed`: Boolean flag indicating if a full cycle has completed

#### Use Cases

- **Animation Sequences**: Create keyframes or sequential adjustments for animations
- **Seed Exploration**: Methodically explore different seeds in image generation
- **Parameter Studies**: Systematically vary parameters to find optimal settings
- **Batch Processing**: Process groups of inputs with different parameters

## Examples

### Basic Range Iteration

To count from 0 to 10 in steps of 1, looping back to the beginning:

1. Add a Range Iterator node
2. Set `mode` to `cycle`
3. Set `start` to `0`
4. Set `end` to `10`
5. Set `step` to `1`
6. Leave `custom_values` empty

### Using Custom Values

To iterate through a specific set of values:

1. Add a Range Iterator node
2. Set `mode` to your preferred pattern
3. Enter values in the `custom_values` field (e.g., `1.5, 2.7, 3.9, 5.2`)
4. Notice how the `start` and `end` inputs are automatically disabled

### Creating Animation Keyframes

To generate keyframes for a smooth animation:

1. Add a Range Iterator node
2. Set `mode` to `bounce`
3. Set appropriate `start`, `end`, and `step` values
4. Connect the `current_value` output to parameters that influence your animation

## Requirements

- ComfyUI (latest version recommended)
- Standard web browser (for UI enhancements)

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

[MIT License](LICENSE)