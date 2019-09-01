#!/usr/bin/env python3

import json

from twisted.web.server import Site
from twisted.web.resource import Resource
from twisted.internet import reactor
from twisted.web.server import Request
from twisted.web.resource import ErrorPage

import requests


class BadRequestErrorPage(ErrorPage):

    def __init__(self, message="Bad request"):
        super().__init__(400, "Bad Request", message)


class MissingParameterException(Exception):

    def __init__(self, name: str):
        super().__init__('Parameter "{}" is required but was not provided'.format(name))


class InvalidCommandException(Exception):

    def __init__(self, name: str):
        super().__init__('Command "{}" is unsupported'.format(name))


class Relay(Resource):

    def __init__(self):
        super().__init__()

        self.TYPE_LIST = type([])
        self.TYPE_STR = type('')
        self.TYPE_BYTES = type(b'')

        self.commands = {
            '/divider': self.command_divider,
            '/rollfor': self.command_roll_for
        }

    def to_bytes(self, value):
        """
        :param value: either a str or a bytes object
        :return: a bytes object
        """
        return value if type(value) == self.TYPE_BYTES else value.encode('UTF-8')

    def to_str(self, value):
        """
        :param value: either a str or a bytes object
        :return: a str object
        """
        return value if type(value) == self.TYPE_STR else str(value, encoding='UTF-8')

    def unwrap_list(self, value):
        return value[0] if type(value) == self.TYPE_LIST and len(value) > 0 else value

    def read_required_parameter(self, name: str, request: Request):
        name_bytes = self.to_bytes(name)

        if name_bytes in request.args.keys():
            return request.args[name_bytes]

        raise MissingParameterException(name)

    def read_required_string_parameter(self, name: str, request: Request):
        return self.to_str(self.unwrap_list(self.read_required_parameter(name, request)))

    def command_divider(self, request: Request):
        return {
            'blocks': [
                {
                    "type": "divider"
                }
            ],
            "response_type": "in_channel"
        }

    def command_roll_for(self, request: Request):
        text = self.read_required_string_parameter('text', request)
        user_id = self.read_required_string_parameter('user_id', request)

        text = text.replace('*', '')
        text = text.replace('_', '')
        text = text.replace('~', '')
        text = text.strip()

        if len(text) == 0:
            text = 'initiative'

        return {
            'blocks': [
                {
                    "type": "divider"
                },
                {
                    "type": "section",
                    "text": {
                        "type": "mrkdwn",
                        "text": "<@{}> says *\"roll for {}!\"* :game_die::game_die::game_die:".format(user_id, text)
                    }
                }
            ],
            "response_type": "in_channel"
        }

    # noinspection PyMethodMayBeStatic,PyPep8Naming
    def render_GET(self, request: Request):
        return self.to_bytes('<html><body>Slack bot is running.</body></html>')

    # noinspection PyPep8Naming
    def render_POST(self, request: Request):
        try:
            command = self.read_required_string_parameter('command', request)

            if command not in self.commands:
                raise InvalidCommandException(command)

            response = self.commands[command](request)

            if response is not None:
                requests.post(
                    self.read_required_string_parameter('response_url', request),
                    timeout=15,
                    data=json.dumps(response),
                    headers={
                        'Content-Type': 'application/json'
                    }
                )

            request.setResponseCode(200)
            return self.to_bytes('')

        except MissingParameterException as e:
            return BadRequestErrorPage(str(e)).render(request)

        except InvalidCommandException as e:
            return BadRequestErrorPage(str(e)).render(request)


if __name__ == '__main__':
    slackbot = Resource()
    slackbot.putChild(b'dnd', Relay())

    root = Resource()
    root.putChild(b'webhook', slackbot)

    reactor.listenTCP(8080, Site(root))
    reactor.run()
