from flask import Flask, jsonify, request

app = Flask(__name__)

@app.get("/")
def home():
    return "Hello from Flask!"

@app.get("/health")
def health():
    return jsonify(status="ok")

@app.post("/echo")
def echo():
    data = request.get_json(silent=True) or {}
    return jsonify(received=data)

if __name__ == "__main__":
    # host="0.0.0.0" lets other devices on your network reach it
    app.run(host="0.0.0.0", port=5001, debug=True)
