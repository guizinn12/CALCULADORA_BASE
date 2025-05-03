import os
import json
from flask import Flask, render_template, jsonify

# Create the Flask application
app = Flask(__name__)
app.secret_key = os.environ.get("SESSION_SECRET", "dev-secret-key")

# Load crimes data
def load_crimes_data():
    with open('static/data/crimes.json', 'r', encoding='utf-8') as file:
        return json.load(file)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/crimes')
def get_crimes():
    try:
        crimes = load_crimes_data()
        return jsonify(crimes)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
