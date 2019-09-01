#!/usr/bin/env python3

# Copyright 2019-2019 Gryphon Zone
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import json

from twisted.web.server import Site
from twisted.web.resource import Resource
from twisted.internet import reactor
from twisted.web.server import Request
from twisted.web.resource import ErrorPage

import requests


class BadRequestErrorPage(ErrorPage):
    """
    Resource page for client errors (400 status code)
    """

    def __init__(self, message="Bad request"):
        super().__init__(400, "Bad Request", message)


class MissingParameterException(Exception):
    """
    Exception indicating a required parameter was not provided
    """

    def __init__(self, name: str):
        """
        :param name: name of the missing parameter
        """
        super().__init__('Parameter "{}" is required but was not provided'.format(name))


class InvalidCommandException(Exception):
    """
    Exception indicating an invalid command was used
    """

    def __init__(self, name: str):
        """
        :param name: name of the invalid command
        """
        super().__init__('Command "{}" is unsupported'.format(name))


class SlackDndSlashCommandWebhook(Resource):
    """
    Class containing logic for handling slash command webhooks
    """

    def __init__(self):
        super().__init__()

        self.TYPE_LIST = type([])
        self.TYPE_STR = type('')
        self.TYPE_BYTES = type(b'')

        self.commands = {
            '/divider': self.divider_COMMAND,
            '/rollfor': self.roll_for_COMMAND
        }

    def to_bytes(self, value) -> bytes:
        """
        takes in an object which may be either a :class:`str` or :class:`bytes`, and returns a :class:`bytes`

        :param value: either a str or a bytes object
        :return: a bytes object
        """
        return value if type(value) == self.TYPE_BYTES else value.encode('UTF-8')

    def to_str(self, value) -> str:
        """
        takes in an object which may be either a :class:`str` or :class:`bytes`, and returns a :class:`str`

        :param value: either a str or a bytes object
        :return: a str object
        """
        return value if type(value) == self.TYPE_STR else str(value, encoding='UTF-8')

    def unwrap_list(self, value):
        """
        If the passed value is a list and contains at least one element, return the first element.
        Otherwise, return the passed value.

        :param value: Any object
        :return: The first element of the list, if the passed object is a list with at least one element, otherwise the
        object
        """
        return value[0] if type(value) == self.TYPE_LIST and len(value) > 0 else value

    def read_required_parameter(self, name: str, request: Request) -> bytes:
        """
        Reads a parameter with the given name from the request,
        raising a :class:`MissingParameterException` if it's absent.

        :param name: Name of the parameter
        :param request: The incoming request
        :return: The value of the parameter
        :raises MissingParameterException: if there is no parameter with the given name
        """
        name_bytes = self.to_bytes(name)

        if name_bytes in request.args.keys():
            return request.args[name_bytes]

        raise MissingParameterException(name)

    def read_required_string_parameter(self, name: str, request: Request) -> str:
        """
        Reads a parameter from the given request, and returns it as a :class:`str`.

        Raises a :class:`MissingParameterException` if there is no parameter with the given name.

        :param name: The name of the parameter
        :param request: The incoming request
        :return: The str value of the parameter
        :raises MissingParameterException: if there is no parameter with the given name
        """
        return self.to_str(self.unwrap_list(self.read_required_parameter(name, request)))

    # noinspection PyPep8Naming,PyUnusedLocal
    @staticmethod
    def divider_COMMAND(request: Request) -> map:
        return {
            'blocks': [
                {
                    "type": "divider"
                }
            ],
            "response_type": "in_channel"
        }

    # noinspection PyPep8Naming
    def roll_for_COMMAND(self, request: Request) -> map:
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

    # noinspection PyMethodMayBeStatic,PyPep8Naming,PyUnusedLocal
    def render_GET(self, request: Request) -> bytes:
        return self.to_bytes('<html><body>Slack bot is running.</body></html>')

    # noinspection PyPep8Naming
    def render_POST(self, request: Request) -> bytes:
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
    dnd_webhook = Resource()
    dnd_webhook.putChild(b'dnd', SlackDndSlashCommandWebhook())

    root = Resource()
    root.putChild(b'webhook', dnd_webhook)

    reactor.listenTCP(8080, Site(root))
    reactor.run()
