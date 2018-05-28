import json
import logging
from collections import defaultdict
import requests
import time

GREEN = 63232
RED = 16187392


class DiscordWebHook:

    def __init__(self, url, author):
        self.url = url
        self.author = author

    def send_message(self, message):
        data = {}

        data['embeds'] = []
        embed = defaultdict(dict)

        embed['author']['name'] = self.author

        success_color = GREEN if message.success else RED

        embed['color'] = success_color
        embed['title'] = message.title
        embed['fields'] = []

        for name, values in message.fields.items():
            embed['fields'].append({'name': name, 'value': '\n'.join(values)})

        data['embeds'].append(dict(embed))

        empty = all(not d for d in data["embeds"])

        if empty and 'content' not in data:
            print('You cant post an empty payload.')
        if empty:
            data['embeds'] = []

        json_data = json.dumps(data, indent=4)

        headers = {'Content-Type': 'application/json'}

        response = requests.post(self.url, data=json_data, headers=headers)

        if response.status_code == 400:
            print("Post Failed, Error 400")
        else:
            print("Payload delivered successfuly")
            print("Code : "+str(response.status_code))
            time.sleep(2)
            return True
