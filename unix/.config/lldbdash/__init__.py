import lldb
import lldbdash.commands
import lldbdash.dashboard
import lldbdash.modules


def __lldb_init_module(debugger: lldb.SBDebugger, internal_dict: dict):
    register_dashboard(debugger)
    register_modules(debugger)


def register_dashboard(debugger: lldb.SBDebugger):
    lldbdash.dashboard.Dashboard.modules = [
        value
        for value in vars(lldbdash.modules).values()
        if lldbdash.modules.is_module(value)
    ]

    container = "dashboard"

    debugger.HandleCommand(
        f"command container add --help 'The command container for the LLDB dashboard.' {container}"
    )

    debugger.HandleCommand(
        "target stop-hook add --script-class lldbdash.dashboard.Dashboard"
    )

    stop_hook_id = get_stop_hook_id(debugger)

    def on_toggle(prev_value: bool, value: bool):
        if not prev_value and value:
            debugger.HandleCommand(f"target stop-hook enable {stop_hook_id}")
            return

        if prev_value and not value:
            debugger.HandleCommand(f"target stop-hook disable {stop_hook_id}")

    enabled = lldbdash.dashboard.Dashboard.enabled = lldbdash.commands.ToggleCommand(
        True,
        enable_help="Enable the dashboard.",
        disable_help="Disable the dashboard.",
        on_change=on_toggle,
    )

    debugger.HandleCommand(
        f"command script add --class {enabled.handlers[0]} {container} enable"
    )
    debugger.HandleCommand(
        f"command script add --class {enabled.handlers[1]} {container} disable"
    )

    debugger.HandleCommand(
        f"command script add --class lldbdash.dashboard.PrintCommand {container} print",
    )

    debugger.HandleCommand(
        f"command script add --class lldbdash.dashboard.DumpCommand {container} dump",
    )
    debugger.HandleCommand(
        f"command script add --class lldbdash.dashboard.LoadCommand {container} load",
    )

    settings = lldbdash.dashboard.Dashboard.get_settings()

    register_settings(
        settings,
        debugger,
        container,
        lldbdash.commands.ListSettingsCommand(
            settings, help=f"List the dashboard settings."
        ),
    )


def register_modules(debugger: lldb.SBDebugger):
    for module in lldbdash.dashboard.Dashboard.modules:
        container = f"dashboard {module.name}"

        debugger.HandleCommand(
            f"command container add --help 'The command container for the {module.name} module.' {container}"
        )

        if settings := module.settings:
            register_settings(
                settings,
                debugger,
                container,
                lldbdash.commands.ListSettingsCommand(
                    settings, help=f"List the {module.name} settings."
                ),
            )

        debugger.HandleCommand(
            f"command script add --class {module.enabled.handlers[0]} {container} enable"
        )
        debugger.HandleCommand(
            f"command script add --class {module.enabled.handlers[1]} {container} disable"
        )


def register_settings(
    settings: dict[str, lldbdash.commands.Command],
    debugger: lldb.SBDebugger,
    container: str,
    list_command: lldbdash.commands.ListSettingsCommand,
):
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

    debugger.HandleCommand(
        f"command script add --class {list_command.handlers[0]} {settings_container} list"
    )


def get_stop_hook_id(debugger: lldb.SBDebugger):
    ci: lldb.SBCommandInterpreter = debugger.GetCommandInterpreter()
    result = lldb.SBCommandReturnObject()
    ci.HandleCommand("target stop-hook list", result)
    output: str = result.GetOutput()
    lines = output.splitlines()
    for i, line in enumerate(lines):
        if line.endswith("lldbdash.dashboard.Dashboard"):
            return int(lines[i - 2][-1])
    raise Exception(
        'Failed to determine stop hook id from "target stop-hook list" output. Dashboard failed to initialize.'
    )
