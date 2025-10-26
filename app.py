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
        print("Dados recebidos:", data)
        
        texto = data.get('texto')
        origem = data.get('origem', 'auto')
        destino = data.get('destino', 'en')

        if not texto:
            return jsonify({"erro": "Texto é obrigatório"}), 400

        # Opção 1: LibreTranslate (funciona melhor)
        url = "https://libretranslate.de/translate"
        
        payload = {
            "q": texto,
            "source": origem,
            "target": destino,
            "format": "text"
        }

        headers = {"Content-Type": "application/json"}
        
        try:
            response = requests.post(url, json=payload, headers=headers, timeout=10)
            print("Status da API:", response.status_code)
            print("Resposta da API:", response.text)
        except requests.exceptions.RequestException as e:
            print("Erro de conexão:", e)
            return jsonify({"erro": f"Erro de conexão: {str(e)}"}), 500

        if response.status_code != 200:
            # Tentar MyMemory API como fallback
            return usar_mymemory_api(texto, origem, destino)

        try:
            traducao = response.json()
            texto_traduzido = traducao.get("translatedText", "")
            print("Texto traduzido:", texto_traduzido)
            
            if texto_traduzido:
                return jsonify({
                    "texto_traduzido": texto_traduzido,
                    "traduzido": texto_traduzido
                })
            else:
                return usar_mymemory_api(texto, origem, destino)
            
        except ValueError as e:
            print("Erro ao parsear JSON:", e)
            return usar_mymemory_api(texto, origem, destino)

    except Exception as e:
        print("Erro na tradução:", e)
        return jsonify({"erro": str(e)}), 500

def usar_mymemory_api(texto, origem, destino):
    """Fallback para MyMemory API"""
    try:
        print("Usando MyMemory API como fallback...")
        url = "https://api.mymemory.translated.net/get"
        
        # Mapear códigos de idioma se necessário
        lang_map = {"pt": "pt-BR", "en": "en", "es": "es", "fr": "fr", "de": "de"}
        target_lang = lang_map.get(destino, destino)
        source_lang = "auto" if origem == "auto" else lang_map.get(origem, origem)
        
        params = {
            "q": texto,
            "langpair": f"{source_lang}|{target_lang}"
        }
        
        response = requests.get(url, params=params, timeout=10)
        print("MyMemory Status:", response.status_code)
        
        if response.status_code == 200:
            data = response.json()
            translated_text = data.get("responseData", {}).get("translatedText", "")
            
            if translated_text and translated_text != "PLEASE SELECT TWO DISTINCT LANGUAGES":
                return jsonify({
                    "texto_traduzido": translated_text,
                    "traduzido": translated_text
                })
        
        return jsonify({"erro": "Não foi possível traduzir o texto"}), 500
        
    except Exception as e:
        print("Erro no MyMemory:", e)
        return jsonify({"erro": "Serviço de tradução indisponível"}), 500

@app.route('/health', methods=['GET'])
def health():
    return jsonify({"status": "online", "message": "Backend funcionando"})

@app.route('/teste-traducao', methods=['GET'])
def teste_traducao():
    """Rota para testar a tradução"""
    try:
        # Teste simples
        url = "https://libretranslate.de/translate"
        payload = {
            "q": "hello",
            "source": "en",
            "target": "pt",
            "format": "text"
        }
        headers = {"Content-Type": "application/json"}
        response = requests.post(url, json=payload, headers=headers, timeout=10)
        return jsonify({
            "status": response.status_code,
            "resposta": response.json() if response.status_code == 200 else response.text
        })
    except Exception as e:
        return jsonify({"erro": str(e)}), 500

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000, debug=True)