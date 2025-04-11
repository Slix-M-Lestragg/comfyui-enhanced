class ContainsAnyDict(dict):
    """
    A special dictionary subclass that always returns True for any key membership check.
    Used in ComfyUI node definition to allow dynamic inputs to be passed to the node.
    """
    def __contains__(self, key):
        return True

class RangeIterator:
    """
    ComfyUI node that generates sequential numeric values following various iteration patterns.
    
    This node can:
    - Iterate through a range of numbers with custom step sizes
    - Cycle through values (looping back to start after reaching the end)
    - Bounce between values (reversing direction at boundaries)
    - Iterate once through values (stopping at the end)
    - Use custom value lists instead of sequential ranges
    
    The node maintains its state between workflow executions,
    allowing it to remember its position in the sequence.
    """
    
    @classmethod
    def IS_CHANGED(cls, *args, **kwargs):
        """
        Forces the node to be re-evaluated on every workflow run.
        
        Returns:
            float("NaN"): A special value that causes ComfyUI to always see this
                         node as changed, triggering re-execution.
        """
        # Force re-evaluation of the node on every run
        return float("NaN")
    
    @classmethod
    def INPUT_TYPES(cls):
        """
        Defines the input interface for the node in the ComfyUI workflow editor.
        
        Returns:
            dict: A structured definition of required, optional, and hidden inputs
                 that ComfyUI will use to build the node interface.
        """     
        return {
        "required": {
            "custom_values": ("STRING", {"default": "", "multiline": False, 
                "tooltip": "Enter comma separated number list\n"
                "(e.g., 1, 1.4, 1.9, 2, 5, 11.1)\n"
                "leave empty to use 'start' and 'end' parameters."}),  # Custom value list as string
            "mode": (["cycle", "bounce", "once"], {"default": "cycle"}),  # Iteration mode
            "start": ("INT", {"default": 0, "min": 0, "max": 100}),  # Starting value for the range
            "end": ("INT", {"default": 10, "min": 1, "max": 100}),   # Ending value for the range
            "step": ("INT", {"default": 1, "min": 1, "max": 10}),    # Step size for iterations
            "reset_counter": ("BOOLEAN", {"default": False})         # Force reset of the counter
        },
        "optional": {
            "value_list": ("LIST",),  # Directly provide a list from another node
            **ContainsAnyDict()  # Support for dynamic inputs from other nodes
        },
        "hidden": {
            "unique_id": "UNIQUE_ID",  # Node ID used to maintain state between runs
        }
        }

    # Define node outputs and metadata
    RETURN_TYPES = ("NUMBER", "NUMBER", "BOOLEAN")  # Output types for ComfyUI
    RETURN_NAMES = ("current_value", "next_value", "cycle_completed")  # Names for the outputs
    FUNCTION = "range_iterator"  # Method that will be called to process the node
    CATEGORY = "Enhanced/Lists"  # Node category in the ComfyUI interface
    OUTPUT_NODE = True  # This can be used as an output node

    def __init__(self):
        """
        Initialize the node's internal state that persists between workflow runs.
        """
        # State variables for tracking iteration position
        self.current_index = None  # Current position in the sequence (None = not initialized)
        self.direction = 1         # For bounce mode: 1 = forward, -1 = backward
        self.cycle_completed = False  # Whether a cycle has been completed
        
        # Cache previous parameter values to detect changes
        self.prev_custom_values = ""    # Previous custom values string
        self.prev_start = None          # Previous start value
        self.prev_end = None            # Previous end value
        self.prev_step = None           # Previous step value
        self.prev_mode = None           # Previous mode
        self.prev_value_list_hash = None  # Hash of previous value_list contents
    
    def range_iterator(self, start, end, step, reset_counter, custom_values, mode="cycle", value_list=None, **kwargs):
        """
        Main node processing function that performs the iteration logic.
        
        Args:
            start (int): Starting value for the range
            end (int): Ending value for the range
            step (int): Step size for iterations
            reset_counter (bool): Whether to reset the counter position
            custom_values (str): Comma-separated values as a string
            mode (str): Iteration mode ("cycle", "bounce", or "once")
            value_list (list, optional): Direct list of values to iterate through
            **kwargs: Dynamic inputs from other nodes
            
        Returns:
            tuple: (current_value, next_value, cycle_completed)
                - current_value: The current value in the sequence
                - next_value: The next value that will be used
                - cycle_completed: Whether a full cycle was completed
        """
        # Handle any dynamic inputs passed through kwargs
        dynamic_inputs = kwargs
        if dynamic_inputs:
            print(f"Received dynamic inputs: {list(dynamic_inputs.keys())}")
            # These can be accessed with dynamic_inputs['input_name']
        
        # --- DETECT PARAMETER CHANGES ---
        # Check if any parameters have changed that would require a reset
        should_reset = reset_counter
        
        # Check if custom values string has changed
        if custom_values != self.prev_custom_values:
            print(f"Custom values changed from '{self.prev_custom_values}' to '{custom_values}' - resetting counter")
            should_reset = True
            self.prev_custom_values = custom_values
        
        # Check if numeric parameters have changed
        if start != self.prev_start:
            print(f"Start value changed from {self.prev_start} to {start} - resetting counter")
            should_reset = True
            self.prev_start = start
            
        if end != self.prev_end:
            print(f"End value changed from {self.prev_end} to {end} - resetting counter")
            should_reset = True
            self.prev_end = end
            
        if step != self.prev_step:
            print(f"Step value changed from {self.prev_step} to {step} - resetting counter")
            should_reset = True
            self.prev_step = step
            
        # Check if mode has changed
        if mode != self.prev_mode:
            print(f"Mode changed from {self.prev_mode} to {mode} - resetting counter")
            should_reset = True
            self.prev_mode = mode
            
        # Check if value_list has changed (using a hash for comparison)
        if value_list is not None:
            current_hash = hash(str(value_list))
            if current_hash != self.prev_value_list_hash:
                print("Value list changed - resetting counter")
                should_reset = True
                self.prev_value_list_hash = current_hash
        
        # --- PROCESS CUSTOM VALUES ---
        # Parse comma-separated custom values if provided
        custom_list = None
        if custom_values and custom_values.strip():
            try:
                # Convert string to list of numbers (float or int)
                custom_list = [float(x.strip()) for x in custom_values.split(',')]
                # Convert to integers if the value has no decimal part
                custom_list = [int(x) if x == int(x) else x for x in custom_list]
                print(f"Parsed custom values: {custom_list}")
                # Adjust end to match list length when using custom list
                end = len(custom_list) - 1
            except ValueError as e:
                print(f"Error parsing custom values: {e}")
                custom_list = None
        
        # Use custom_list if available, otherwise use value_list from input
        if custom_list is not None:
            value_list = custom_list
            
        # Flag to indicate we're using a list rather than numeric range
        using_list = value_list is not None and len(value_list) > 0
        
        # --- INITIALIZE OR RESET STATE ---
        if self.current_index is None or should_reset:
            self.current_index = start
            self.direction = 1
            self.cycle_completed = False
            print(f"Counter reset to {start}")
        
        # When using a list, ensure index is within list bounds
        if using_list:
            list_end = len(value_list) - 1
            if self.current_index > list_end:
                self.current_index = list_end
        
        # Store current index before updating for this iteration
        current_index = self.current_index
        
        # --- GET CURRENT VALUE ---
        # Get current value (either from list or direct index)
        if using_list:
            current_value = value_list[current_index]
        else:
            current_value = current_index
        
        # --- CALCULATE NEXT INDEX & VALUE BASED ON MODE ---
        if mode == "cycle":
            # Cycle mode: loop back to start after reaching end
            next_index = current_index + (step * self.direction)
            
            if using_list:
                if next_index > list_end:
                    # Modulo operation to wrap around the list
                    next_index = next_index % len(value_list)
                    self.cycle_completed = True
                else:
                    self.cycle_completed = False
            else:
                if next_index > end:
                    # Jump back to start value
                    next_index = start
                    self.cycle_completed = True
                else:
                    self.cycle_completed = False
                
        elif mode == "bounce":
            # Bounce mode: reverse direction at boundaries
            next_index = current_index + (step * self.direction)
            
            if using_list:
                if next_index > list_end:
                    # Hit upper bound, reverse direction and calculate bounce position
                    self.direction = -1
                    next_index = list_end - (next_index - list_end)
                    self.cycle_completed = False
                elif next_index < 0:
                    # Hit lower bound, reverse direction and calculate bounce position
                    self.direction = 1
                    next_index = 0 + (0 - next_index)
                    self.cycle_completed = True  # Full cycle completed when going from bottom to top
                else:
                    self.cycle_completed = False
            else:
                if next_index > end:
                    # Hit upper bound, reverse direction and calculate bounce position
                    self.direction = -1
                    next_index = end - (next_index - end)
                    self.cycle_completed = False
                elif next_index < start:
                    # Hit lower bound, reverse direction and calculate bounce position
                    self.direction = 1
                    next_index = start + (start - next_index)
                    self.cycle_completed = True  # Full cycle completed when going from bottom to top
                else:
                    self.cycle_completed = False
                
        elif mode == "once":
            # Once mode: stop at the end boundary
            next_index = current_index + step
            
            if using_list:
                if next_index > list_end:
                    # Stop at the end of list
                    next_index = list_end
                    self.cycle_completed = True
                else:
                    self.cycle_completed = False
            else:
                if next_index > end:
                    # Stop at the end value
                    next_index = end
                    self.cycle_completed = True
                else:
                    self.cycle_completed = False
        
        # Update the state for the next execution
        self.current_index = next_index
        
        # Calculate next value based on the next index
        if using_list:
            next_value = value_list[next_index]
        else:
            next_value = next_index
        
        # Log the current state for debugging
        print(f"Range Iterator: current={current_value}, next={next_value}, mode={mode}, completed={self.cycle_completed}")
        
        # Return the three outputs
        return (current_value, next_value, self.cycle_completed)