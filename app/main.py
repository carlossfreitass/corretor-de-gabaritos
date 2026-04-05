import json
from flask import Flask, request, jsonify
from services.gabarito_service import gerar_gabarito
from services.omr_service import corrigir_gabarito

app = Flask(__name__)

app.json.sort_keys = False
app.config['JSON_AS_ASCII'] = False
app.json.ensure_ascii = False

@app.route('/')
def inicio():
    return jsonify({'status': 'API de correção de gabaritos ativa'})

@app.route('/gerar-gabarito', methods=['POST'])
def rota_gerar_gabarito():
    data = request.json

    nome_prova = data.get('nome_prova')
    id_prova = data.get('id_prova')
    total_questoes = data.get('total_questoes')
    alternativas = data.get('alternativas')

    caminho = gerar_gabarito(
        nome_prova,
        id_prova,
        total_questoes,
        alternativas,
    )

    return jsonify({
        'mensagem': 'gabarito gerado',
        'caminho': caminho,
    })

@app.route('/corrigir-gabarito', methods=['POST'])
def rota_corrigir_gabarito():
    # ARQUIVO DE IMAGEM
    file = request.files.get('file')
    if not file:
        return jsonify({"erro": "Nenhum arquivo de imagem enviado."}), 400

    # GABARITO OFICIAL
    gabarito_raw = request.form.get('gabarito')
    if not gabarito_raw:
        return jsonify({"erro": "Gabarito não enviado."}), 400

    try:
        gabarito = json.loads(gabarito_raw)
    except json.JSONDecodeError:
        return jsonify({"erro": "gabarito inválido. Envie um JSON válido."}), 400

    # VALOR DA PROVA
    valor_prova = float(request.form.get('valor_prova', 10.0))

    # PESOS
    pesos_raw = request.form.get('pesos')
    pesos = json.loads(pesos_raw) if pesos_raw else None

    resultado = corrigir_gabarito(
        file,
        gabarito,
        valor_prova,
        pesos,
    )

    return jsonify(resultado)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)