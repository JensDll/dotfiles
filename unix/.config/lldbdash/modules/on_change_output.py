import lldb
from lldbdash.common import file_streams


def is_file(output: str):
    return output != "0"


def on_change_output(prev_output: str, current_output: str):
    if is_file(current_output):
        add_or_increase(current_output)

    if is_file(prev_output):
        remove_or_decrease(prev_output)


def add_or_increase(key: str):
    entry = file_streams.setdefault(key, {"stream": lldb.SBStream(), "num_writers": 0})
    if entry["num_writers"] == 0:
        entry["stream"].RedirectToFile(key, True)
    entry["num_writers"] += 1


def remove_or_decrease(key: str):
    entry = file_streams[key]
    entry["num_writers"] -= 1
    if entry["num_writers"] == 0:
        entry["stream"].Clear()
        del file_streams[key]
