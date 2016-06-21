import json
import logging
import os

import requests
from skygear.registry import get_registry

log = logging.getLogger(__name__)


class FacebookBot():
    def __init__(self, page_id, token):
        self.page_id = page_id
        self.token = token

    @property
    def thread_settings_url(self):
        url = "https://graph.facebook.com/v2.6/{page_id}/thread_settings"
        return url.format(page_id=self.page_id)

    def call_to_actions(self, message):
        r = requests.post(
            self.thread_settings_url,
            params={
                'access_token': self.token
            },
            json={
                "call_to_actions": [{
                    "message": {
                        "attachment": {
                            "payload": {
                                "template_type": "generic",
                                "elements": [message]
                            },
                            "type": "template"
                        }
                    }
                }],
                "setting_type": "call_to_actions",
                "thread_state": "new_thread"
            }
        )
        log.debug(r.json())


class FBRegistry:
    def __init__(self, path, skygear_registry=get_registry()):
        self.fb_verify = os.getenv('FB_VERIFY')
        self.root = {}
        self.postback = {}
        self.skygear_registry = skygear_registry
        self.skygear_registry.register(
            'handler', path, self.verify, method=['GET'])
        self.skygear_registry.register(
            'handler', path, self.handler, method=['POST'])

    def register(self, func, recipient_id, postback):
        if postback is not None:
            if recipient_id not in self.postback:
                self.postback[recipient_id] = {}
            self.postback[recipient_id][postback] = func
        else:
            self.root[recipient_id] = func

    def get_postback_func(self, recipient_id, postback):
        if recipient_id in self.postback:
            if postback in self.postback[recipient_id]:
                return self.postback[recipient_id][postback]
        if postback in self.postback['*']:
            return self.postback['*'][postback]
        return None
        
    def verify(self, request):
        verify_token = request.values.get('hub.verify_token')
        log.debug('Get facebook verify request', verify_token)
        if verify_token == self.fb_verify:
            return request.values.get('hub.challenge')
        else:
            return 'You are not facebook'

    def handler(self, request):
        log.debug('Got message from facebook')
        body = request.get_data(as_text=True)
        payload = json.loads(body)
        log.debug(payload)
        events = payload['entry'][0]['messaging']
        for evt in events:
            # Most specific match come first
            recipient_id = evt['recipient']['id']
            if 'postback' in evt:
                postback = evt['postback']['payload']
                func = self.get_postback_func(recipient_id, postback)
                if func is not None:
                    func(evt)
            if recipient_id in self.root:
                return self.root[recipient_id](evt)
            else:
                return self.root['*'](evt)


class FBPostman:
    def __init__(self, token):
        self.token = token

    def _send(self, sender, payload):
        log.debug(payload)
        return requests.post(
            'https://graph.facebook.com/v2.6/me/messages',
            params={
                'access_token': self.token 
            },
            json={
                'recipient': {
                    'id': sender
                },
                'message': payload
            }
        )

    def send(self, sender, payload):
        log.debug(payload.__class__.__name__)
        if payload.__class__.__name__ == 'str':
            log.debug('sending text message')
            return self.message(sender, payload)
        else:
            evenlop = {
                'attachment': {
                    'type': 'template',
                    'payload': payload
                }
            }
            return self._send(sender, evenlop)

    def message(self, sender, message):
        payload = {
            'text': message
        }
        return self._send(sender, payload)

_fb_registry = {}


def messager_handler(path, recipient_id='*', postback=None, token=None):
    if path not in _fb_registry:
        _fb_registry[path] = FBRegistry(path)
    registery = _fb_registry[path]
    def handler(func):
        _func = with_postman(func, token)
        registery.register(
            _func,
            recipient_id,
            postback
        )
        log.debug('Registered message handler %s, %s, %s',
              path, recipient_id, postback)
        return func
    return handler


def with_postman(func, token):
    if token is None:
        token = os.getenv('FB_TOKEN')
    postman = FBPostman(token)
    def wrapper(evt):
        return func(evt, postman)
    return wrapper
