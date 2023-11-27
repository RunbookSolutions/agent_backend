# admin_routes.py
from flask import Blueprint, request, jsonify
from models import Agent, Plugin, Task
from database import db
import uuid

agent_blueprint = Blueprint('agent', __name__, url_prefix='/api/agent')

@agent_blueprint.route('/', methods=['GET'])
def get_agent_info():
    ip_address = request.remote_addr

    # Check if the agent already exists in the database
    agent = Agent.query.filter_by(ip_address=ip_address).first()

    if agent is None:
        # If the agent doesn't exist, create a new agent
        agent = Agent(id=str(uuid.uuid4()), ip_address=ip_address)
        db.session.add(agent)
        db.session.commit()

    # Return the agent information in the specified JSON format
    return jsonify({
        "data": {
            "id": agent.id,
            "ip_address": agent.ip_address,
            "name": agent.name,
            "team_id": agent.team_id,
            "plugins": [plugin.id for plugin in agent.plugins]
        }
    })

@agent_blueprint.route('/plugin/<plugin_id>', methods=['GET'])
def get_plugin_info(plugin_id):
    ip_address = request.remote_addr

    # Get the agent by IP address
    agent = Agent.query.filter_by(ip_address=ip_address).first()

    if agent is None:
        return jsonify({"error": "Agent not found"}), 404

    # Get the plugin by ID
    plugin = Plugin.query.filter_by(id=plugin_id, agent_id=agent.id).first()

    if plugin is None:
        return jsonify({"error": "Plugin not found"}), 404

    # Format plugin information in the specified JSON format
    plugin_data = {
        "id": plugin.id,
        "name": plugin.name,
        "version": plugin.version,
        "description": plugin.description,
        "script": plugin.script,
        "hash": plugin.hash,
        "commands": {
            command.name: {
                "id": command.id,
                "name": command.name,
                "function": command.function
            }
            for command in plugin.commands
        }
    }

    return jsonify({"data": plugin_data})

@agent_blueprint.route('/tasks', methods=['GET'])
def get_agent_tasks():
    ip_address = request.remote_addr

    # Get the agent by IP address
    agent = Agent.query.filter_by(ip_address=ip_address).first()

    if agent is None:
        return jsonify({"error": "Agent not found"}), 404

    # Get tasks associated with the agent
    tasks = Task.query.filter_by(agent_id=agent.id).all()

    # Format tasks data in the specified JSON format
    tasks_data = [
        {
            "id": task.id,
            "command": task.command,
            "cron": task.cron,
            "arguments": task.arguments
        }
        for task in tasks
    ]

    return jsonify({"data": tasks_data})

@agent_blueprint.route('/task/<task_id>', methods=['POST'])
def post_task_result(task_id):
    ip_address = request.remote_addr

    # Get the agent by IP address
    agent = Agent.query.filter_by(ip_address=ip_address).first()

    if agent is None:
        return jsonify({"error": "Agent not found"}), 404

    # Get the task by ID
    task = Task.query.filter_by(id=task_id, agent_id=agent.id).first()

    if task is None:
        return jsonify({"error": "Task not found"}), 404

    # Get the task result data from the request payload
    result_data = request.json.get('data')

    # Update the task in the database with the result data
    task.result = result_data
    db.session.commit()

    return jsonify({"message": "Task result successfully received"})

