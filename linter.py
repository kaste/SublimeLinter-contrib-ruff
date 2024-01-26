import json
import logging
import os

from SublimeLinter.lint import LintMatch, PermanentError, PythonLinter


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

    def find_errors(self, output):
        try:
            content = json.loads(output)
        except ValueError:
            self.logger.error(
                "JSON Decode error: We expected JSON from 'ruff', "
                "but instead got this:\n{}\n\n"
                .format(output)
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

        for match in content:
            code = match["code"]
            yield LintMatch(
                match=match,
                filename=match["filename"],
                line=match["location"]["row"] - 1,
                col=match["location"]["column"] - 1,
                end_line=match["end_location"]["row"] - 1,
                end_col=match["end_location"]["column"] - 1,
                error_type="error" if code.startswith("F") else "warning",
                code=code,
                message=match["message"],

            )
