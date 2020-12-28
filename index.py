import sys
sys.path.append('lib')

import requests
import os
import json
import datetime

def shaping_data(event):
    return {
        'en': event['en'],
        'ja': event['en'],
        'published': event['published'],
        'url': event['url'],
        'webhook': event['webhook']
    }

def translation(obj):
    try:
        response = requests.post(
            "https://api.deepl.com/v2/translate",
            data={
                "auth_key": os.environ['DEEPL_API_KEY'],
                "text": obj['en'],
                "target_lang": 'JA'
            }
        )
        print(response.status_code)
        result = response.json()
        obj['ja'] = result["translations"][0]["text"]
    except Exception as et:
        sys.stderr.write("*** error *** in Translation ***\n")
        sys.stderr.write(str(et) + "\n")
    else:
        return obj

def sendWebHook(obj):
    content = obj['en'] + '\n' + obj['ja'] + '\n' + obj['published'] + '\n' + obj['URL']
    try:
        print('shot webhook!')
        response = requests.post(
            obj['webhook'],
            json.dumps({"content": content}),
            headers={'Content-Type': 'application/json'}
        )
        print(response)
    except Exception as ew:
        sys.stderr.write("*** error *** in SendWebHook ***\n")
        sys.stderr.write(str(ew) + "\n")
    else:
        return response

def handler(event, context):
    obj = shaping_data(event)
    translated = translation(obj)
    sendWebHook(translated)
    data = {
        'output': 'Hello World',
        'timestamp': datetime.datetime.utcnow().isoformat(),
        'content': translated['content']
    }
    return {'statusCode': 200,
            'body': json.dumps(data),
            'headers': {'Content-Type': 'application/json'}}
