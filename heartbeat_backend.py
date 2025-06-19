from flask import Flask, jsonify
from flask_cors import CORS
from datetime import datetime
import time

app = Flask(__name__)
# Enable CORS for all routes
CORS(app)

# Store server start time
server_start_time = time.time()

@app.route('/heartbeat', methods=['GET'])
def heartbeat():
    """
    Simple heartbeat endpoint that returns server status
    """
    current_time = datetime.now().isoformat()
    uptime_seconds = int(time.time() - server_start_time)
    
    return jsonify({
        'status': 'alive',
        'timestamp': current_time,
        'uptime_seconds': uptime_seconds,
        'message': 'Server is running'
    }), 200

@app.route('/health', methods=['GET'])
def health_check():
    """
    More detailed health check endpoint
    """
    try:
        # You can add more health checks here
        # e.g., database connection, external service checks
        
        return jsonify({
            'status': 'healthy',
            'timestamp': datetime.now().isoformat(),
            'uptime_seconds': int(time.time() - server_start_time),
            'services': {
                'database': 'connected',  # Add actual DB check here
                'cache': 'connected'      # Add actual cache check here
            }
        }), 200
    except Exception as e:
        return jsonify({
            'status': 'unhealthy',
            'error': str(e),
            'timestamp': datetime.now().isoformat()
        }), 503

@app.route('/', methods=['GET'])
def home():
    return jsonify({'message': 'Backend server is running'}), 200

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)