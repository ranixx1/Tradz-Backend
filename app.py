from flask import Flask, request, jsonify
from flask_cors import CORS
import requests

app = Flask(__name__)
CORS(app)

@app.route('/traduzir', methods=['POST'])
def traduzir():
    try:
        data = request.get_json()
        texto = data.get('texto')
        origem = data.get('origem', 'auto')
        destino = data.get('destino', 'en')

        url = "https://translate.argosopentech.com/translate" 

        payload = {
            "q": texto,
            "source": origem,
            "target": destino,
            "format": "text"
        }

        headers = {"Content-Type": "application/json"}
        response = requests.post(url, json=payload, headers=headers)

        try:
            traducao = response.json()
        except ValueError:
            print("Erro: resposta não é JSON:", response.text)
            return jsonify({"erro": "Resposta inválida da API"}), 500

        return jsonify({"traduzido": traducao.get("translatedText", "")})

    except Exception as e:
        print("Erro na tradução:", e)
        return jsonify({"erro": str(e)}), 500


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)
