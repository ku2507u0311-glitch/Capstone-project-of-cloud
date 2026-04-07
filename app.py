from flask import Flask, request, jsonify
from flask_cors import CORS
import sqlite3

app = Flask(__name__)
CORS(app)

def init_db():
    conn = sqlite3.connect('events.db')
    c = conn.cursor()
    c.execute('CREATE TABLE IF NOT EXISTS registrations (id INTEGER PRIMARY KEY AUTOINCREMENT, name TEXT, event TEXT)')
    c.execute('CREATE TABLE IF NOT EXISTS events_list (id INTEGER PRIMARY KEY AUTOINCREMENT, event_name TEXT UNIQUE)')
    
    c.execute('SELECT count(*) FROM events_list')
    if c.fetchone()[0] == 0:
        default_events = [('Tech Fest',), ('Cultural Event',), ('Workshop',)]
        c.executemany('INSERT INTO events_list (event_name) VALUES (?)', default_events)
    
    conn.commit()
    conn.close()

@app.route('/register', methods=['POST'])
def register():
    data = request.get_json()
    name = data.get('name')
    event = data.get('event')

    if not name or not event:
        return jsonify({"error": "Missing data"}), 400

    conn = sqlite3.connect('events.db')
    c = conn.cursor()
    c.execute('INSERT INTO registrations (name, event) VALUES (?, ?)', (name, event))
    conn.commit()
    conn.close()

    return jsonify({"message": "Registration successful!"}), 201

@app.route('/events', methods=['GET'])
def get_events():
    conn = sqlite3.connect('events.db')
    c = conn.cursor()
    c.execute('SELECT event_name FROM events_list')
    events = [row[0] for row in c.fetchall()]
    conn.close()
    return jsonify(events)

@app.route('/events', methods=['POST'])
def add_event():
    data = request.get_json()
    event_name = data.get('event_name')
    
    if not event_name:
        return jsonify({"error": "Event name is required"}), 400

    conn = sqlite3.connect('events.db')
    c = conn.cursor()
    try:
        c.execute('INSERT INTO events_list (event_name) VALUES (?)', (event_name,))
        conn.commit()
        return jsonify({"message": "Event added successfully!"}), 201
    except sqlite3.IntegrityError:
        return jsonify({"error": "Event already exists"}), 400
    finally:
        conn.close()

@app.route('/registrations', methods=['GET'])
def get_registrations():
    conn = sqlite3.connect('events.db')
    c = conn.cursor()
    c.execute('SELECT name, event FROM registrations')
    registrations = [{"name": row[0], "event": row[1]} for row in c.fetchall()]
    conn.close()
    return jsonify(registrations)

if __name__ == '__main__':
    init_db()
    app.run(debug=True, port=5000)
    db_config = {
    'host': 'localhost',
    'user': 'root',
    'password': '', # Leave this completely empty!
    'database': 'event_db'
}