from flask import Flask, jsonify
import datetime

app = Flask(__name__)

@app.route("/")
def home():
    return """
    <html>
    <head><title>My Cloud App</title></head>
    <body style="font-family: sans-serif; text-align: center; padding: 50px;">
        <h1>🚀 Deployed via LangGraph!</h1>
        <p>This app was automatically deployed to AWS EC2.</p>
        <p>Try <a href="/api/status">/api/status</a></p>
    </body>
    </html>
    """

@app.route("/api/status")
def status():
    return jsonify({
        "status": "running",
        "message": "Auto-deployed via LangGraph + GitHub webhook",
        "time": datetime.datetime.utcnow().isoformat()
    })

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
