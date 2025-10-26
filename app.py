from flask import Flask, request, jsonify
from flask_cors import CORS
import requests
import logging

app = Flask(__name__)

CORS(app, resources={r"/*": {"origins": ["https://tradz-front-project.vercel.app", "*"]}})

logging.basicConfig(level=logging.DEBUG)

def traduzir(texto, destino):
    url = "https://libretranslate.de/translate"
    payload = {"q": texto, "source": "auto", "target": destino, "format": "text"}
    r = requests.post(url, json=payload)
    r.raise_for_status()
    return r.json()["translatedText"]

@app.route('/traduzir', methods=['POST'])
def traduzir_texto():
    try:
        dados = request.get_json()
        if not dados or 'texto' not in dados or 'destino' not in dados:
            return jsonify({"erro": "Dados incompletos. 'texto' e 'destino' são obrigatórios."}), 400

        texto_original = dados.get('texto', '').strip()
        idioma_destino = dados.get('destino')

        if not texto_original:
            return jsonify({"texto_traduzido": ""}), 200

        texto_traduzido = traduzir(texto_original, idioma_destino)
        return jsonify({"texto_traduzido": texto_traduzido}), 200

    except Exception as e:
        app.logger.error(f"Erro na tradução: {e}")
        return jsonify({"erro": f"Ocorreu um erro no servidor: {e}"}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
