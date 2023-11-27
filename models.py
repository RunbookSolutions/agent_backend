from database import db  # Import the db instance from database.py
import uuid

agent_plugin_association = db.Table(
    'agent_plugin_association',
    db.Column('agent_id', db.String, db.ForeignKey('agent.id')),
    db.Column('plugin_id', db.String, db.ForeignKey('plugin.id'))
)

class Argument(db.Model):
    id = db.Column(db.String, primary_key=True)
    key = db.Column(db.String)
    key_type = db.Column(db.String)
    command_id = db.Column(db.String, db.ForeignKey('command.id'), nullable=False)

    def __init__(self, key, key_type, command_id):
        self.id = uuid.uuid4().hex
        self.key = key
        self.key_type = key_type
        self.command_id = command_id

    def save(self):
        db.session.commit()

class Agent(db.Model):
    id = db.Column(db.String, primary_key=True)
    ip_address = db.Column(db.String)
    name = db.Column(db.String)
    team_id = db.Column(db.String)
    tasks = db.relationship('Task', backref='agent', lazy=True)  # Add this line
    plugins = db.relationship('Plugin', secondary=agent_plugin_association, backref='agents', lazy='dynamic')


    def save(self):
        db.session.commit()

class Plugin(db.Model):
    id = db.Column(db.String, primary_key=True)
    name = db.Column(db.String)
    version = db.Column(db.Integer)
    description = db.Column(db.String)
    script = db.Column(db.String)
    hash = db.Column(db.String)
    commands = db.relationship('Command', backref='plugin', lazy=True)

    def __init__(self, name, version, description, script, commands=None):
        self.id = uuid.uuid4().hex
        self.name = name
        self.version = version
        self.description = description
        self.script = script
        self.commands = commands if commands is not None else []

    def save(self):
        db.session.commit()

class Command(db.Model):
    id = db.Column(db.String, primary_key=True)
    name = db.Column(db.String)
    function = db.Column(db.String)
    plugin_id = db.Column(db.String, db.ForeignKey('plugin.id'), nullable=False)
    arguments = db.relationship('Argument', backref='command', lazy=True)

    def __init__(self, name, description, function, plugin_id, arguments=None):
        self.id = uuid.uuid4().hex
        self.name = name
        self.description = description
        self.function = function
        self.plugin_id = plugin_id
        self.arguments = arguments if arguments is not None else []

    def save(self):
        db.session.commit()

class Task(db.Model):
    id = db.Column(db.String, primary_key=True)
    command = db.Column(db.String)
    cron = db.Column(db.String)
    arguments = db.Column(db.String)
    agent_id = db.Column(db.String, db.ForeignKey('agent.id'), nullable=False)  # Update this line

    def save(self):
        db.session.commit()
