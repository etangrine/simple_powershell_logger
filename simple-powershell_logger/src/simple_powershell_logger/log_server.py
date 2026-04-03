from flask import Flask, request, jsonify
from discord_webhook import DiscordWebhook

app = Flask(__name__)

@app.route('/log', methods=['POST'])
def receive_log():
    # print("receive")
    if request.is_json:
        
        data = request.get_json()
        command = data.get('command')
        hostname = data.get('hostname')
        webhook = DiscordWebhook(url="https://discord.com/api/webhooks/1489748337912582288/eHSWcC8UNwlBHCFY5ujSkE48TDOpPiEr2LjFd3_sKJd_A9D8t_cRwD8gbxfqJJ1VVLHQ",
                                 content=f"Command: {command}, Hostname: {hostname}",
                                 rate_limit_retry=True
                                 )
        response = webhook.execute()
        print(response)
        print(f"Host {hostname} ran {command}")
        return f"Host {hostname} ran {command}"
        #Incorporate discord webhook