from server import PromptServer


class AnyType(str):
    """
    ComfyUI custom nodeでよく使われるANY型。
    型チェック時に他の型と不一致扱いされないようにする。
    """
    def __ne__(self, other):
        return False


ANY_TYPE = AnyType("*")

def make_title_payload(label, running, pending, total):
    return {
        "label": label,
        "running": running,
        "pending": pending,
        "total": total,
    }

def get_queue_counts():
    """
    /queue APIを叩かず、ComfyUI内部のPromptQueueから件数だけ読む。
    大量キュー時でも軽くするため、巨大なqueue配列のJSON化はしない。
    """
    server = getattr(PromptServer, "instance", None)
    if server is None:
        return 0, 0, 0

    prompt_queue = getattr(server, "prompt_queue", None)
    if prompt_queue is None:
        return 0, 0, 0

    # 最軽量ルート。
    if all(hasattr(prompt_queue, name) for name in ("queue", "currently_running", "mutex")):
        with prompt_queue.mutex:
            pending = len(prompt_queue.queue)
            running = len(prompt_queue.currently_running)
            total = pending + running
            return running, pending, total

    # 保険。
    if hasattr(prompt_queue, "get_tasks_remaining"):
        total = prompt_queue.get_tasks_remaining()
        return 0, total, total

    # 最終手段。大量キュー時はやや重い。
    if hasattr(prompt_queue, "get_current_queue_volatile"):
        running_items, pending_items = prompt_queue.get_current_queue_volatile()
        running = len(running_items)
        pending = len(pending_items)
        return running, pending, running + pending

    return 0, 0, 0


def make_status(label, running, pending, total):
    return f"{label}: running={running}, pending={pending}, total={total}"


def make_title(label, running, pending, total, title_format):
    """
    折りたたみタイトル用の短い表示を作る。
    total: queue: 500
    short: queue: 1/499/500
    full : queue: running=1, pending=499, total=500
    """
    if title_format == "total":
        return f"{label}: {total}"

    if title_format == "short":
        return f"{label}: {running}/{pending}/{total}"

    return make_status(label, running, pending, total)


class LightQueueCounterAnyPassthrough:
    """
    何でも受けて、何でもそのまま返す軽量キューカウンター。
    画像、latent、conditioning、model、文字列など、任意の経路に差し込める。
    """

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "value": (ANY_TYPE, {"forceInput": True}),
            },
            "optional": {
                "label": ("STRING", {"default": "queue", "multiline": False}),
                "title_format": (["total", "short", "full"], {"default": "total"}),
                "print_to_console": ("BOOLEAN", {"default": True}),
            },
        }

    RETURN_TYPES = (ANY_TYPE, "STRING", "STRING", "INT", "INT", "INT")
    RETURN_NAMES = ("value", "status", "title", "running", "pending", "total")
    FUNCTION = "run"
    CATEGORY = "utils/queue"

    def run(self, value, label="queue", title_format="total", print_to_console=True):
        running, pending, total = get_queue_counts()

        status = make_status(label, running, pending, total)
        title = make_title(label, running, pending, total, title_format)

        if print_to_console:
            print(f"[LightQueueCounter] {status}")

        return (value, status, title, running, pending, total)


class LightQueueCounterSetTitle:
    """
    文字列を受け取り、自分自身のノードタイトルに設定する表示用ノード。
    AnyPassthrough の status または title を接続して使う。
    """

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "title": ("STRING", {"forceInput": True}),
            },
        }

    RETURN_TYPES = ("STRING",)
    RETURN_NAMES = ("title",)
    FUNCTION = "run"
    OUTPUT_NODE = True
    CATEGORY = "utils/queue"

    @classmethod
    def IS_CHANGED(cls, title):
        # 表示専用なので毎回実行させる。
        return float("nan")

    def run(self, title):
        title = str(title).replace("\n", " ").strip()

        return {
            "ui": {
                "light_queue_counter_title": [title],
                "text": [title],
            },
            "result": (title,),
        }


class LightQueueCounterTitleTap:
    """
    任意の値をトリガーとして受け取り、キュー件数を読んで自分のタイトルに表示する。
    メイン経路を変更したくない場合に枝分かれで置く。
    """

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "trigger": (ANY_TYPE, {"forceInput": True}),
            },
            "optional": {
                "label": ("STRING", {"default": "queue", "multiline": False}),
                "title_format": (["total", "short", "full"], {"default": "total"}),
                "print_to_console": ("BOOLEAN", {"default": False}),
            },
        }

    RETURN_TYPES = ()
    FUNCTION = "run"
    OUTPUT_NODE = True
    CATEGORY = "utils/queue"

    @classmethod
    def IS_CHANGED(cls, trigger, label="queue", title_format="total", print_to_console=False):
        # 表示専用なので毎回実行させる。
        return float("nan")

    def run(self, trigger, label="queue", title_format="total", print_to_console=False):
        running, pending, total = get_queue_counts()

        status = make_status(label, running, pending, total)
        title = make_title(label, running, pending, total, title_format)
        payload = make_title_payload(label, running, pending, total)

        if print_to_console:
            print(f"[LightQueueCounter] {status}")

        return {
            "ui": {
                "light_queue_counter_title": [title],
                "light_queue_counter_payload": [payload],
                "text": [status],
            },
            "result": (),
        }


NODE_CLASS_MAPPINGS = {
    "LightQueueCounterAnyPassthrough": LightQueueCounterAnyPassthrough,
    "LightQueueCounterSetTitle": LightQueueCounterSetTitle,
    "LightQueueCounterTitleTap": LightQueueCounterTitleTap,
}

NODE_DISPLAY_NAME_MAPPINGS = {
    "LightQueueCounterAnyPassthrough": "Light Queue Counter Any Passthrough",
    "LightQueueCounterSetTitle": "Light Queue Counter Set Title",
    "LightQueueCounterTitleTap": "Light Queue Counter Title Tap",
}