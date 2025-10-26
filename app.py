from flask import Flask, request, jsonify
from flask_cors import CORS
import requests

app = Flask(__name__)
CORS(app)

# Mapeamento de idiomas para MyMemory API
LANG_MAP = {
    "pt": "pt-BR",      # Português Brasileiro
    "en": "en",         # Inglês
    "es": "es",         # Espanhol
    "fr": "fr",         # Francês
    "de": "de",         # Alemão
    "it": "it",         # Italiano
    "ja": "ja",         # Japonês
    "ko": "ko",         # Coreano
    "zh": "zh-CN",      # Chinês
    "ru": "ru",         # Russo
    "ar": "ar",         # Árabe
    "hi": "hi"          # Hindi
}

def detect_language(text):
    """
    Detecta o idioma do texto usando uma API simples
    """
    if not text or len(text.strip()) < 2:
        return "en"  # Default para inglês
    
    # Análise básica por palavras comuns
    text_lower = text.lower()
    
    portuguese_words = ['o', 'a', 'de', 'do', 'da', 'em', 'um', 'uma', 'é', 'são', 'que']
    english_words = ['the', 'a', 'an', 'in', 'on', 'at', 'is', 'are', 'to', 'for']
    spanish_words = ['el', 'la', 'de', 'en', 'un', 'una', 'es', 'son', 'que']
    french_words = ['le', 'la', 'de', 'en', 'un', 'une', 'est', 'sont', 'que']
    german_words = ['der', 'die', 'das', 'in', 'ein', 'eine', 'ist', 'sind', 'und']
    
    scores = {
        'pt': sum(1 for word in portuguese_words if word in text_lower),
        'en': sum(1 for word in english_words if word in text_lower),
        'es': sum(1 for word in spanish_words if word in text_lower),
        'fr': sum(1 for word in french_words if word in text_lower),
        'de': sum(1 for word in german_words if word in text_lower)
    }
    
    # Retorna o idioma com maior score, ou inglês por padrão
    return max(scores.items(), key=lambda x: x[1])[0] if max(scores.values()) > 0 else 'en'

@app.route('/traduzir', methods=['POST', 'OPTIONS'])
def traduzir():
    try:
        if request.method == 'OPTIONS':
            return jsonify({}), 200
            
        data = request.get_json()
        print("Dados recebidos:", data)
        
        texto = data.get('texto', '').strip()
        origem = data.get('origem', 'auto')
        destino = data.get('destino', 'en')

        if not texto:
            return jsonify({"erro": "Texto é obrigatório"}), 400

        # Se origem for 'auto', detectar o idioma
        if origem == 'auto':
            origem = detect_language(texto)
            print(f"Idioma detectado: {origem}")

        # Mapear códigos de idioma para MyMemory
        source_lang = LANG_MAP.get(origem, origem)
        target_lang = LANG_MAP.get(destino, destino)

        # MyMemory API
        url = "https://api.mymemory.translated.net/get"
        params = {
            "q": texto,
            "langpair": f"{source_lang}|{target_lang}"
        }
        
        print(f"Enviando para MyMemory: {params}")
        response = requests.get(url, params=params, timeout=10)
        print(f"Status MyMemory: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            translated_text = data.get("responseData", {}).get("translatedText", "")
            
            print(f"Texto traduzido: {translated_text}")
            
            # Verificar se a tradução é válida
            if (translated_text and 
                translated_text != "PLEASE SELECT TWO DISTINCT LANGUAGES" and
                translated_text != texto):  # Evitar retornar o mesmo texto
                
                return jsonify({
                    "texto_traduzido": translated_text,
                    "traduzido": translated_text,
                    "idioma_detectado": origem if origem != 'auto' else None
                })
            else:
                return jsonify({
                    "erro": "Não foi possível traduzir o texto",
                    "detalhes": "Texto muito curto ou idiomas incompatíveis"
                }), 400
        else:
            return jsonify({
                "erro": "Erro na API de tradução", 
                "status": response.status_code
            }), 500

    except requests.exceptions.Timeout:
        return jsonify({"erro": "Timeout na conexão com serviço de tradução"}), 500
    except requests.exceptions.RequestException as e:
        return jsonify({"erro": f"Erro de conexão: {str(e)}"}), 500
    except Exception as e:
        print("Erro geral na tradução:", e)
        return jsonify({"erro": "Erro interno no servidor"}), 500

@app.route('/health', methods=['GET'])
def health():
    return jsonify({
        "status": "online", 
        "servico": "Tradz Backend",
        "api": "MyMemory Translation"
    })

@app.route('/teste-traducao', methods=['GET'])
def teste_traducao():
    """Rota para testar a tradução"""
    try:
        # Teste simples
        texto_teste = "hello world"
        params = {
            "q": texto_teste,
            "langpair": "en|pt-BR"
        }
        
        response = requests.get("https://api.mymemory.translated.net/get", params=params, timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            translated = data.get("responseData", {}).get("translatedText", "")
            
            return jsonify({
                "status": "success",
                "teste": texto_teste,
                "traduzido": translated,
                "api_status": "funcionando"
            })
        else:
            return jsonify({
                "status": "error",
                "erro": f"API retornou status {response.status_code}"
            }), 500
            
    except Exception as e:
        return jsonify({
            "status": "error",
            "erro": str(e)
        }), 500

@app.route('/idiomas', methods=['GET'])
def listar_idiomas():
    """Lista os idiomas suportados"""
    idiomas = [
        {"codigo": "pt", "nome": "Português"},
        {"codigo": "en", "nome": "Inglês"},
        {"codigo": "es", "nome": "Espanhol"},
        {"codigo": "fr", "nome": "Francês"},
        {"codigo": "de", "nome": "Alemão"},
        {"codigo": "it", "nome": "Italiano"},
        {"codigo": "ja", "nome": "Japonês"}
    ]
    return jsonify(idiomas)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000, debug=True)