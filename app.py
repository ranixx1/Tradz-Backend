from flask import Flask, request, jsonify
from flask_cors import CORS
import translators as ts
import logging
import os

app = Flask(__name__)

frontend_url = os.environ.get('FRONTEND_URL', 'http://localhost:5173')
CORS(app, origins=[frontend_url])

logging.basicConfig(level=logging.DEBUG)

@app.route('/traduzir', methods=['POST'])
def traduzir_texto():
    try:
        dados = request.get_json()
        if not dados or 'texto' not in dados or 'destino' not in dados:
            return jsonify({"erro": "Dados incompletos. 'texto' e 'destino' são obrigatórios."}), 400

        texto_original = dados['texto']
        idioma_destino = dados['destino']

        if not texto_original.strip():
            return jsonify({"texto_traduzido": ""}), 200

        texto_traduzido = ts.translate_text(
            query_text=texto_original,
            translator='google',
            from_language='auto',
            to_language=idioma_destino
        )
        return jsonify({"texto_traduzido": texto_traduzido}), 200

    except Exception as e:
        app.logger.error(f"Erro na tradução: {e}")
        return jsonify({"erro": f"Ocorreu um erro no servidor: {e}"}), 500

if __name__ == '__main__':
    app.run(port=5000, debug=True)
