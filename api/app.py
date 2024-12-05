from flask import Flask
import os
import socket

from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)

@app.route("/")
def hello():
    html = """Hello {name}!
    Hostname: {hostname}"""
    return html.format(name=os.getenv("NAME", "world"), hostname=socket.gethostname())

if __name__ == "__main__":
    print("Starting app...")
    app.run(host='0.0.0.0', port=5000)