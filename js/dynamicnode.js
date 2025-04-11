import { app } from "../../../scripts/app.js";

const _ID = [
  "RangeIterator"
];

app.registerExtension({
  name: "Slix.EnhancedComfyUI",
  async beforeRegisterNodeDef(nodeType, nodeData, app) {
    if (!_ID.includes(nodeData.name)) {
      return;
    }

    const onWidgetChanged = nodeType.prototype.onWidgetChanged;
    nodeType.prototype.onWidgetChanged = function(name, value) {
      if(onWidgetChanged) {
        onWidgetChanged.apply(this, arguments);
      }
      
      if (name === "custom_values") {
        const hasCustomValues = value && value.trim().length > 0;
        
        // Handle the input slot for "end"
        const endInput = this.inputs ? this.inputs.find(input => input.name === "end") : null;
        
        if(hasCustomValues && endInput) {
          // Remove by index if you can find it
          const endIndex = this.inputs.indexOf(endInput);
          if (endIndex !== -1) {
        this.removeInput(endIndex);
          }
        } else if (!hasCustomValues && !this.inputs.find(input => input.name === "end")) {
          // Restore the input if needed
          this.addInput("end", "INT");
        }
        
        // Handle the widget for "end"
        const endWidget = this.widgets ? this.widgets.find(widget => widget.name === "end") : null;
        if(endWidget) {
          endWidget.hidden = hasCustomValues;
          this.setDirtyCanvas(true);
        }
      }
    };
    
    return nodeType;
  },
});
