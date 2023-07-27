import gdb  # pyright: ignore [reportMissingModuleSource]

from .dashboard import Dashboard


def custom_prompt(current_prompt):  # type: (str) -> str
    # https://sourceware.org/gdb/current/onlinedocs/gdb.html/gdb_002eprompt.html#gdb_002eprompt
    prompt = gdb.prompt.substitute_prompt(r">>> ")
    return prompt


def start():
    gdb.prompt_hook = custom_prompt
    Dashboard()
