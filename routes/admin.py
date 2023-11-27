# admin_routes.py
import re
from flask import Blueprint, render_template, request, jsonify, redirect, url_for
from models import Agent, Plugin, Task, Command, Argument, Response
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

@admin_blueprint.route('/view_agent/<string:agent_id>', methods=['GET'])
def view_agent(agent_id):
    # Fetch the agent details from the database
    # Replace the following line with your actual database query
    agent = Agent.query.get(agent_id)

    if agent is None:
        return render_template('error.html', error="Agent not found"), 404

    # Fetch tasks associated with the agent
    tasks = Task.query.filter_by(agent_id=agent.id).all()
    # Query all plugins
    all_plugins = Plugin.query.all()

    return render_template('admin_view_agent.html', agent=agent, tasks=tasks, all_plugins=all_plugins)

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
        new_plugin = Plugin(name=name, version=version, description=description, script=script, commands=commands)

        for i in range(len(request.form.getlist('commands[]'))):
            command_name = request.form.getlist('commands[]')[i]
            command_description = request.form.getlist('descriptions[]')[i]
            command_function = request.form.getlist('functions[]')[i]
            
            command = Command(name=command_name, description=command_description, function=command_function, plugin_id=new_plugin.id)
            db.session.add(command)
            
            # Extracting arguments for each command
            argument_keys = request.form.getlist(f'arguments_keys[{i}][]')
            argument_types = request.form.getlist(f'arguments_types[{i}][]')

            # Creating and adding Argument instances to the Command
            for key, arg_type in zip(argument_keys, argument_types):
                if key is not None and key != "":
                    argument = Argument(key=key, key_type=arg_type, command_id=command.id)
                    command.arguments.append(argument)
                    db.session.add(argument)

            commands.append(command)

        

        # Add commands and arguments to the session
        db.session.add(new_plugin)              
        db.session.commit()

        return redirect(url_for('admin.list_plugins'))

    return render_template('admin_create_plugin.html')

def extract_command_ids(input_list):
    command_ids = []

    for input_str in input_list:
        match = re.match(r"commands\[([a-f0-9]+)\]", input_str)
        if match:
            command_ids.append(match.group(1))

    return command_ids

@admin_blueprint.route('/edit_plugin/<string:plugin_id>', methods=['GET', 'POST'])
def edit_plugin(plugin_id):
    plugin = Plugin.query.get(plugin_id)

    if request.method == 'POST':
        plugin.name = request.form.get('name')
        plugin.version = request.form.get('version')
        plugin.description = request.form.get('description')
        plugin.script = request.form.get('script')

        # Create new Commands & Arguments
        for i in range(len(request.form.getlist('commands[]'))):
            command_name = request.form.getlist('commands[]')[i]
            command_description = request.form.getlist('descriptions[]')[i]
            command_function = request.form.getlist('functions[]')[i]
            
            command = Command(name=command_name, description=command_description, function=command_function, plugin_id=plugin_id)
            db.session.add(command)
            
            # Extracting arguments for each command
            argument_keys = request.form.getlist(f'arguments_keys[{i}][]')
            argument_types = request.form.getlist(f'arguments_types[{i}][]')

            # Creating and adding Argument instances to the Command
            for key, arg_type in zip(argument_keys, argument_types):
                argument = Argument(key=key, key_type=arg_type, command_id=command.id)
                command.arguments.append(argument)
                db.session.add(argument)

        existing_command_ids = extract_command_ids([
            key for key in request.form.keys() if key.startswith('commands[')
        ])
        # Go though existing Commands
        for command_id in existing_command_ids:
            command_name = request.form.get(f'commands[{command_id}]')
            command_description = request.form.get(f'descriptions[{command_id}]')
            command_function = request.form.get(f'functions[{command_id}]')
            command = Command.query.get(command_id)
            command.name = command_name
            command.description = command_description
            command.function = command_function
            db.session.commit()

            # New Arguments
            # Extracting arguments for each command
            argument_keys = request.form.getlist(f'arguments_keys[{command_id}][]')
            argument_types = request.form.getlist(f'arguments_types[{command_id}][]')

            # Creating and adding Argument instances to the Command
            for key, arg_type in zip(argument_keys, argument_types):
                argument = Argument(key=key, key_type=arg_type, command_id=command_id)
                command.arguments.append(argument)
                db.session.add(argument)

            existing_argument_ids = extract_command_ids([
                key for key in request.form.keys() if key.startswith(f'arguments_keys[{command_id}][')
            ])
            for argument_id in existing_argument_ids:
                argument_key = request.form.get(f'arguments_keys[{command_id}][{argument_id}]')
                argument_type = request.form.get(f'arguments_types[{command_id}][{argument_id}]')
                argument = Argument.query.get(argument_id)
                argument.key = argument_key
                argument.key_type = argument_type
                db.session.commit()

        db.session.commit()

        return redirect(url_for('admin.view_plugin', plugin_id=plugin.id))

    return render_template('admin_edit_plugin.html', plugin=plugin)

@admin_blueprint.route('/plugins/<plugin_id>', methods=['GET'])
def view_plugin(plugin_id):
    # Fetch the plugin details from the database
    # Replace the following line with your actual database query
    plugin = Plugin.query.get(plugin_id)
    return render_template('admin_view_plugin.html', plugin=plugin)

@admin_blueprint.route('/assign_plugin/<string:agent_id>', methods=['POST'])
def assign_plugin(agent_id):
    agent = Agent.query.get(agent_id)

    if agent is None:
        return render_template('error.html', error="Agent not found"), 404

    plugin_id = request.form.get('plugin_id')
    plugin = Plugin.query.get(plugin_id)

    if plugin is None:
        return render_template('error.html', error="Plugin not found"), 404

    agent.plugins.append(plugin)
    db.session.commit()

    return redirect(url_for('admin.view_agent', agent_id=agent_id))


@admin_blueprint.route('/create_task/<agent_id>', methods=['GET', 'POST'])
def create_task(agent_id):
    agent = Agent.query.get(agent_id)

    if agent is None:
        return render_template('error.html', error="Agent not found"), 404

    if request.method == 'POST':
        command_id = request.form.get('command_id')
        cron = request.form.get('cron')
        arguments = request.form.get('arguments')

        command = Command.query.get(command_id)

        if command is None:
            return render_template('error.html', error="Command not found"), 404

        # Create a new task
        new_task = Task(command=command.name, cron=cron, arguments=arguments, agent_id=agent.id)
        db.session.add(new_task)
        db.session.commit()

        return redirect(url_for('admin.view_agent', agent_id=agent.id))

    # Get the available commands based on the plugins assigned to the agent
    available_commands = []
    for plugin in agent.plugins:
        for command in plugin.commands:
            available_commands.append({
                'id': command.id,
                'name': command.name,
                'function': command.function
            })

    return render_template('admin_create_task.html', agent=agent, available_commands=available_commands)

@admin_blueprint.route('/get_command_arguments/<command_id>', methods=['GET'])
def get_command_arguments(command_id):
    command = Command.query.filter_by(id=command_id).first()

    # Fetch arguments for the specified command_id
    arguments = [
        {"id": arg.id, "key": arg.key, "key_type": arg.key_type}
        for arg in command.arguments
    ]

    # Return the arguments as a JSON response
    return jsonify({"arguments": arguments})

# Route for deleting a task
@admin_blueprint.route('/admin/delete_task/<task_id>', methods=['POST'])
def delete_task(task_id):
    # Get the task by ID
    task = Task.query.get(task_id)

    if task:
        agent_id = task.agent_id
        # Delete associated responses
        Response.query.filter_by(task_id=task.id).delete()

        # Delete the task
        db.session.delete(task)
        db.session.commit()

        # Redirect to the agent view page or any other appropriate page
        return redirect(url_for('admin.view_agent', agent_id=agent_id))

    # Task not found
    return render_template('error.html', error_message='Task not found')

# Route for deleting a command
@admin_blueprint.route('/admin/delete_command/<command_id>', methods=['GET'])
def delete_command(command_id):
    try:
        command = Command.query.get(command_id)
        if command:
            plugin_id = command.plugin_id
            db.session.delete(command)
            db.session.commit()
            return redirect(url_for('admin.view_plugin', plugin_id=plugin_id))
        else:
            return render_template('error.html', error_message='Command not found')
    except Exception as e:
        return render_template('error.html', error_message=str(e))

