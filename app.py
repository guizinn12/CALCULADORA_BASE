import os
import json
from flask import Flask, render_template, jsonify, request, redirect, url_for

# Create the Flask application
app = Flask(__name__)
app.secret_key = os.environ.get("SESSION_SECRET", "dev-secret-key")

# Load crimes data
def load_crimes_data():
    with open('static/data/crimes.json', 'r', encoding='utf-8') as file:
        return json.load(file)

# Load config data
def load_config_data():
    with open('static/data/config.json', 'r', encoding='utf-8') as file:
        return json.load(file)

# Save config data
def save_config_data(config):
    with open('static/data/config.json', 'w', encoding='utf-8') as file:
        json.dump(config, file, indent=2)

@app.route('/')
def index():
    config = load_config_data()
    return render_template('index.html', config=config)

@app.route('/crimes')
def get_crimes():
    try:
        crimes = load_crimes_data()
        return jsonify(crimes)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/config')
def get_config():
    try:
        config = load_config_data()
        return jsonify(config)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/admin')
def admin():
    config = load_config_data()
    return render_template('admin.html', config=config)

@app.route('/update_config', methods=['POST'])
def update_config():
    try:
        data = request.form
        config = load_config_data()
        
        # Update city settings
        config['city']['name'] = data.get('city_name', config['city']['name'])
        config['city']['logo'] = data.get('city_logo', config['city']['logo'])
        config['city']['description'] = data.get('city_description', config['city']['description'])
        
        # Update theme colors
        config['theme']['primary_color'] = data.get('primary_color', config['theme']['primary_color'])
        config['theme']['secondary_color'] = data.get('secondary_color', config['theme']['secondary_color'])
        config['theme']['accent_color'] = data.get('accent_color', config['theme']['accent_color'])
        config['theme']['warning_color'] = data.get('warning_color', config['theme']['warning_color'])
        config['theme']['success_color'] = data.get('success_color', config['theme']['success_color'])
        config['theme']['danger_color'] = data.get('danger_color', config['theme']['danger_color'])
        
        # Update server info
        config['server']['name'] = data.get('server_name', config['server']['name'])
        config['server']['discord_url'] = data.get('discord_url', config['server']['discord_url'])
        config['server']['website_url'] = data.get('website_url', config['server']['website_url'])
        config['server']['instagram_url'] = data.get('instagram_url', config['server']['instagram_url'])
        
        # Save updated config
        save_config_data(config)
        
        return redirect(url_for('admin', success=True))
    except Exception as e:
        return redirect(url_for('admin', error=str(e)))

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
