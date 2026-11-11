## 0.1.1

### Fixes

- Route Title Tap and Set Title updates through ComfyUI's shared `onExecuted` callback for Legacy Nodes and Nodes 2.0.
- Remove numeric node-ID conversion and delegate execution-target resolution to ComfyUI.
- Preserve existing Python APIs, workflow node identifiers, inputs, outputs, and queue-counting behavior.

### Validation

- Pass 8 JavaScript tests and 5 Python tests.
- User reported successful operation after testing; renderer versions and individual checklist results were not recorded.
- See [compatibility notes](docs/nodes-2-compatibility.md) for official-source references and the manual verification checklist.

## 0.1.0

Initial release.

### Features

- Add lightweight queue counter nodes for ComfyUI
- Read queue counts directly from ComfyUI backend without polling `/queue`
- Add Any Passthrough node
- Add Title Tap node for folded-node title display
- Support title formats: `total`, `short`, and `full`
- Support live label/title format switching based on the latest executed result

### Notes

This node updates when the workflow node is executed. It does not use a timer-based polling loop.
