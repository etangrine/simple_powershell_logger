from flask import Flask, request, jsonify

app = Flask(__name__)

@app.route('/log', methods=['POST'])
def receive_log():
    # print("receive")
    if request.is_json:
        data = request.get_json()
        command = data.get('command')
        hostname = data.get('hostname')
        print(f"Host {hostname} ran {command}")
        return f"Host {hostname} ran {command}"
        #Incorporate discord webhook