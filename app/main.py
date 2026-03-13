from flask import Flask, request, jsonify
from services.gabarito_service import gerar_gabarito
from services.omr_service import corrigir_gabarito

app = Flask(__name__)

app.config['JSON_AS_ASCII'] = False
app.json.ensure_ascii = False

@app.route('/')
def inicio():
  return jsonify({'status': 'API de correção de gabaritos ativa'})

@app.route('/gerar-gabarito', methods=['POST'])
def rota_gerar_gabarito():
  data = request.json

  total_questoes = data.get('total_questoes')
  alternativas = data.get('alternativas')
  orientacao = data.get('orientacao')
  id_prova = data.get('id_prova')

  caminho = gerar_gabarito(
    total_questoes,
    alternativas,
    orientacao,
    id_prova
  )

  return jsonify({
    'mensagem': 'gabarito gerado',
    'caminho': caminho
  })

@app.route('/corrigir-gabarito', methods=['POST'])
def rota_corrigir_gabarito():
  file = request.file.get('file')
  metadata = request.form.get('metadata')

  resultado = corrigir_gabarito(file, metadata)

  return jsonify(resultado)

if __name__ == '__main__':
  app.run(debug=True)