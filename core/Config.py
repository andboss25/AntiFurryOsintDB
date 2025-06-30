import json

def GetConfig():
    return json.loads(open("config.json").read())