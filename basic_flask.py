from flask import Flask, jsonify
import logging

# Configure logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

app = Flask(__name__)

@app.route('/')
def index():
    logger.debug("Root route accessed")
    return "Hello, World!"

@app.route('/test')
def test():
    logger.debug("Test route accessed")
    return jsonify({"status": "success", "message": "Test endpoint working"})

if __name__ == '__main__':
    logger.debug("Starting basic Flask app on port 5010")
    # Disable reloader and debugger to avoid potential issues
    app.run(host='127.0.0.1', port=5010, debug=False, use_reloader=False, threaded=True) 