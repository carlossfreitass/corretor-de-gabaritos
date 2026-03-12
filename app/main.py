from flask import Flask, request, jsonify

app = Flask(__name__)

app.config['JSON_AS_ASCII'] = False
app.json.ensure_ascii = False

@app.route('/')
def home():
  return jsonify({'status': 'API de correção de gabaritos ativa'})

if __name__ == '__main__':
  app.run(debug=True)