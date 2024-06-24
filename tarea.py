from flask import Flask, request, jsonify, render_template
import re

app = Flask(__name__)

# Reglas para el lexer
TOKEN_REGEX = re.compile(r'(<[^>]+>)|([^<]+)')

def is_html5(code):
    return code.strip().lower().startswith('<!doctype html>')

def tokenize(code):
    tokens = []
    for token in TOKEN_REGEX.findall(code):
        if token[0]:  # Si el token es una etiqueta
            token = token[0]
            if token.startswith('</'):  # Es una etiqueta de cierre
                tokens.append(('TAG_CLOSE', token[2:-1]))  # Eliminar </ y >
            elif token.endswith('/>'):  # Etiqueta auto-cerrada
                tokens.append(('TAG_SELF_CLOSE', token[1:-2]))  # Eliminar < y />
            else:  # Es una etiqueta de apertura
                tokens.append(('TAG_OPEN', token[1:-1]))  # Eliminar < y >
        elif token[1].strip():  # Capturar texto entre etiquetas
            tokens.append(('TEXT', token[1].strip()))
    return tokens

def syntactic_analysis(tokens):
    stack = []
    auto_close_tags = {'meta', 'img', 'input', 'br', 'hr', 'link', 'area', 'base', 'col', 'command', 'embed', 'keygen', 'param', 'source', 'track', 'wbr'}
    for token_type, value in tokens:
        if token_type == 'TAG_OPEN':
            tag_name = value.split()[0]  # Asume que el primer elemento es el nombre de la etiqueta
            if tag_name not in auto_close_tags:  # Solo apilar si no es auto-cerrada
                stack.append(tag_name)
        elif token_type == 'TAG_CLOSE':
            if not stack:
                return "Sintaxis Incorrecta: Cierre inesperado de la etiqueta </{}>".format(value)
            if stack.pop() != value:
                return "Sintaxis Incorrecta: La etiqueta de cierre </{}> no coincide".format(value)
    if stack:
        return "Sintaxis Incorrecta: Faltan etiquetas de cierre para {}".format(", ".join(stack))
    return "Sintaxis Correcta"

def semantic_analysis(tokens):
    # Ejemplo de análisis: verificar que la etiqueta 'meta' tenga un atributo 'charset="UTF-8"'
    meta_charset = False
    for i, (token_type, value) in enumerate(tokens):
        if token_type == 'TAG_OPEN' and 'meta' in value:
            if 'charset="UTF-8"' in value:
                meta_charset = True
    return "Análisis Semántico Correcto" if meta_charset else "Análisis Semántico Incorrecto"

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/lexical', methods=['POST'])
def lexical():
    code = request.json['code']
    if not is_html5(code):
        return jsonify(result="El código no es HTML5.")
    tokens = tokenize(code)
    result = "\n".join([f"Token: {token_type}, Value: {value}" for token_type, value in tokens])
    return jsonify(result=result)

@app.route('/syntactic', methods=['POST'])
def syntactic():
    code = request.json['code']
    if not is_html5(code):
        return jsonify(result="El código no es HTML5.")
    tokens = tokenize(code)
    result = syntactic_analysis(tokens)
    return jsonify(result=result)

@app.route('/semantic', methods=['POST'])
def semantic():
    code = request.json['code']
    if not is_html5(code):
        return jsonify(result="El código no es HTML5.")
    tokens = tokenize(code)
    result = semantic_analysis(tokens)
    return jsonify(result=result)

if __name__ == '__main__':
    app.run(debug=True)
