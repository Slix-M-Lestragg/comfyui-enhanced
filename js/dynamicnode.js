import { app } from "../../../scripts/app.js";

/**
 * List of node identifiers that this extension will modify.
 * Currently only handles the Range Iterator node.
 */
const _ID = [
  "Range Iterator"
];

/**
 * ComfyUI Extension for enhancing node behavior.
 * 
 * This extension modifies specific nodes to provide additional functionality
 * beyond what's possible in the Python backend alone. For the Range Iterator
 * node, it handles the relationship between custom values and the start/end
 * numeric inputs, disabling numeric inputs when custom values are present.
 */
app.registerExtension({
  name: "Slix.EnhancedComfyUI",
  async beforeRegisterNodeDef(nodeType, nodeData, app) {
    // Skip nodes that aren't in our target list
    if (!_ID.includes(nodeData.name)) {
      return;
    }

    // Track first initialization state to handle setup logic
    let initialized = false;

    /**
     * Override the onNodeCreated method to add custom initialization logic.
     * This runs when a node is first added to the workspace.
     * 
     * @param {*} arguments - Original arguments passed to the method
     */
    const onNodeCreated = nodeType.prototype.onNodeCreated;
    nodeType.prototype.onNodeCreated = function() {
      if(onNodeCreated) {
        onNodeCreated.apply(this, arguments);
      }
      
      initialized = true;
    };

    /**
     * Override the onWidgetChanged method to handle custom widget interactions.
     * This manages the relationship between custom_values and the numeric inputs.
     * 
     * @param {string} name - Name of the widget that changed
     * @param {*} value - New value of the widget
     */
    const onWidgetChanged = nodeType.prototype.onWidgetChanged;
    nodeType.prototype.onWidgetChanged = function(name, value) {
      if(onWidgetChanged) {
        onWidgetChanged.apply(this, arguments);
      }
      console.log(`Widget changed: ${name}, Value: ${value}`);
      
      // Handle special case for custom_values widget
      if (name === "custom_values") {
        const hasCustomValues = value && value.trim().length > 0;
        
        if(hasCustomValues) {
          // Parse custom values into an array
          const customValues = value.split(',').filter(x => x.trim() !== '');
          // Calculate appropriate end value based on array length
          const calculatedEnd = customValues.length > 0 ? customValues.length - 1 : 0;
          
          // Find and update the end widget
          const endWidget = this.widgets ? this.widgets.find(widget => widget.name === "end") : null;
          if (endWidget) {
            // Set the end value to match the custom values length and disable the widget
            endWidget.value = calculatedEnd;
            endWidget.disabled = true;
          }
          
          // Also disable start widget when using custom values
          const startWidget = this.widgets ? this.widgets.find(widget => widget.name === "start") : null;
          if (startWidget) {
            startWidget.disabled = true;
          }
          
          // Trigger UI updates
          this.computeSize();
          this.setDirtyCanvas(true, true);
        } else {
          // When custom values are cleared, re-enable the standard widgets
          const endWidget = this.widgets ? this.widgets.find(widget => widget.name === "end") : null;
          if (endWidget) {
            endWidget.disabled = false;
          }
          
          const startWidget = this.widgets ? this.widgets.find(widget => widget.name === "start") : null;
          if (startWidget) {
            startWidget.disabled = false;
          }
          
          // Trigger UI updates
          this.computeSize();
          this.setDirtyCanvas(true, true);
        }
      }
    };
    
    return nodeType;
  },
});
