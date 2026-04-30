from flask import Flask, request, jsonify
from discord_webhook import DiscordWebhook
import os 

app = Flask(__name__)
Discord_Webhook = os.environ.get('Discord_Webhook')

@app.route('/log', methods=['POST'])
def receive_log():
    # print("receive")
    if request.is_json:
        
        data = request.get_json()
        command = data.get('command')
        hostname = data.get('hostname') #don't leave hard coded 
        username = data.get('username')
        webhook = DiscordWebhook(url=Discord_Webhook,
                                 content=f"Command: {command}, Hostname: {hostname}, Username: {username}",
                                 rate_limit_retry=True
                                 )
        response = webhook.execute()
        print(response)
        print(f"Host {hostname} ran {command}")
        return f"Host {hostname} ran {command}"
        #Incorporate discord webhook