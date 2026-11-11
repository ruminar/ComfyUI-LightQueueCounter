import { app } from "../../../scripts/app.js";

function getWidgetValue(node, name) {
    const widget = node?.widgets?.find((w) => w.name === name);
    return widget?.value;
}

function normalizeLabel(value) {
    const label = String(value ?? "").trim();
    return label || "queue";
}

function makeStatus(label, running, pending, total) {
    return `${label}: running=${running}, pending=${pending}, total=${total}`;
}

function makeTitle(label, running, pending, total, titleFormat) {
    if (titleFormat === "short") {
        return `${label}: ${running}/${pending}/${total}`;
    }

    if (titleFormat === "full") {
        return makeStatus(label, running, pending, total);
    }

    return `${label}: ${total}`;
}

function chooseTitle(node, output) {
    const payloadList = output?.light_queue_counter_payload;

    if (payloadList && payloadList.length) {
        const payload = payloadList[0];

        const label = normalizeLabel(
            getWidgetValue(node, "label") ?? payload.label
        );

        const titleFormat = String(
            getWidgetValue(node, "title_format") ?? "total"
        );

        const running = Number(payload.running ?? 0);
        const pending = Number(payload.pending ?? 0);
        const total = Number(payload.total ?? running + pending);

        return makeTitle(label, running, pending, total, titleFormat);
    }

    const titlePayload = output?.light_queue_counter_title;
    if (titlePayload && titlePayload.length) {
        return String(titlePayload[0] ?? "").trim();
    }

    return "";
}

function updateNodeTitle(node, output) {
    if (!node || !output) {
        return;
    }

    const title = chooseTitle(node, output);
    if (!title) {
        return;
    }

    node.title = title;
    node._lightQueueCounterLastOutput = output;

    node.setDirtyCanvas?.(true, true);
    app.graph.setDirtyCanvas?.(true, true);
}

function installWidgetCallbacks(node) {
    const widgetNames = ["title_format", "label"];

    for (const name of widgetNames) {
        const widget = node?.widgets?.find((w) => w.name === name);

        if (!widget || widget._lightQueueCounterCallbackInstalled) {
            continue;
        }

        const originalCallback = widget.callback;

        widget.callback = function (...args) {
            const result = originalCallback?.apply(this, args);

            if (node._lightQueueCounterLastOutput) {
                updateNodeTitle(node, node._lightQueueCounterLastOutput);
            }

            return result;
        };

        widget._lightQueueCounterCallbackInstalled = true;
    }
}

app.registerExtension({
    name: "LightQueueCounter.Title",

    beforeRegisterNodeDef(nodeType, nodeData) {
        if (!["LightQueueCounterTitleTap", "LightQueueCounterSetTitle"].includes(nodeData.name)) {
            return;
        }

        // Let ComfyUI resolve execution IDs (including subgraphs) in both renderers.
        const originalOnExecuted = nodeType.prototype.onExecuted;
        nodeType.prototype.onExecuted = function (...args) {
            const result = originalOnExecuted?.apply(this, args);
            installWidgetCallbacks(this);
            updateNodeTitle(this, args[0]);
            return result;
        };

        if (nodeData.name !== "LightQueueCounterTitleTap") {
            return;
        }

        const originalOnNodeCreated = nodeType.prototype.onNodeCreated;

        nodeType.prototype.onNodeCreated = function (...args) {
            const result = originalOnNodeCreated?.apply(this, args);
            installWidgetCallbacks(this);
            return result;
        };
    },
});
