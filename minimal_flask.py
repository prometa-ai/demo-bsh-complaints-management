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
    logger.debug("Starting minimal Flask app on port 5008")
    app.run(debug=True, port=5008, threaded=False) 