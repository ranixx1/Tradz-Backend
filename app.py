from flask import Flask, request, jsonify
from flask_cors import CORS
import requests
import re
import html

app = Flask(__name__)
CORS(app)

# Mapeamento de idiomas para MyMemory API
LANG_MAP = {
    "pt": "pt-BR",
    "en": "en",
    "es": "es", 
    "fr": "fr",
    "de": "de",
    "it": "it",
    "ja": "ja"
}

def clean_html_tags(text):
    """Remove tags HTML do texto de forma mais agressiva"""
    if not text:
        return text
    
    print(f"Texto antes da limpeza: {repr(text)}")
    
    # Método 1: Remover tags HTML
    clean = re.compile('<.*?>')
    text = re.sub(clean, '', text)
    
    # Método 2: Decodificar entidades HTML
    text = html.unescape(text)
    
    # Método 3: Remover qualquer caractere especial problemático
    text = re.sub(r'[^\w\sáéíóúàèìòùâêîôûãõçñÁÉÍÓÚÀÈÌÒÙÂÊÎÔÛÃÕÇÑ,.;!?]', '', text)
    
    print(f"Texto após limpeza: {repr(text)}")
    
    return text.strip()

def detect_language(text):
    """Detecta o idioma do texto"""
    if not text or len(text.strip()) < 2:
        return "en"
    
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
    
    return max(scores.items(), key=lambda x: x[1])[0] if max(scores.values()) > 0 else 'en'

@app.route('/traduzir', methods=['POST', 'OPTIONS'])
def traduzir():
    try:
        if request.method == 'OPTIONS':
            return jsonify({}), 200
            
        data = request.get_json()
        texto = data.get('texto', '').strip()
        origem = data.get('origem', 'auto')
        destino = data.get('destino', 'en')

        print(f"Recebido: texto='{texto}', origem='{origem}', destino='{destino}'")

        if not texto:
            return jsonify({"erro": "Texto é obrigatório"}), 400

        if origem == 'auto':
            origem = detect_language(texto)
            print(f"Idioma detectado: {origem}")

        source_lang = LANG_MAP.get(origem, origem)
        target_lang = LANG_MAP.get(destino, destino)

        # MyMemory API
        url = "https://api.mymemory.translated.net/get"
        params = {
            "q": texto,
            "langpair": f"{source_lang}|{target_lang}"
        }
        
        print(f"Fazendo requisição para MyMemory: {params}")
        response = requests.get(url, params=params, timeout=10)
        
        print(f"Status da resposta: {response.status_code}")
        print(f"Resposta bruta: {response.text}")
        
        if response.status_code == 200:
            data = response.json()
            translated_text = data.get("responseData", {}).get("translatedText", "")
            
            print(f"Texto traduzido (bruto): {repr(translated_text)}")
            
            # Limpa as tags HTML do texto traduzido
            cleaned_text = clean_html_tags(translated_text)
            
            print(f"Texto final limpo: {repr(cleaned_text)}")
            
            # Verificar se a tradução é válida
            if (cleaned_text and 
                cleaned_text != "PLEASE SELECT TWO DISTINCT LANGUAGES" and
                cleaned_text != texto):
                
                return jsonify({
                    "texto_traduzido": cleaned_text,
                    "traduzido": cleaned_text
                })
            else:
                return jsonify({"erro": "Não foi possível traduzir o texto"}), 400
        else:
            return jsonify({"erro": "Erro na API de tradução"}), 500

    except Exception as e:
        print("Erro na tradução:", e)
        return jsonify({"erro": "Erro interno no servidor"}), 500

@app.route('/health', methods=['GET'])
def health():
    return jsonify({"status": "online"})

@app.route('/debug', methods=['POST'])
def debug():
    data = request.get_json()
    texto = data.get('texto', '')
    cleaned = clean_html_tags(texto)
    return jsonify({
        "original": texto,
        "limpo": cleaned,
        "repr_original": repr(texto),
        "repr_limpo": repr(cleaned)
    })

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)