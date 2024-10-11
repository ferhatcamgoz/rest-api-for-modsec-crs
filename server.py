import logging
from flask import Flask, request, jsonify

app = Flask(__name__)

logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')

response_map = {}

@app.route('/response', methods=['POST'])
def store_response():
    data = request.get_json()
    
    unique_id = request.headers.get('X-Request-Random')

    
    if not unique_id:
        return jsonify({'error': 'X-Request-Random header missing'}), 400

    response_map[unique_id] = {
        'responseHeaders': data.get('responseHeaders', {}),
        'responseBody': data.get('responseBody', '')
    }

    
    return jsonify({'message': 'Response stored successfully'}), 200

@app.route('/<path:path>', methods=['GET', 'POST', 'PUT', 'DELETE'])
def handle_request(path):
    
    unique_id = request.headers.get('X-Request-Random')
    
    if not unique_id:
        return jsonify({'error': 'X-Request-Random header missing'}), 400
    elif unique_id not in response_map:
        return jsonify({'error': 'Unique ID not found in response map'}), 404

    stored_response = response_map[unique_id]
    
    stored_response_body = stored_response['responseBody']
    stored_response_header = stored_response['responseHeaders']

    if request.method == 'GET':
        return jsonify({
            'status': 'GET Request Successful',
            'responseHeaders': stored_response_header,
            'responseBody': stored_response_body
        }), 200

    elif request.method == 'POST':
        return jsonify({
            'status': 'POST Request Successful',
            'responseHeaders': stored_response_header,
            'responseBody': stored_response_body
        }), 200

    elif request.method == 'PUT':
        return jsonify({
            'status': 'PUT Request Successful',
            'responseHeaders': stored_response_header,
            'responseBody': stored_response_body
        }), 200

    elif request.method == 'DELETE':
        return jsonify({
            'status': 'DELETE Request Successful',
            'responseHeaders': stored_response_header,
            'responseBody': stored_response_body
        }), 200

    return jsonify({'error': 'Method not allowed'}), 405

@app.route('/', methods=['GET', 'POST', 'PUT', 'DELETE'])
def handle_root():
    return handle_request(path='')

if __name__ == '__main__':
    app.run(port=8080)
