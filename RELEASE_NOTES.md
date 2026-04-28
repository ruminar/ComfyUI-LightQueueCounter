## v0.1.0

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