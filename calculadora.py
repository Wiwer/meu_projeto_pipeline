from urllib.parse import parse_qs

from flask import Flask, request, jsonify

app = Flask(__name__)

try:
    from fastapi import FastAPI, HTTPException, Query
except ImportError:  # pragma: no cover - fallback para ambientes sem FastAPI instalado
    FASTAPI_AVAILABLE = False
    fastapi_app = None
else:
    FASTAPI_AVAILABLE = True
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


if FASTAPI_AVAILABLE:
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
else:  # pragma: no cover - fallback só usado em ambientes sem FastAPI instalado
    async def _fallback_fastapi_app(scope, receive, send):
        async def _send_json(status, payload):
            await send({
                'type': 'http.response.start',
                'status': status,
                'headers': [(b'content-type', b'application/json')],
            })
            await send({
                'type': 'http.response.body',
                'body': payload.encode('utf-8'),
            })

        path = scope.get('path', '/')
        method = scope.get('method', 'GET')
        query = parse_qs(scope.get('query_string', b'').decode('utf-8'))

        if method != 'GET':
            await _send_json(405, '{"detail": "Method not allowed"}')
            return

        if path == '/docs':
            await send({
                'type': 'http.response.start',
                'status': 200,
                'headers': [(b'content-type', b'text/html; charset=utf-8')],
            })
            await send({
                'type': 'http.response.body',
                'body': b'<!doctype html><html><body><h1>Calculadora API</h1><p>Swagger UI fallback ativo.</p></body></html>',
            })
            return

        if path == '/openapi.json':
            await _send_json(200, '{"info": {"title": "Calculadora API", "version": "1.0.0"}}')
            return

        if path == '/':
            await _send_json(200, '{"mensagem": "🚀 DEPLOY AUTOMATICO FUNCIONANDO! Quero ver se atualiza! Depois das alterações 44", "endpoints": {"/somar?a=2&b=3": "Soma dois números", "/dividir?a=10&b=2": "Divide dois números"}}')
            return

        if path == '/hello':
            await _send_json(200, '{"mensagem": "Hello, world! Olá, mundo! Atual2"}')
            return

        if path == '/dump':
            await _send_json(200, '{"mensagem": "dump endpoint funcionando! Com teste!"}')
            return

        if path == '/somar':
            try:
                a = float(query.get('a', ['0'])[0])
                b = float(query.get('b', ['0'])[0])
                await _send_json(200, '{"operacao": "soma", "resultado": ' + str(somar(a, b)) + '}')
            except Exception as exc:
                await _send_json(400, '{"detail": "' + str(exc) + '"}')
            return

        if path == '/dividir':
            try:
                a = float(query.get('a', ['0'])[0])
                b = float(query.get('b', ['0'])[0])
                await _send_json(200, '{"operacao": "divisao", "resultado": ' + str(dividir(a, b)) + '}')
            except Exception as exc:
                await _send_json(400, '{"detail": "' + str(exc) + '"}')
            return

        await _send_json(404, '{"detail": "Not Found"}')

    fastapi_app = _fallback_fastapi_app


if __name__ == '__main__':
    app.run(debug=True)