#! /usr/bin/env python3
from botguts import Slack_Bot  # , Bot_Command
from importlib import import_module
import sys

asdbot_not = Slack_Bot()

# help_command = Bot_Command(
#     call='help',
#     response=asdbot.helper,
#     name='help',
#     category='default',
#     docs=[
#         "Usage, @asdbot help (something)",
#         "Tells you the categories if you don't include (something)",
#         "Tells you the functions available in a category",
#         "or gives the documentation for a function"
#     ]
# )
# asdbot.bot_commands.append(help_command)

with open('module_list.txt', 'r') as f:
    for line in f:
        mod = line.strip()
        mod = mod.replace(r'/', '.')
        import_module(mod)
        asdbot_not.register(sys.modules[mod])

if __name__ == '__main__':
    asdbot_not.connect_and_run()
