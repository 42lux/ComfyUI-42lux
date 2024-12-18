import { app } from "../../../scripts/app.js";
import { api } from "../../../scripts/api.js";

/**
 * Registers the TokenCounter extension with the app.
 */
app.registerExtension({
    name: "42lux.TokenCounter",

    /**
     * Sets up the event listener for token counter updates.
     */
    async setup() {
        api.addEventListener("42lux.token_counter.update", handleTokenCounterUpdate);
    },

    /**
     * Modifies the node definition before registration.
     * @param {Object} nodeType - The type of the node.
     * @param {Object} nodeData - The data associated with the node.
     * @param {Object} app - The application instance.
     */
    async beforeRegisterNodeDef(nodeType, nodeData, app) {
        if (nodeData.name === "PromptWithTokenCounter") {
            const originalOnNodeCreated = nodeType.prototype.onNodeCreated;
            nodeType.prototype.onNodeCreated = function() {
                if (originalOnNodeCreated) {
                    originalOnNodeCreated.apply(this, arguments);
                }
                this.addWidget("text", "token_count", "0", null, { multiline: false });
            };
        }
    }
});

/**
 * Handles the token counter update event.
 * @param {Event} event - The event object containing details of the update.
 */
function handleTokenCounterUpdate(event) {
    const { node: nodeId, widget: widgetName, text } = event.detail;

    const node = app.graph.getNodeById(nodeId);
    if (!node) {
        console.error(`Node to update (#${nodeId}) not found.`);
        return;
    }

    const widget = node.widgets.find(w => w.name === widgetName);
    if (!widget) {
        console.error(`Widget to update (#${nodeId}:${widgetName}) not found.`);
        return;
    }

    widget.value = text;
    app.graph.setDirtyCanvas(true);
}
