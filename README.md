SublimeLinter-contrib-ruff
==========================

This linter plugin for [SublimeLinter](https://github.com/SublimeLinter/SublimeLinter) provides an interface to [ruff](https://docs.astral.sh/ruff/). It will be used with files that have the “Python” syntax.

## Installation
SublimeLinter must be installed in order to use this plugin. 

Please use [Package Control](https://packagecontrol.io) to install the linter plugin.

Before installing this plugin, you must ensure that `ruff` is installed on your system. Typically

```
pip install ruff
# or:
rye install ruff
```

will do that.  You can also install it into a virtual environment and SublimeLinter will find it.

## Quick Fixes

`ruff` provides fixes for some errors.  These fixes are available in SublimeLinter as quick actions. See the Command Palette: `SublimeLinter: Quick Action`.  (Also: https://github.com/SublimeLinter/SublimeLinter#quick-actionsfixers)

![image](https://github.com/kaste/SublimeLinter-contrib-ruff/assets/8558/5dd3507a-4b30-442d-ace2-c5840c13d454)

You may want to define a key binding:

```
    // To trigger a quick action
    { "keys": ["ctrl+k", "ctrl+f"],
      "command": "sublime_linter_quick_actions"
    },
```


## Settings
- SublimeLinter settings: http://sublimelinter.readthedocs.org/en/latest/settings.html
- Linter settings: http://sublimelinter.readthedocs.org/en/latest/linter_settings.html

Additional SublimeLinter-ruff settings:

|Setting|Description    |
|:------|:--------------|
|no-cache                  |Default: `True`.  Turn the cache off as this plugin runs on every python file by default.  `ruff` is probably fast enough without a cache but you may turn this back "on" (`false`) on projects.|
|disable_if_not_dependency |Default: `False`.  If set to `true`, use only locally installed `ruff` executables from virtual environments or skip linting the project.
|check_for_local_configuration |Default: `False`. Set to `true` to check for a local "ruff.toml" configuration file. Skip running ruff if such a file cannot be found.[1]|


[1] "pyproject.toml" detection is not implemented (yet?).

