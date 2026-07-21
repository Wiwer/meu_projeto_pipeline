from flask import Flask, request, jsonify

app = Flask(__name__)

def somar(a, b):
    return a + b

def dividir(a, b):
    if b == 0:
        raise ValueError("Não é possível dividir por zero!")
    return a / b

@app.route('/somar', methods=['GET'])
def api_somar():
    try:
        a = float(request.args.get('a', 0))
        b = float(request.args.get('b', 0))
        resultado = somar(a, b)
        return jsonify({'operacao': 'soma', 'resultado': resultado})
    except Exception as e:
        return jsonify({'erro': str(e)}), 400

@app.route('/dividir', methods=['GET'])
def api_dividir():
    try:
        a = float(request.args.get('a', 0))
        b = float(request.args.get('b', 0))
        resultado = dividir(a, b)
        return jsonify({'operacao': 'divisao', 'resultado': resultado})
    except ValueError as e:
        return jsonify({'erro': str(e)}), 400
    except Exception as e:
        return jsonify({'erro': str(e)}), 400

@app.route('/')
def home():
    return jsonify({
        'mensagem': '🚀 DEPLOY AUTOMATICO FUNCIONANDO! Quero ver se atualiza! Depois das alterações 44'
        '',
        'endpoints': {
            '/somar?a=2&b=3': 'Soma dois números',
            '/dividir?a=10&b=2': 'Divide dois números'
        }
    })

@app.route('/hello')
def hello():
    return jsonify({'mensagem': 'Hello, world! Olá, mundo! Atual2'})

if __name__ == '__main__':
    app.run(debug=True)

@app.route('/dump')
def dump():
    return jsonify({'mensagem': 'dump endpoint funcionando!'})

if __name__ == '__main__':
    app.run(debug=True)