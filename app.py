import os
import json
import re
import requests
import urllib.parse
from flask import Flask, render_template, jsonify, request, redirect, url_for, send_file, Response
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import DeclarativeBase
import io
import zipfile
from datetime import datetime

# Configuração do SQLAlchemy
class Base(DeclarativeBase):
    pass

# Create the Flask application and configure database
app = Flask(__name__)
app.secret_key = os.environ.get("SESSION_SECRET", "dev-secret-key")

# Configuração do banco de dados
app.config["SQLALCHEMY_DATABASE_URI"] = os.environ.get("DATABASE_URL")
app.config["SQLALCHEMY_ENGINE_OPTIONS"] = {
    "pool_recycle": 300,
    "pool_pre_ping": True,
}

# Inicializa o SQLAlchemy
db = SQLAlchemy(model_class=Base)
db.init_app(app)

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

# Importa os modelos após a inicialização do bd
with app.app_context():
    from models import City, CityConfig  # noqa: F401
    db.create_all()

# Novas rotas para gerenciar cidades e exportar HTML
@app.route('/cities')
def list_cities():
    cities = City.query.all()
    config = load_config_data()
    return render_template('cities.html', cities=cities, config=config)

@app.route('/city/add', methods=['GET', 'POST'])
def add_city():
    if request.method == 'POST':
        name = request.form.get('name')
        logo_url = request.form.get('logo_url')
        description = request.form.get('description')
        
        city = City(name=name, logo_url=logo_url, description=description)
        
        # Adiciona a configuração padrão
        config = CityConfig(
            server_name=request.form.get('server_name', 'FiveM RP Server'),
            discord_url=request.form.get('discord_url', '#'),
            website_url=request.form.get('website_url', '#'),
            instagram_url=request.form.get('instagram_url', '#'),
            primary_color=request.form.get('primary_color', '#1e3a8a'),
            secondary_color=request.form.get('secondary_color', '#172554'),
            accent_color=request.form.get('accent_color', '#3b82f6'),
            danger_color=request.form.get('danger_color', '#ef4444'),
            success_color=request.form.get('success_color', '#22c55e'),
            warning_color=request.form.get('warning_color', '#f59e0b')
        )
        
        city.configs.append(config)
        db.session.add(city)
        db.session.commit()
        
        return redirect(url_for('list_cities'))
    
    return render_template('city_form.html', city=None, config=load_config_data())

@app.route('/city/<int:city_id>/edit', methods=['GET', 'POST'])
def edit_city(city_id):
    city = City.query.get_or_404(city_id)
    
    if request.method == 'POST':
        city.name = request.form.get('name')
        city.logo_url = request.form.get('logo_url')
        city.description = request.form.get('description')
        
        # Atualiza a configuração
        if city.configs:
            config = city.configs[0]
        else:
            config = CityConfig(city_id=city.id)
            city.configs.append(config)
        
        config.server_name = request.form.get('server_name')
        config.discord_url = request.form.get('discord_url')
        config.website_url = request.form.get('website_url')
        config.instagram_url = request.form.get('instagram_url')
        config.primary_color = request.form.get('primary_color')
        config.secondary_color = request.form.get('secondary_color')
        config.accent_color = request.form.get('accent_color')
        config.danger_color = request.form.get('danger_color')
        config.success_color = request.form.get('success_color')
        config.warning_color = request.form.get('warning_color')
        
        db.session.commit()
        return redirect(url_for('list_cities'))
    
    # Se for GET, exibe o formulário de edição
    if city.configs:
        city_config = city.configs[0]
    else:
        city_config = CityConfig()  # Configuração vazia para evitar erros
    
    return render_template('city_form.html', city=city, city_config=city_config, config=load_config_data())

@app.route('/city/<int:city_id>/delete', methods=['POST'])
def delete_city(city_id):
    city = City.query.get_or_404(city_id)
    db.session.delete(city)
    db.session.commit()
    return redirect(url_for('list_cities'))

@app.route('/city/<int:city_id>/export')
def export_city_html(city_id):
    city = City.query.get_or_404(city_id)
    
    if not city.configs:
        return "Configuração da cidade não encontrada", 404
    
    city_config = city.configs[0]
    crimes_data = load_crimes_data()
    
    # Criar um pacote ZIP com todos os arquivos necessários
    memory_file = io.BytesIO()
    with zipfile.ZipFile(memory_file, 'w') as zf:
        # Index.html
        html_content = render_template('export/index.html', 
                                      city=city, 
                                      config=city_config.to_json(),
                                      crimes=crimes_data)
        zf.writestr('index.html', html_content)
        
        # Adicionar CSS
        css_content = ''
        with open('static/css/styles.css', 'r') as css_file:
            css_content = css_file.read()
        zf.writestr('css/styles.css', css_content)
        
        # Adicionar JavaScript
        js_content = ''
        with open('static/js/calculator.js', 'r') as js_file:
            js_content = js_file.read()
        zf.writestr('js/calculator.js', js_content)
        
        # Adicionar dados de crimes
        crimes_json = json.dumps(crimes_data, indent=2)
        zf.writestr('data/crimes.json', crimes_json)
        
        # Adicionar configuração
        config_json = json.dumps(city_config.to_json(), indent=2)
        zf.writestr('data/config.json', config_json)
        
        # Adicionar README com instruções
        readme = f"""# Calculadora Penal FiveM - {city.name}
        
Esta calculadora penal para FiveM foi exportada em {datetime.now().strftime('%d/%m/%Y %H:%M')}.

## Como usar

1. Extraia todos os arquivos deste ZIP para uma pasta
2. Abra o arquivo index.html em um navegador web
3. A calculadora funciona offline e não precisa de conexão com internet

## Personalizações

Para alterar as configurações, edite o arquivo data/config.json.
Para alterar os crimes e suas penalidades, edite o arquivo data/crimes.json.

Desenvolvido com Calculadora Penal FiveM (c) 2025.
        """
        zf.writestr('README.md', readme)
    
    # Posiciona o cursor no início do arquivo
    memory_file.seek(0)
    
    return send_file(
        memory_file,
        mimetype='application/zip',
        as_attachment=True,
        download_name=f'calculadora_penal_{city.name.lower().replace(" ", "_")}.zip'
    )

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
