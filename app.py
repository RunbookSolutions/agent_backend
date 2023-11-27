from flask import Flask, request, jsonify
from flask_cors import CORS  # Import CORS for allowing requests from any origin
from database import init_db
from routes.admin import admin_blueprint
from routes.agent import agent_blueprint

app = Flask(__name__)
CORS(app)  # Allow requests from any origin
app.config.from_pyfile('config.py')
init_db(app)

# Register the admin blueprint
app.register_blueprint(admin_blueprint)

# Register the admin blueprint
app.register_blueprint(agent_blueprint)

# Define your API routes and handlers here

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
