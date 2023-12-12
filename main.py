from app import app
from flask_cors import CORS

if __name__ == "__main__":
    CORS(
        app,
        resources={
            r"/searchaddr1": {"origins": "https://blog.bouldermon.com/"},
            r"/searchaddr2": {"origins": "https://blog.bouldermon.com/"},
        },
    )
    app.run(host="0.0.0.0", port="5050")
