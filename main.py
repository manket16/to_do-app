

from flask import Flask, render_template, request, redirect,  session, jsonify
import json
import argon2

app = Flask(__name__)

# # Replace the following values with your MongoDB Atlas connection details
# MONGO_URI = "mongodb+srv://kumarmanket135:<password>@cluster0.y6fxwcj.mongodb.net/?retryWrites=true&w=majority"
# client = MongoClient(MONGO_URI)
# db = client.your_database_name


app.secret_key = 'dsjklerjk49ejsklfjd'


@app.route('/')
def index():
    return render_template('login.html')

@app.route('/index')
def home():
    return render_template('index.html')

@app.route('/signup_page')
def signup_page():
    return render_template('signup.html')


def write_to_json(data):
    with open('user_info.json', 'w') as file:
        json.dump(data, file)

def read_from_json():
    try:
        with open('user_info.json', 'r') as file:
            data = json.load(file)
    except FileNotFoundError:
        data = {}
    return data

@app.route('/signup', methods=['POST'])
def signup():
    data = read_from_json()
    username = request.form['username']
    password = request.form['password']
    name = request.form['name']
    dob = request.form['dob']

    if username in data:
        return "Username already exists"

    hasher = argon2.PasswordHasher()
    hashed_password = hasher.hash(password)

    data[username] = {
        "password": hashed_password,
        "name": name,
        "dob": dob
    }

    write_to_json(data)
    return redirect('/')

@app.route('/login', methods=['POST'])
def login():
    data = read_from_json()
    username = request.form['username']
    password = request.form['password']

    if username in data:
        stored_hashed_password = data[username]['password']
        hasher = argon2.PasswordHasher()
        try:
            hasher.verify(stored_hashed_password, password)
            session['username'] = username
            return render_template('index.html')
        except argon2.exceptions.VerifyMismatchError:
            return "Invalid password"
    else:
        return "Invalid user"




@app.route('/show_tasks')
def show_tasks():
    username = session.get('username')
    data = read_from_json()

    if username in data and 'tasks' in data[username]:
        user_tasks = data[username]['tasks']
    else:
        user_tasks = []

    return render_template('show_tasks.html', user_tasks=user_tasks)



@app.route('/remove', methods=['POST'])
def remove_task():
    # Retrieve 'username' from the session
    username = session.get('username')

    # Retrieve 'task' from the form data
    task_to_remove = request.form.get('task')

    if username and task_to_remove:
        user_data = read_from_json()

        if username in user_data and task_to_remove in user_data[username]['tasks']:
                user_data[username]['tasks'].remove(task_to_remove)
                write_to_json(user_data)

                # Pass the updated tasks to the template
                user_tasks = user_data[username]['tasks']  # or user_tasks = user_data.get(username, {}).get('tasks', [])

                return render_template('show_tasks.html', user_tasks=user_tasks)

    return jsonify({"error": "Task removal failed"}), 400



@app.route('/add_task', methods=['POST'])
def add_task():
    # Retrieve 'username' from the session
    username = session.get('username')

    # Retrieve 'task' from the form data
    task = request.form.get('task')

    if username and task:
        data = read_from_json()
        if username in data:
            if 'tasks' not in data[username]:
                # Create 'tasks' key and initialize it with a list
                data[username]['tasks'] = [task]
            else:
                # Append the new task to the existing list
                data[username]['tasks'].append(task)
            write_to_json(data)

    return render_template('index.html')









app.run(host='0.0.0.0', port=8080)
