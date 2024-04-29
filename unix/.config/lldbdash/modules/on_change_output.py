import lldb
from lldbdash.common import g_file_streams


def on_change_output(prev_output: str, current_output: str):
    if current_output != "0":
        add_or_increase(current_output)

    if prev_output != "0":
        remove_or_decrease(prev_output)


def add_or_increase(key: str):
    entry = g_file_streams.setdefault(
        key, {"stream": lldb.SBStream(), "num_writers": 0}
    )
    if entry["num_writers"] == 0:
        entry["stream"].RedirectToFile(key, True)
    entry["num_writers"] += 1


def remove_or_decrease(key: str):
    entry = g_file_streams[key]
    entry["num_writers"] -= 1
    if entry["num_writers"] == 0:
        entry["stream"].Clear()
        del g_file_streams[key]
