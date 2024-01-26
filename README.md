SublimeLinter-contrib-ruff
==========================

[![Build Status](https://travis-ci.org/SublimeLinter/SublimeLinter-contrib-ruff.svg?branch=master)](https://travis-ci.org/SublimeLinter/SublimeLinter-contrib-ruff)

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


## Settings
- SublimeLinter settings: http://sublimelinter.readthedocs.org/en/latest/settings.html
- Linter settings: http://sublimelinter.readthedocs.org/en/latest/linter_settings.html

Additional SublimeLinter-ruff settings:

|Setting|Description    |
|:------|:--------------|
|no-cache                  |Default: `True`.  As this plugin by default runs on every python file, turn the cache off.  `ruff` is already fast without a cache but turn this back on (`false`) on projects.|
|disable_if_not_dependency |Default: `False`.  If set to `true`, use only locally installed `ruff` executables from virtual environments or skip linting the project.
|check_for_local_configuration |Set to `true` to check for a local "ruff.toml" configuration file. Skip running ruff if such a file cannot be found.[1]|


[1] Unfortunately "pyproject.toml" detection is not implemented as we don't have a toml parser at hand in Python 3.3 (yik, we run 3.3 here). (TODO?)
