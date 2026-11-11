"""Backend contract tests without importing a ComfyUI installation."""
import contextlib
import importlib.util
import io
import math
from pathlib import Path
import sys
import threading
import types
import unittest
from unittest.mock import patch

server = types.ModuleType("server")
server.PromptServer = type("PromptServer", (), {"instance": None})
spec = importlib.util.spec_from_file_location("counter_nodes", Path(__file__).resolve().parents[1] / "nodes.py")
nodes = importlib.util.module_from_spec(spec)
with patch.dict(sys.modules, {"server": server}):
    spec.loader.exec_module(nodes)


class NodeTests(unittest.TestCase):
    def tearDown(self):
        server.PromptServer.instance = None

    def queue(self, queue):
        server.PromptServer.instance = types.SimpleNamespace(prompt_queue=queue)

    def test_queue_counts_and_fallbacks(self):
        self.assertEqual(nodes.get_queue_counts(), (0, 0, 0))
        self.queue(types.SimpleNamespace())
        self.assertEqual(nodes.get_queue_counts(), (0, 0, 0))
        self.queue(types.SimpleNamespace(queue=[1, 2], currently_running={1: object()}, mutex=threading.RLock()))
        self.assertEqual(nodes.get_queue_counts(), (1, 2, 3))
        self.queue(types.SimpleNamespace(get_tasks_remaining=lambda: 7))
        self.assertEqual(nodes.get_queue_counts(), (0, 7, 7))
        self.queue(types.SimpleNamespace(get_current_queue_volatile=lambda: ([1], [2, 3])))
        self.assertEqual(nodes.get_queue_counts(), (1, 2, 3))

    def test_workflow_contract(self):
        expected = {
            "LightQueueCounterAnyPassthrough": (["value"], ["label", "title_format", "print_to_console"], ("value", "status", "title", "running", "pending", "total")),
            "LightQueueCounterSetTitle": (["title"], [], ("title",)),
            "LightQueueCounterTitleTap": (["trigger"], ["label", "title_format", "print_to_console"], ()),
        }
        self.assertEqual(set(nodes.NODE_CLASS_MAPPINGS), set(expected))
        for name, (required, optional, outputs) in expected.items():
            cls = nodes.NODE_CLASS_MAPPINGS[name]
            inputs = cls.INPUT_TYPES()
            self.assertEqual(list(inputs["required"]), required)
            self.assertEqual(list(inputs.get("optional", {})), optional)
            self.assertEqual(getattr(cls, "RETURN_NAMES", ()), outputs)
            self.assertEqual(len(cls.RETURN_TYPES), len(outputs))

    def test_passthrough_identity_and_outputs(self):
        self.queue(types.SimpleNamespace(queue=[1, 2], currently_running={1: object()}, mutex=threading.RLock()))
        value = object()
        for fmt, title in [("total", "q: 3"), ("short", "q: 1/2/3"), ("full", "q: running=1, pending=2, total=3")]:
            result = nodes.LightQueueCounterAnyPassthrough().run(value, "q", fmt, False)
            self.assertIs(result[0], value)
            self.assertEqual(result[1:], ("q: running=1, pending=2, total=3", title, 1, 2, 3))

    def test_title_tap_payload_and_console(self):
        with contextlib.redirect_stdout(io.StringIO()) as console:
            result = nodes.LightQueueCounterTitleTap().run(object(), print_to_console=True)
        self.assertEqual(result["result"], ())
        self.assertEqual(result["ui"]["light_queue_counter_payload"], [{"label": "queue", "running": 0, "pending": 0, "total": 0}])
        self.assertEqual(result["ui"]["light_queue_counter_title"], ["queue: 0"])
        self.assertIn("[LightQueueCounter]", console.getvalue())

    def test_set_title_and_always_execute(self):
        result = nodes.LightQueueCounterSetTitle().run("  first\nsecond  ")
        self.assertEqual(result["result"], ("first second",))
        self.assertEqual(result["ui"]["light_queue_counter_title"], ["first second"])
        self.assertTrue(math.isnan(nodes.LightQueueCounterSetTitle.IS_CHANGED("x")))
        self.assertTrue(math.isnan(nodes.LightQueueCounterTitleTap.IS_CHANGED(object())))


if __name__ == "__main__":
    unittest.main()
