# admin_routes.py
from flask import Blueprint, render_template, request, jsonify, redirect, url_for
from models import Agent, Plugin, Task, Command, Argument
from database import db

admin_blueprint = Blueprint('admin', __name__, url_prefix='/admin')

@admin_blueprint.route('/')
def dashboard():
    agents_count = Agent.query.count()
    plugins_count = Plugin.query.count()
    tasks_count = Task.query.count()

    return render_template('admin_dashboard.html', agents_count=agents_count, plugins_count=plugins_count, tasks_count=tasks_count)

@admin_blueprint.route('/agents', methods=['GET'])
def list_agents():
    agents = Agent.query.all()
    return render_template('admin_agents.html', agents=agents)

@admin_blueprint.route('/agent_details/<agent_id>')
def agent_details(agent_id):
    agent = Agent.query.get(agent_id)

    if agent is None:
        return render_template('error.html', error="Agent not found"), 404

    return render_template('agent_details.html', agent=agent)

@admin_blueprint.route('/edit_agent/<agent_id>', methods=['POST'])
def edit_agent(agent_id):
    agent = Agent.query.get(agent_id)

    if agent is None:
        return render_template('error.html', error="Agent not found"), 404

    new_name = request.form.get('new_name')
    agent.name = new_name
    agent.save()  # Assuming you have a `save` method in your `Agent` model

    return redirect(url_for('admin.list_agents'))

@admin_blueprint.route('/plugins', methods=['GET'])
def list_plugins():
    plugins = Plugin.query.all()
    return render_template('admin_plugins.html', plugins=plugins)

@admin_blueprint.route('/tasks/<agent_id>', methods=['GET'])
def list_tasks(agent_id):
    agent = Agent.query.get(agent_id)

    if agent is None:
        return render_template('error.html', error="Agent not found"), 404

    tasks = Task.query.filter_by(agent_id=agent.id).all()
    return render_template('admin_tasks.html', agent=agent, tasks=tasks)

@admin_blueprint.route('/results/<agent_id>', methods=['GET'])
def list_task_results(agent_id):
    agent = Agent.query.get(agent_id)

    if agent is None:
        return render_template('error.html', error="Agent not found"), 404

    tasks = Task.query.filter_by(agent_id=agent.id).all()
    results = [task.result for task in tasks if task.result is not None]
    return render_template('admin_results.html', agent=agent, results=results)

@admin_blueprint.route('/create_plugin', methods=['GET', 'POST'])
def create_plugin():
    if request.method == 'POST':
        name = request.form.get('name')
        version = request.form.get('version')
        description = request.form.get('description')
        script = request.form.get('script')

        # Extracting commands from the form
        commands = []
        command_names = request.form.getlist('command_name')
        command_descriptions = request.form.getlist('command_description')
        command_functions = request.form.getlist('command_function')

        for name, description, function in zip(command_names, command_descriptions, command_functions):
            command = Command(name=name, description=description, function=function)

            # Extracting arguments for each command
            argument_keys = request.form.getlist(f'{name}_argument_key')
            argument_types = request.form.getlist(f'{name}_argument_type')

            # Creating and adding Argument instances to the Command
            for key, arg_type in zip(argument_keys, argument_types):
                argument = Argument(key=key, key_type=arg_type)
                command.arguments.append(argument)

            commands.append(command)

        new_plugin = Plugin(name=name, version=version, description=description, script=script, commands=commands)

        db.session.add(new_plugin)
        db.session.commit()

        return redirect(url_for('admin.list_plugins'))

    return render_template('admin_create_plugin.html')


@admin_blueprint.route('/plugins/<plugin_id>', methods=['GET'])
def view_plugin(plugin_id):
    # Fetch the plugin details from the database
    # Replace the following line with your actual database query
    plugin = Plugin.query.get(plugin_id)
    return render_template('admin_view_plugin.html', plugin=plugin)