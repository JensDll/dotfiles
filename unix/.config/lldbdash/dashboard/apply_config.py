import json
import pathlib
import typing

if typing.TYPE_CHECKING:
    from lldbdash.modules import Module

    from .dashboard import Dashboard


def apply_config(path: pathlib.Path, dashboard: "Dashboard"):
    with open(path) as f:
        json_config = json.load(f)

    dashboard.enabled.set_value(json_config["enabled"])
    for name, value in json_config["settings"].items():
        dashboard.get_settings()[name].set_value(value)

    for name, json_module in json_config["modules"].items():
        module: "Module" = next(filter(lambda m: m.name == name, dashboard.modules))
        module.enabled.set_value(json_module["enabled"])
        for name, value in json_module["settings"].items():
            module.settings[name].set_value(value)
