"""CLI interface for hiddifypanel_bot project.

Be creative! do whatever you want!

- Install click or typer and create a CLI app
- Use builtin argparse
- Start a web application
- Import things from your .base module
"""
import asyncio
from . import utils
from . import basebot
def main():  # pragma: no cover
    utils.setup_translation()
    # import i18n
    # print(i18n.t("start",locale='fa'))
    # asyncio.run(basebot.bot.polling(restart_on_change=True))
    asyncio.run(basebot.bot.polling())
    