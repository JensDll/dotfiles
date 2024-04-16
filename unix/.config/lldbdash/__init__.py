import typing

import lldb
import lldbdash.commands
import lldbdash.dashboard
import lldbdash.modules


def __lldb_init_module(debugger: lldb.SBDebugger, internal_dict: dict):
    modules = [
        value
        for value in vars(lldbdash.modules).values()
        if lldbdash.modules.is_module(value)
    ]

    lldbdash.dashboard.Dashboard.modules = modules

    debugger.HandleCommand(
        "command container add --help 'The command container for the LLDB dashboard.' dashboard"
    )

    register_modules(debugger, modules)

    debugger.HandleCommand(
        "target stop-hook add --script-class lldbdash.dashboard.Dashboard"
    )


def register_modules(
    debugger: lldb.SBDebugger, modules: typing.Iterable[lldbdash.modules.Module]
):
    for module in modules:
        container = f"dashboard {module.name}"

        debugger.HandleCommand(
            f"command container add --help 'The command container for the {module.name} module.' {container}"
        )

        if settings := module.settings:
            settings_container = f"{container} settings"

            debugger.HandleCommand(f"command container add {settings_container}")
            debugger.HandleCommand(f"command container add {settings_container} set")
            debugger.HandleCommand(f"command container add {settings_container} show")

            for name, setting in settings.items():
                debugger.HandleCommand(
                    f"command script add --class {setting.handlers[0]} {settings_container} set {name}"
                )
                debugger.HandleCommand(
                    f"command script add --class {setting.show_command.handlers[0]} {settings_container} show {name}"
                )

            list_settings = lldbdash.commands.ListSettingsCommand(
                settings, help=f"List the settings values of the {module.name} module."
            )

            debugger.HandleCommand(
                f"command script add --class {list_settings.handlers[0]} {settings_container} list"
            )

        debugger.HandleCommand(
            f"command script add --class {module.enabled.handlers[0]} {container} enable"
        )
        debugger.HandleCommand(
            f"command script add --class {module.enabled.handlers[1]} {container} disable"
        )

        set_container = f"{container} set"
        show_container = f"{container} show"

        debugger.HandleCommand(f"command container add {show_container}")
        debugger.HandleCommand(f"command container add {set_container}")

        debugger.HandleCommand(
            f"command script add --class {module.output.handlers[0]} --completion-type disk-file {set_container} output"
        )
        debugger.HandleCommand(
            f"command script add --class {module.output.show_command.handlers[0]} {show_container} output"
        )
