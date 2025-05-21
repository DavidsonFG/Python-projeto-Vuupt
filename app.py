from flask import Flask, request, render_template, redirect, url_for, flash, jsonify
import requests
import os
from dotenv import load_dotenv
from datetime import datetime
import json

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
        
        # Preparar payload - corrigido para usar os nomes de campos esperados pela API
        payload = {
            "title": titulo,        # Nome em inglês conforme API
            "type": tipo            # tipo (coleta/entrega) conforme API
        }
        
        # Adicionar destinatário se fornecido
        if destinatario_id:
            payload["customer_id"] = destinatario_id  # Corrigido para customer_id conforme API
        
        # Adicionar campos opcionais se fornecidos
        if agente_id:
            payload["agent_id"] = agente_id  # Corrigido para agent_id conforme API
        if codigo:
            payload["code"] = codigo  # Corrigido para code conforme API
        if telefone:
            payload["phone"] = telefone  # Corrigido para phone conforme API
        if email:
            payload["email"] = email
        
        # Adicionar dados de geocodificação se disponíveis
        if geo_data:
            payload["address"] = geo_data["formatted_address"]  # Corrigido para address conforme API
            payload["latitude"] = geo_data["latitude"]
            payload["longitude"] = geo_data["longitude"]
        
        # Log do payload para debug
        app.logger.info(f"Payload do serviço: {json.dumps(payload)}")
        
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
        
        # Preparar payload - corrigido para usar os nomes de campos esperados pela API
        payload = {
            "name": nome,           # Corrigido para name conforme API
            "type": tipo,           # tipo (pessoa/empresa) conforme API
            "address": geo_data["formatted_address"],  # Corrigido para address conforme API
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
        
        # Preparar payload - corrigido para usar os nomes de campos esperados pela API
        payload = {
            "service_id": servico_id,  # Corrigido para service_id conforme API
            "start_time_estimation": previsao_inicio,  # Corrigido para start_time_estimation conforme API
            "start_base_id": base_inicio_id  # Corrigido para start_base_id conforme API
        }
        
        # Adicionar fim com base no tipo
        if tipo_fim == 'servico':
            payload["end_service_id"] = fim_id  # Corrigido para end_service_id conforme API
        else:
            payload["end_base_id"] = fim_id  # Corrigido para end_base_id conforme API
        
        # Adicionar campos opcionais se fornecidos
        if nome:
            payload["name"] = nome  # Corrigido para name conforme API
        if veiculo_id:
            payload["vehicle_id"] = veiculo_id  # Corrigido para vehicle_id conforme API
        if agente_id:
            payload["agent_id"] = agente_id  # Corrigido para agent_id conforme API
        
        # Log do payload para debug
        app.logger.info(f"Payload da rota: {json.dumps(payload)}")
        
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