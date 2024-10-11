from flask import Flask, request, jsonify
import requests
import time
import os
import json

app = Flask(__name__)

modsecurity_log_file = "/var/log/modsecurity/audit.log"

from urllib.parse import urlparse, urlencode

class RequestModel:
    def __init__(self, url, method, requestHeaders, requestBody, responseHeaders, responseBody):
        self.url = url
        self.method = method
        self.requestHeaders = requestHeaders
        self.requestBody = requestBody
        self.responseHeaders = responseHeaders
        self.responseBody = responseBody

import json

@app.route('/', methods=['POST'])
def forward_request():
    data = request.get_json()

    model = RequestModel(
        url=data.get('url', ''),
        method=data.get('method', '').upper(),
        requestHeaders=data.get('requestHeaders', {}),
        requestBody=data.get('requestBody', {}),
        responseHeaders=data.get('responseHeaders', {}),
        responseBody=data.get('responseBody', {})
    )

    parsed_url = urlparse(model.url)
    path = parsed_url.path
    query = parsed_url.query

    if query:
        full_path = f"{path}?{query}"
    else:
        full_path = path

    full_url = f"http://127.0.0.1:82/{full_path}"

    unique_id = str(int(time.time() * 1000))
    model.requestHeaders['X-Request-Random'] = unique_id
 
    post_url = "http://127.0.0.1:8080/response"
    post_data = {
        'responseHeaders': model.responseHeaders,
        'responseBody': model.responseBody
    }
    post_response = requests.post(post_url, headers={'X-Request-Random': unique_id}, json=post_data)

    if post_response.status_code != 200:
        return jsonify({'error': 'Failed to forward to 8080'}), 500

    if model.method == 'GET':
        response = requests.get(full_url, headers=model.requestHeaders, params=model.requestBody)
    elif model.method == 'POST':
        response = requests.post(full_url, headers=model.requestHeaders, json=model.requestBody)
    elif model.method == 'PUT':
        response = requests.put(full_url, headers=model.requestHeaders, json=model.requestBody)
    elif model.method == 'DELETE':
        response = requests.delete(full_url, headers=model.requestHeaders, json=model.requestBody)
    else:
        return jsonify({'error': 'Unsupported method'}), 400


    time.sleep(0.05)
    log_path = "/var/log/modsecurity/audit.log"
    if os.path.exists(log_path):
        with open(log_path, 'r') as log_file:
            logs = log_file.read()
        if unique_id in logs:
                relevant_logs = extract_modsecurity_logs(logs, unique_id)
                return jsonify({
                    'result': json.loads(relevant_logs)
                }), response.status_code
    return jsonify({
    }), response.status_code

def extract_modsecurity_logs(log_content, unique_id):
    relevant_logs = []
    logs = log_content.split('\n')
    inside_relevant_block = False
    for line in logs:
        if unique_id in line:
            inside_relevant_block = True
        if inside_relevant_block:
            relevant_logs.append(line)
        if inside_relevant_block and 'end of audit log' in line.lower():
            break
    return '\n'.join(relevant_logs)

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5000)

