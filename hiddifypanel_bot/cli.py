"""CLI interface for hiddifypanel_bot project.

Be creative! do whatever you want!

- Install click or typer and create a CLI app
- Use builtin argparse
- Start a web application
- Import things from your .base module
"""
from . import utils

def main():  # pragma: no cover
    utils.setup_translation()
    import i18n
    print(i18n.t("start",locale='fa'))