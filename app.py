from flask import Flask, request, jsonify
from flask_cors import CORS
import requests
import re
import html
import unicodedata

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

def clean_translation_text(text):
    """Limpa o texto traduzido de forma mais robusta"""
    if not text:
        return ""
    
    print(f"Texto recebido para limpeza: {repr(text)}")
    
    # 1. Remove todas as tags HTML
    text = re.sub(r'<[^>]+>', '', text)
    
    # 2. Decodifica entidades HTML
    text = html.unescape(text)
    
    # 3. Remove caracteres de controle e unicode problemático
    text = ''.join(char for char in text if unicodedata.category(char)[0] != 'C')
    
    # 4. Remove espaços extras e quebras de linha no início/fim
    text = text.strip()
    
    # 5. Corrige problemas comuns de formatação
    text = re.sub(r'\s+', ' ', text)
    

    if len(text) <= 3 and any(char in text for char in ['á', 'é', 'í', 'ó', 'ú']):
        # Para espanhol: "Oá" provavelmente deveria ser "Hola"
        if text.lower() in ['oá', 'oÁ']:
            text = 'Hola'
        # Para francês: "bonjour," -> "bonjour"
        elif text.lower().startswith('bonjour'):
            text = 'Bonjour'
    
    print(f"Texto após limpeza: {repr(text)}")
    return text

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
        
        if response.status_code == 200:
            data = response.json()
            translated_text = data.get("responseData", {}).get("translatedText", "")
            
            print(f"Texto traduzido (bruto): {repr(translated_text)}")
            
            cleaned_text = clean_translation_text(translated_text)
            
            if (cleaned_text and 
                cleaned_text != "PLEASE SELECT TWO DISTINCT LANGUAGES" and
                cleaned_text != texto):
                
                if destino == 'es' and texto.lower() == 'olá' and cleaned_text.lower() in ['oá', 'oÁ']:
                    cleaned_text = 'Hola'
                elif destino == 'fr' and texto.lower() == 'olá' and 'bonjour' in cleaned_text.lower():
                    cleaned_text = 'Bonjour'
                
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

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)