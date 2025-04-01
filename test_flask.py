from flask import Flask

app = Flask(__name__)

@app.route('/')
def index():
    return 'Flask is working!'

@app.route('/test')
def test():
    return 'This is a test route'

if __name__ == '__main__':
    print("Starting test Flask app...")
    app.run(debug=True, port=5003) 