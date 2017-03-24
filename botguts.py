#!/usr/bin/env python3
'''
Containers for a modular slack bot.
'''
import os
from slackclient import SlackClient
import time

BOT_NAME = 'acebot_not'
BOT_ID = os.environ.get("BOT_ID")

AT_BOT = "<@" + BOT_ID + ">"
slack_client = SlackClient(os.environ.get('SLACK_BOT_TOKEN'))


class Bot_Command(object):
    """A container for a slack bot command that contains call and response"""

    def __init__(self,
                 call,
                 response,
                 name=None,
                 category='default',
                 docs="I don't know any more about this"):
        super(Bot_Command, self).__init__()
        self.call = call  # What the slack bot listens for.
        self.response = response  # How the slackbot responds.
        self.category = category
        self.docs = 'help'  # Not yet used - could default to the docstring for response??
        if name:
            self.name = name
        else:
            name = response.__name__

    def use_this(self, command):
        return command.startswith(self.call)


class Slack_Bot(object):
    """docstring for Slack_Bot"""

    def __init__(self, bot_commands=[]):
        super(Slack_Bot, self).__init__()
        self.bot_commands = bot_commands
        self.categories = set()

    def register(self, module):
        self.bot_commands.extend(module.bot_commands)
        for comm in self.bot_commands:
            self.categories.add(comm.category)

    def parse_slack_output(self, slack_rtm_output):
        output_list = slack_rtm_output
        if output_list and len(output_list) > 0:
            for output in output_list:
                if output and 'text' in output and AT_BOT in output['text']:
                    return output['text'].split(AT_BOT)[1].strip().lower(), output['channel'], output['ts']
        return None, None, None

    def handle_command(self, command, channel, ts):
        response = []
        for comm in self.bot_commands:
            if comm.use_this(command):
                answer = comm.response(command)
                if isinstance(answer, str):
                    response.append(comm.response(command))
                else:
                    response.extend(comm.response(command))

        if not response:
            response = ["Sorry, I don't know that command."]

        for out in response:
            print(out)
            slack_client.api_call("chat.postMessage", channel=channel, text=out, as_user=True)

    def connect_and_run(self):
        READ_WEBSOCKET_DELAY = 1
        if slack_client.rtm_connect():
            print(BOT_NAME + " connected and running!")
            while True:
                command, channel, ts = self.parse_slack_output(slack_client.rtm_read())
                if command and channel:
                    self.handle_command(command, channel, ts)
                time.sleep(READ_WEBSOCKET_DELAY)
        else:
            print("Connection failed.  Invalid Slack token or bot ID?")
