from flask import Flask, render_template, request, redirect, url_for, session, flash
import sqlite3
import networkx as nx

app = Flask(__name__)
app.secret_key = 'your_secret_key'  # Change this to a random string

# Database Initialization for Student DB
def init_db():
    conn = sqlite3.connect('database.db')
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS users 
                 (id INTEGER PRIMARY KEY, name TEXT, role TEXT, email TEXT, password TEXT)''')
    c.execute('''CREATE TABLE IF NOT EXISTS messages 
                 (id INTEGER PRIMARY KEY, sender_id INTEGER, receiver_id INTEGER, message TEXT)''')
    conn.commit()
    conn.close()

# Kruskal's AI Suggestion
def suggest_connections():
    G = nx.Graph()
    conn = sqlite3.connect('database.db')
    c = conn.cursor()
    users = c.execute("SELECT id, name FROM users").fetchall()
    messages = c.execute("SELECT sender_id, receiver_id FROM messages").fetchall()
    for user in users:
        G.add_node(user[0], name=user[1])
    for msg in messages:
        G.add_edge(msg[0], msg[1], weight=1)
    mst = nx.minimum_spanning_tree(G)
    return list(mst.edges())

@app.route('/dashboard', methods=['GET', 'POST'])
def dashboard():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    conn = sqlite3.connect('database.db')
    c = conn.cursor()
    if request.method == 'POST':
        sender_id = session['user_id']
        receiver_id = int(request.form['receiver_id'])
        message = request.form['message']
        c.execute("INSERT INTO messages (sender_id, receiver_id, message) VALUES (?, ?, ?)", 
                  (sender_id, receiver_id, message))
        conn.commit()
    users = c.execute("SELECT * FROM users").fetchall()
    messages = c.execute("SELECT * FROM messages").fetchall()
    suggestions = suggest_connections()
    conn.close()
    return render_template('dashboard.html', users=users, messages=messages, suggestions=suggestions)