import json

'''
You need a "keys.json" file like this:
{
    "youtube": "Your Google API key",
    "discord": "Your Discord token"
}
...and Google secret file named "secret.json" 
'''

data = {}
with open('DISK:\\Way_to_keys\\\\keys.json') as file:
    data = json.load(file)
    

CONFIG = {
    'token': data["discord"], 
    'prefix': '.'
}

YDL_CONFIG = {
    'format': 'bestaudio/best', 
    'noplaylist':'True'
}

FFMPEG_CONFIG = {
    'options': '-vn'
}

YOUTUBE_CONFIG = {
    'api_key': data["youtube"] 
}