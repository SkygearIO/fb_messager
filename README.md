# Facebook messager adaptor

This code snippet intended to make bot writing easy in Skygear plugin

## Usage

__First__

Assumed you registered at `https://portal.skygear.io`

__Second__

Use git submodule to import the source code

```
git submodule add https://github.com/SkygearIO/fb_messager.git fb_messager
```

__Third__

In your cloud code, import the code. And register your first endpoint as
following:

``` python
from .fb_messager import messager_handler

@messager_handler('fbwebhook')
def echo(evt, postman):
    sender = evt['sender']['id']
    if 'message' in evt:
        msg = evt['message']
        if 'text' in msg:
            r = postman.send(sender, msg['text'])
    log.info('Cat cannot handle')
```

__Forth__

Go to the Facebook developer console, create a new app. Add `Messenger`
product to the App. You may follow the guide here:
https://developers.facebook.com/docs/messenger-platform/quickstart/

In other to verify the webhook endpoint, you need to config `FB_VERIFY`. Make it
the same with the verify token filled in
`https://developers.facebook.com/apps/<app_id>/webhooks/`. You can do it at
https://portal-staging.skygear.io/app/settings

The adaptor will replied facebook verification correctly. The Facebook
`Callback URL` will be `https://<your_app_name>.skygeario.com/fbwebhook`.

__Fifth__

To make a reply to converation works
You notice the `messager_handler` func will receive two parameters, `evt` and 
`psotman`. For the format of `evt` dict, you may refer to
https://developers.facebook.com/docs/messenger-platform/webhook-reference

You may look into the dict, decide what to do. Save an record, or just reply a
message. In the above message, it is just an echo. To make `postman` able to
post message to the conversation, you need to proivde `FB_TOKEN`. `FB_TOKEN` can
Acquire at `Token Generation` section located here:
https://developers.facebook.com/apps/<app_id>/messenger/
You may set the `FB_TOKEN` in https://portal-staging.skygear.io/app/settings

