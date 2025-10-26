from flask import Flask, request, jsonify
from flask_cors import CORS
from translate import Translator
import logging
import os

app = Flask(__name__)
frontend_url = os.environ.get('FRONTEND_URL', 'http://localhost:5173')
origins = [
    frontend_url
]

CORS(app, origins=origins)
logging.basicConfig(level=logging.DEBUG)

@app.route('/traduzir', methods=['POST'])
def traduzir_texto():

    try:
        dados = request.get_json()
        if not dados or 'texto' not in dados or 'destino' not in dados:
            return jsonify({"erro": "Dados incompletos. 'texto' e 'destino' são obrigatórios."}), 400

        texto_original = dados.get('texto')
        idioma_destino = dados.get('destino')

        if not texto_original.strip():
            return jsonify({"texto_traduzido": ""}), 200

        translator = Translator(to_lang=idioma_destino)
        texto_traduzido = translator.translate(texto_original)  
        return jsonify({
            "texto_traduzido": texto_traduzido
        }), 200

    except Exception as e:
        app.logger.error(f"Erro na tradução: {e}")
        return jsonify({"erro": f"Ocorreu um erro no servidor: {e}"}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
