from flask import Flask, request, jsonify
from flask_cors import CORS
import requests

app = Flask(__name__)
CORS(app)  

@app.route('/traduzir', methods=['POST', 'OPTIONS'])
def traduzir():
    try:
        # Handle preflight request
        if request.method == 'OPTIONS':
            return jsonify({}), 200
            
        data = request.get_json()
        print("Dados recebidos:", data)  #  debug
        
        texto = data.get('texto')
        origem = data.get('origem', 'auto')
        destino = data.get('destino', 'en')

        if not texto:
            return jsonify({"erro": "Texto é obrigatório"}), 400

        url = "https://translate.argosopentech.com/translate" 

        payload = {
            "q": texto,
            "source": origem,
            "target": destino,
            "format": "text"
        }

        headers = {"Content-Type": "application/json"}
        response = requests.post(url, json=payload, headers=headers)
        print("Status da API:", response.status_code)  # debug
        print("Resposta da API:", response.text)  # debug

        if response.status_code != 200:
            return jsonify({"erro": f"Erro na API de tradução: {response.status_code}"}), 500

        try:
            traducao = response.json()
            texto_traduzido = traducao.get("translatedText", "")
            print("Texto traduzido:", texto_traduzido)  # debug
            
            return jsonify({
                "texto_traduzido": texto_traduzido,
                "traduzido": texto_traduzido  
            })
            
        except ValueError as e:
            print("Erro ao parsear JSON:", e)
            print("Resposta original:", response.text)
            return jsonify({"erro": "Resposta inválida da API"}), 500

    except Exception as e:
        print("Erro na tradução:", e)
        return jsonify({"erro": str(e)}), 500

@app.route('/health', methods=['GET'])
def health():
    return jsonify({"status": "online"})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000, debug=True)