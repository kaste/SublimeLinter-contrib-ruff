from functools import partial
import json
import logging
import os

import sublime

from SublimeLinter.lint import LintMatch, PermanentError, PythonLinter
from SublimeLinter.lint.quick_fix import (
    TextRange, QuickAction, add_at_eol, ignore_rules_inline,
    extend_existing_comment, line_error_is_on,
    merge_actions_by_code_and_line, quick_actions_for,
)

packages_path = sublime.packages_path()


MYPY = False
if MYPY:
    from typing import List, Iterator, Optional
    from SublimeLinter.lint import util
    from SublimeLinter.lint.linter import VirtualView
    from SublimeLinter.lint.persist import LintError


class Ruff(PythonLinter):
    cmd = 'ruff check --output-format=json -'
    regex = None
    defaults = {
        "selector": "source.python",
        # As we run automatically everywhere, turn off the cache to
        # not create a temp-file-mess.
        "--no-cache": True,
        # Check for "ruff.toml" and ".ruff.toml" configuration files
        # and skip linting otherwise.
        "check_for_local_configuration": False,
    }
    config_file_names = ("ruff.toml", ".ruff.toml", )

    def run(self, cmd, code):
        cwd = self.get_working_dir()
        if (
            self.context.get("file", "").startswith(packages_path)
            and os.path.exists(os.path.join(cwd, "mypy.ini"))
            and not os.path.exists(os.path.join(cwd, ".python-version"))
        ):
            self.logger.info(
                "Skip ruff: no '.python-version' file found at '{}' "
                "but mypy is configured. This can lead to false positives as "
                "ruff does not read type comments."
                .format(cwd)
            )
            self.notify_unassign()
            raise PermanentError(
                "assume file contains type comments that ruff does not read"
            )

        if (
            self.settings.get("check_for_local_configuration")
            and cwd and not any(
                os.path.exists(os.path.join(cwd, name))
                for name in self.config_file_names
            )
        ):
            self.logger.info(
                "Skip ruff: no local configuration found at '{}'".format(cwd)
            )
            self.notify_unassign()
            raise PermanentError("no local configuration found")
        return super().run(cmd, code)

    def parse_output(self, proc, virtual_view):
        # type: (util.popen_output, VirtualView) -> Iterator[LintError]
        # stderr is noisy e.g.
        # error: Failed to parse at 155:15: Unexpected token 'QuickAction'
        # but these also appear well formatted on `stdout`
        if proc.stderr.strip() and not proc.stdout.strip():
            self.on_stderr(proc.stderr)

        if not proc.stdout:
            self.logger.info('{}: no output'.format(self.name))
            return

        try:
            content = json.loads(proc.stdout)
        except ValueError:
            self.logger.error(
                "JSON Decode error: We expected JSON from 'ruff', "
                "but instead got this:\n{}\n\n"
                .format(proc.stdout)
            )
            self.notify_failure()
            return

        if self.logger.isEnabledFor(logging.INFO):
            import pprint
            self.logger.info(
                '{} output:\n{}'.format(self.name, pprint.pformat(content)))

        """
          {
            "cell": null,
            "code": "E501",
            "end_location": {
              "column": 140,
              "row": 24
            },
            "filename": "~\\api.py",
            "fix": null,
            "location": {
              "column": 121,
              "row": 24
            },
            "message": "Line too long (139 > 120)",
            "noqa_row": 24,
            "url": "https://docs.astral.sh/ruff/rules/line-too-long"
          }
        """

        for item in content:
            code = item["code"]
            match = LintMatch(
                match=item,
                filename=item["filename"],
                line=item["location"]["row"] - 1,
                col=item["location"]["column"] - 1,
                end_line=item["end_location"]["row"] - 1,
                end_col=item["end_location"]["column"] - 1,
                error_type="error" if code.startswith("F") else "warning",
                code=code,
                message=item["message"],
            )
            error = self.process_match(match, virtual_view)
            if error:
                try:
                    fix_description = item["fix"]
                except KeyError:
                    pass
                else:
                    if fix_description:
                        error["fix"] = fix_description
                yield error


@quick_actions_for("ruff")
def ruff_fixes_provider(errors, _view):
    # type: (List[LintError], Optional[sublime.View]) -> Iterator[QuickAction]
    def make_action(error):
        # type: (LintError) -> QuickAction
        return QuickAction(
            "ruff: {fix[message]}".format(**error),
            partial(ruff_fix_error, error),
            "{msg}".format(**error),
            solves=[error]
        )

    except_ = lambda error: "fix" not in error
    yield from merge_actions_by_code_and_line(make_action, except_, errors, _view)


def ruff_fix_error(error, view) -> "Iterator[TextRange]":
    """
    "fix": {
      "applicability": "safe",
      "edits": [
        {
          "content": "...",
          "end_location": {
            "column": 1,
            "row": 26
          },
          "location": {
            "column": 1,
            "row": 1
          }
        }
      ],
      "message": "Organize imports"
    },
    """
    fix_description = error["fix"]
    for edit in fix_description["edits"]:
        line = edit["location"]["row"] - 1
        col = edit["location"]["column"] - 1
        end_line = edit["end_location"]["row"] - 1
        end_col = edit["end_location"]["column"] - 1
        region = sublime.Region(
            view.text_point(line, col),
            view.text_point(end_line, end_col)
        )
        yield TextRange(edit["content"], region)


@ignore_rules_inline("ruff", except_for={
    # some indentation rules are not stylistic in python
    # the following violations cannot be ignored
    "E112",  # expected an indented block
    "E113",  # unexpected indentation
    "E116",  # unexpected indentation (comment)
    "E901",  # SyntaxError or IndentationError
    "E902",  # IOError
    "E999",  # SyntaxError
    "F722",  # syntax error in forward annotation
})
def ignore_ruff_code(error, view):
    # type: (LintError, sublime.View) -> Iterator[TextRange]
    line = line_error_is_on(view, error)
    code = error["code"]
    yield (
        extend_existing_comment(
            r"(?i)# noqa:[\s]?(?P<codes>[A-Z]+[0-9]+((?:,\s?)[A-Z]+[0-9]+)*)",
            ", ",
            {code},
            line
        )
        or add_at_eol(
            "  # noqa: {}".format(code),
            line
        )
    )
