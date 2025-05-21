from flask import Flask, request, render_template, redirect, url_for, flash, jsonify
import requests
import os
from dotenv import load_dotenv
from datetime import datetime

# Carregar variáveis de ambiente
load_dotenv()

app = Flask(__name__)
app.secret_key = "vuupt_integration_secret_key"

# Configurações da API
VUUPT_TOKEN = os.getenv("VUUPT_TOKEN")
VUUPT_BASE_URL = os.getenv("VUUPT_BASE_URL", "https://api.vuupt.com/api/v1")
GOOGLE_MAPS_API_KEY = os.getenv("GOOGLE_MAPS_API_KEY")

# Headers para requisições à API Vuupt
def get_vuupt_headers():
    return {
        "Authorization": f"Bearer {VUUPT_TOKEN}",
        "Content-Type": "application/json"
    }

# Função para geocodificação usando Google Maps API
def get_geocode_data(address):
    address = address.replace(" ", "+")
    url = f"https://maps.googleapis.com/maps/api/geocode/json?address={address}&key={GOOGLE_MAPS_API_KEY}"
    
    response = requests.get(url)
    data = response.json()
    
    if data['status'] == 'OK':
        result = data['results'][0]
        location = result['geometry']['location']
        formatted_address = result['formatted_address']
        
        return {
            'latitude': location['lat'],
            'longitude': location['lng'],
            'formatted_address': formatted_address
        }
    else:
        return None

# Rota principal
@app.route('/')
def index():
    return render_template('index.html')

# ----- SERVIÇOS -----

# Listar serviços
@app.route('/servicos')
def listar_servicos():
    try:
        response = requests.get(
            f"{VUUPT_BASE_URL}/services",
            headers=get_vuupt_headers()
        )
        response.raise_for_status()
        servicos = response.json()['data']
        return render_template('servicos/listar.html', servicos=servicos)
    except Exception as e:
        flash(f"Erro ao listar serviços: {str(e)}", "danger")
        return redirect(url_for('index'))

# Formulário para criar serviço
@app.route('/servicos/criar', methods=['GET'])
def form_servico():
    return render_template('servicos/criar.html')

# API para buscar contatos
@app.route('/api/contatos')
def api_contatos():
    try:
        response = requests.get(
            f"{VUUPT_BASE_URL}/customers",
            headers=get_vuupt_headers()
        )
        response.raise_for_status()
        return jsonify(response.json())
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# API para buscar agentes
@app.route('/api/agentes')
def api_agentes():
    try:
        response = requests.get(
            f"{VUUPT_BASE_URL}/agents",
            headers=get_vuupt_headers()
        )
        response.raise_for_status()
        return jsonify(response.json())
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# Criar serviço
@app.route('/servicos/criar', methods=['POST'])
def criar_servico():
    try:
        # Dados do formulário
        titulo = request.form.get('titulo')
        tipo = request.form.get('tipo')  # Coleta ou Entrega
        destinatario_id = request.form.get('destinatario_id')
        agente_id = request.form.get('agente_id')
        codigo = request.form.get('codigo')
        telefone = request.form.get('telefone')
        email = request.form.get('email')
        
        # Endereço (com geocodificação)
        endereco = request.form.get('endereco')
        geo_data = None
        
        if endereco:
            geo_data = get_geocode_data(endereco)
            if not geo_data:
                flash("Erro na geocodificação do endereço", "danger")
                return redirect(url_for('form_servico'))
        
        # Preparar payload
        payload = {
            "title": titulo,
            "type": tipo
        }
        
        # Adicionar destinatário se fornecido
        if destinatario_id:
            payload["destinatario_id"] = destinatario_id
        
        # Adicionar campos opcionais se fornecidos
        if agente_id:
            payload["agente_id"] = agente_id
        if codigo:
            payload["codigo"] = codigo
        if telefone:
            payload["telefone"] = telefone
        if email:
            payload["email"] = email
        
        # Adicionar dados de geocodificação se disponíveis
        if geo_data:
            payload["endereco"] = geo_data["formatted_address"]
            payload["latitude"] = geo_data["latitude"]
            payload["longitude"] = geo_data["longitude"]
        
        # Enviar requisição para a API
        response = requests.post(
            f"{VUUPT_BASE_URL}/services",
            headers=get_vuupt_headers(),
            json=payload
        )
        response.raise_for_status()
        
        flash("Serviço criado com sucesso!", "success")
        return redirect(url_for('listar_servicos'))
    
    except Exception as e:
        flash(f"Erro ao criar serviço: {str(e)}", "danger")
        return redirect(url_for('form_servico'))

# Criar novo contato
@app.route('/contatos/criar', methods=['POST'])
def criar_contato():
    try:
        # Dados do formulário
        nome = request.form.get('nome')
        tipo = request.form.get('tipo')  # Pessoa ou Empresa
        endereco = request.form.get('endereco')
        
        # Geocodificação
        geo_data = get_geocode_data(endereco)
        if not geo_data:
            return jsonify({"error": "Erro na geocodificação do endereço"}), 400
        
        # Preparar payload
        payload = {
            "nome": nome,
            "tipo": tipo,
            "endereco": geo_data["formatted_address"],
            "latitude": geo_data["latitude"],
            "longitude": geo_data["longitude"]
        }
        
        # Enviar requisição para a API
        response = requests.post(
            f"{VUUPT_BASE_URL}/customers",
            headers=get_vuupt_headers(),
            json=payload
        )
        response.raise_for_status()
        
        return jsonify(response.json())
    
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# ----- ROTAS -----

# Listar rotas
@app.route('/rotas')
def listar_rotas():
    try:
        response = requests.get(
            f"{VUUPT_BASE_URL}/routes",
            headers=get_vuupt_headers()
        )
        response.raise_for_status()
        rotas = response.json()['data']
        return render_template('rotas/listar.html', rotas=rotas)
    except Exception as e:
        flash(f"Erro ao listar rotas: {str(e)}", "danger")
        return redirect(url_for('index'))

# Formulário para criar rota
@app.route('/rotas/criar', methods=['GET'])
def form_rota():
    return render_template('rotas/criar.html')

# API para buscar serviços
@app.route('/api/servicos')
def api_servicos():
    try:
        response = requests.get(
            f"{VUUPT_BASE_URL}/services",
            headers=get_vuupt_headers()
        )
        response.raise_for_status()
        return jsonify(response.json())
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# API para buscar bases operacionais
@app.route('/api/bases')
def api_bases():
    try:
        response = requests.get(
            f"{VUUPT_BASE_URL}/operational-bases",
            headers=get_vuupt_headers()
        )
        response.raise_for_status()
        return jsonify(response.json())
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# API para buscar veículos
@app.route('/api/veiculos')
def api_veiculos():
    try:
        response = requests.get(
            f"{VUUPT_BASE_URL}/vehicles",
            headers=get_vuupt_headers()
        )
        response.raise_for_status()
        return jsonify(response.json())
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# Criar rota
@app.route('/rotas/criar', methods=['POST'])
def criar_rota():
    try:
        # Dados do formulário
        servico_id = request.form.get('servico_id')
        previsao_inicio = request.form.get('previsao_inicio')
        base_inicio_id = request.form.get('base_inicio_id')
        tipo_fim = request.form.get('tipo_fim')  # 'servico' ou 'base'
        
        if tipo_fim == 'servico':
            fim_id = servico_id
        else:
            fim_id = request.form.get('base_fim_id')
        
        nome = request.form.get('nome')
        veiculo_id = request.form.get('veiculo_id')
        agente_id = request.form.get('agente_id')
        
        # Preparar payload
        payload = {
            "servico_id": servico_id,
            "previsao_inicio": previsao_inicio,
            "base_inicio_id": base_inicio_id
        }
        
        # Adicionar fim com base no tipo
        if tipo_fim == 'servico':
            payload["servico_fim_id"] = fim_id
        else:
            payload["base_fim_id"] = fim_id
        
        # Adicionar campos opcionais se fornecidos
        if nome:
            payload["nome"] = nome
        if veiculo_id:
            payload["veiculo_id"] = veiculo_id
        if agente_id:
            payload["agente_id"] = agente_id
        
        # Enviar requisição para a API
        response = requests.post(
            f"{VUUPT_BASE_URL}/routes",
            headers=get_vuupt_headers(),
            json=payload
        )
        response.raise_for_status()
        
        flash("Rota criada com sucesso!", "success")
        return redirect(url_for('listar_rotas'))
    
    except Exception as e:
        flash(f"Erro ao criar rota: {str(e)}", "danger")
        return redirect(url_for('form_rota'))

if __name__ == "__main__":
    app.run(debug=True)