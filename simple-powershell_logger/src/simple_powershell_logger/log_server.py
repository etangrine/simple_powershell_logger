from flask import Flask, request, jsonify

app = Flask(__name__)

app.route('/log', methods=['POST'])
def receive_log():

    if request.is_json():
        data = request.get_json()
        command = data.get('command')
        hostname = data.get('hostname')
        print(f"Host {hostname} rand {command}")
        #Incorporate discord webhook