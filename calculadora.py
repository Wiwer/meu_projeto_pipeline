from flask import Flask, request, jsonify
from fastapi import FastAPI, HTTPException, Query

app = Flask(__name__)
fastapi_app = FastAPI(
    title="Calculadora API",
    description="API de exemplo com operações de soma e divisão, com documentação automática OpenAPI/Swagger.",
    version="1.0.0",
)


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
        'mensagem': '🚀 DEPLOY AUTOMATICO FUNCIONANDO! Quero ver se atualiza! Depois das alterações 44',
        'endpoints': {
            '/somar?a=2&b=3': 'Soma dois números',
            '/dividir?a=10&b=2': 'Divide dois números'
        }
    })


@app.route('/hello')
def hello():
    return jsonify({'mensagem': 'Hello, world! Olá, mundo! Atual2'})


@app.route('/dump')
def dump():
    return jsonify({'mensagem': 'dump endpoint funcionando! Com teste!'})


@fastapi_app.get('/', summary='Documentação inicial da API')
def home_fastapi():
    return {
        'mensagem': '🚀 DEPLOY AUTOMATICO FUNCIONANDO! Quero ver se atualiza! Depois das alterações 44',
        'endpoints': {
            '/somar?a=2&b=3': 'Soma dois números',
            '/dividir?a=10&b=2': 'Divide dois números'
        },
    }


@fastapi_app.get('/hello', summary='Mensagem de teste')
def hello_fastapi():
    return {'mensagem': 'Hello, world! Olá, mundo! Atual2'}


@fastapi_app.get('/dump', summary='Endpoint de debug')
def dump_fastapi():
    return {'mensagem': 'dump endpoint funcionando! Com teste!'}


@fastapi_app.get('/somar', summary='Soma dois números')
def api_somar_fastapi(a: float = Query(..., description='Primeiro número'), b: float = Query(..., description='Segundo número')):
    try:
        return {'operacao': 'soma', 'resultado': somar(a, b)}
    except Exception as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


@fastapi_app.get('/dividir', summary='Divide dois números')
def api_dividir_fastapi(a: float = Query(..., description='Dividendo'), b: float = Query(..., description='Divisor')):
    try:
        return {'operacao': 'divisao', 'resultado': dividir(a, b)}
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    except Exception as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


if __name__ == '__main__':
    app.run(debug=True)