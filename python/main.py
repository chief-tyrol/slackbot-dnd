#!/usr/bin/env python
import json
import sys
from twisted.web.server import Site
from twisted.web.resource import Resource
from twisted.internet import reactor

import requests

NAME = 'xanathar'
LIST_TYPE = type([])

class Relay(Resource):

    def __init__(self):
        self.commands = {}
        self.commands['/divider'] = self.divider
        self.commands['/rollfor'] = self.roll_for

    def list_to_value(self, value):
        if type(value) == LIST_TYPE and len(value) > 0:
            return value[0]
        return value

    def divider(self, request):
        response = {
            'blocks': [{"type": "divider"}],
            "response_type": "in_channel"
        }
        return json.dumps(response)

    def roll_for(self, request):
        t = str(self.list_to_value(request.args['text']))

        if len(t) == 0:
            t = 'initiative'
        else:
            t = str(t)

        t = t.replace('*', '')
        t = t.replace('_', '')
        t = t.replace('~', '')

        response_url = str(self.list_to_value(request.args['response_url']))
        user_id = str(self.list_to_value(request.args['user_id']))

        response = {
            'blocks': [
                {
                    "type": "divider"
                },
                {
                    "type": "section",
                    "text": {
                        "type": "mrkdwn",
                        "text": "<@{}> says *\"roll for {}!\"* :game_die::game_die::game_die:".format(user_id, t)
                    }
                }
            ],
            "response_type": "in_channel"
        }

        requests.post(response_url, data=json.dumps(response), headers={'content-type': 'application/json'}, timeout=60)

        return ''

    def render_GET(self, request):
        return '<html><body>{} is running.</body></html>'.format(NAME)

    def render_POST(self, request):
        command = request.args['command']

        if type(command) == LIST_TYPE:
            command = command[0]

        if command in self.commands:
            request.setResponseCode(200)
            request.responseHeaders.addRawHeader('Content-Type', 'application/json')
            return self.commands[command](request)
        
        request.setResponseCode(404)
        return '<html><body>Command "{}" not recognized</body></html>'.format(command)

if __name__ == '__main__':
    cogsworth = Resource()
    cogsworth.putChild(NAME, Relay())

    root = Resource()
    root.putChild('webhook', cogsworth)

    reactor.listenTCP(8080, Site(root))
    reactor.run()
