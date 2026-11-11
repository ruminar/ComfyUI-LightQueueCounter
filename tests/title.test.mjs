import assert from "node:assert/strict";
import { readFileSync } from "node:fs";
import test from "node:test";
import vm from "node:vm";

const source = readFileSync(new URL("../web/light_queue_counter_title.js", import.meta.url), "utf8")
    .replace('import { app } from "../../../scripts/app.js";', "");

function fixture(name = "LightQueueCounterTitleTap", original = {}) {
    let extension;
    let dirty = 0;
    const app = {
        registerExtension(value) { extension = value; },
        // No getNodeById: output delivery must not look up or coerce node IDs.
        graph: { setDirtyCanvas() { dirty++; } },
    };
    vm.runInNewContext(source, { app });
    class Node {
        constructor() {
            this.id = "subgraph:non-numeric-id";
            this.widgets = [
                { name: "label", value: "queue" },
                { name: "title_format", value: "total" },
            ];
        }
        setDirtyCanvas() { dirty++; }
    }
    Object.assign(Node.prototype, original);
    extension.beforeRegisterNodeDef(Node, { name });
    const node = new Node();
    node.onNodeCreated?.();
    return { node, Node, dirty: () => dirty };
}

const output = {
    light_queue_counter_title: ["queue: 3"],
    light_queue_counter_payload: [{ label: "backend", running: 1, pending: 2, total: 3 }],
};

test("execution updates only its receiving node and requests redraw", () => {
    const { node, Node, dirty } = fixture();
    const other = new Node();
    node.onExecuted(output);
    assert.equal(node.title, "queue: 3");
    assert.equal(other.title, undefined);
    assert.equal(dirty(), 2);
});

test("title assignment reaches a renderer's property setter", () => {
    const { node } = fixture();
    const writes = [];
    Object.defineProperty(node, "title", { set(value) { writes.push(value); } });
    node.onExecuted(output);
    assert.deepEqual(writes, ["queue: 3"]);
});

test("label and all title formats change without another execution", () => {
    const { node } = fixture();
    node.onExecuted(output);
    const [label, format] = node.widgets;
    label.value = " jobs ";
    label.callback(label.value);
    assert.equal(node.title, "jobs: 3");
    format.value = "short";
    format.callback(format.value, {}, node);
    assert.equal(node.title, "jobs: 1/2/3");
    format.value = "full";
    format.callback(format.value);
    assert.equal(node.title, "jobs: running=1, pending=2, total=3");
    label.value = " ";
    label.callback(label.value);
    assert.match(node.title, /^queue:/);
});

test("existing hooks keep this, arguments and return values", () => {
    const calls = [];
    const { node } = fixture("LightQueueCounterTitleTap", {
        onNodeCreated(...args) { calls.push([this, args]); return 17; },
        onExecuted(...args) { calls.push([this, args]); return 23; },
    });
    assert.equal(node.onNodeCreated("created"), 17);
    assert.equal(node.onExecuted(output, "extra"), 23);
    assert.equal(calls.at(-1)[0], node);
    assert.deepEqual(calls.at(-1)[1], [output, "extra"]);
});

test("widget callback is wrapped once and preserves its contract", () => {
    const { node } = fixture("LightQueueCounterTitleTap", {
        onNodeCreated() {
            this.widgets[0].callback = function (...args) {
                assert.equal(this, node.widgets[0]);
                assert.deepEqual(args, ["changed", 2, node]);
                return 31;
            };
        },
    });
    const callback = node.widgets[0].callback;
    node.onExecuted(output);
    node.onExecuted(output);
    assert.equal(node.widgets[0].callback, callback);
    assert.equal(node.widgets[0].callback("changed", 2, node), 31);
});

test("Set Title accepts title-only output with no widgets", () => {
    const { node } = fixture("LightQueueCounterSetTitle");
    delete node.widgets;
    node.onExecuted({ light_queue_counter_title: [" custom title "] });
    assert.equal(node.title, "custom title");
});

test("missing widgets use payload label; unrelated or empty output is ignored", () => {
    const { node } = fixture();
    delete node.widgets;
    node.onExecuted(output);
    assert.equal(node.title, "backend: 3");
    for (const value of [undefined, {}, { text: ["unrelated"] }, { light_queue_counter_title: [""] }]) {
        node.onExecuted(value);
        assert.equal(node.title, "backend: 3");
    }
});

test("other node types are not patched", () => {
    const { node } = fixture("LightQueueCounterAnyPassthrough");
    assert.equal(node.onExecuted, undefined);
    assert.equal(node.onNodeCreated, undefined);
});
