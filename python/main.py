#!/usr/bin/env python
import json
import sys
from twisted.web.server import Site
from twisted.web.resource import Resource
from twisted.internet import reactor

NAME = 'xanathar'
LIST_TYPE = type([])

class Relay(Resource):

    def __init__(self):
        self.commands = {}
        self.commands['/divider'] = self.divider
        self.commands['/rollfor'] = self.roll_for

    def divider(self, request):
        response = {
            'blocks': [{"type": "divider"}],
            "response_type": "in_channel"
        }
        return json.dumps(response)

    def roll_for(self, request):
        t = request.args['text']

        if type(t) == LIST_TYPE and len(t) > 0:
            t = str(t[0])

        if len(t) == 0:
            t = 'initiative'
        else:
            t = str(t)

        t = t.replace('*', '')
        t = t.replace('_', '')
        t = t.replace('~', '')

        response = {
            'blocks': [
                {
                    "type": "divider"
                },
                {
                    "type": "section",
                    "text": {
                        "type": "mrkdwn",
                        "text": "*Roll for {}*".format(t)
                    }
                }
            ],
            "response_type": "in_channel"
        }
        return json.dumps(response)

    def render_GET(self, request):
        return '<html><body>{} is running.</body></html>'.format(NAME)

    def render_POST(self, request):
        command = request.args['command']

        if type(command) == LIST_TYPE:
            command = command[0]

        if command in self.commands:
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
