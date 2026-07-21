import calculadora
import pytest


def test_somar():
    assert calculadora.somar(2, 3) == 5
    assert calculadora.somar(-1, 1) == 0
    assert calculadora.somar(2.5, 0.5) == 3.0


def test_dividir():
    assert calculadora.dividir(10, 2) == 5.0
    assert calculadora.dividir(9, 3) == 3.0
    assert pytest.approx(calculadora.dividir(1, 3), 1e-9) == 1/3


def test_dividir_por_zero():
    with pytest.raises(ValueError):
        calculadora.dividir(5, 0)


def test_fastapi_docs_available():
    client = calculadora.app.test_client()

    docs = client.get('/docs')
    assert docs.status_code == 200
    assert 'Swagger UI' in docs.get_data(as_text=True)

    openapi = client.get('/openapi.json')
    assert openapi.status_code == 200
    schema = openapi.get_json()
    assert schema['info']['title'] == 'Calculadora API'

    root = client.get('/')
    assert root.status_code == 200
    assert root.get_json()['mensagem']

    hello = client.get('/hello')
    assert hello.status_code == 200
    assert hello.get_json()['mensagem'] == 'Hello, world! Olá, mundo! Atual2'

    dump = client.get('/dump')
    assert dump.status_code == 200
    assert dump.get_json()['mensagem'] == 'dump endpoint funcionando! Com teste!'

    soma = client.get('/somar?a=2&b=3')
    assert soma.status_code == 200
    assert soma.get_json()['resultado'] == 5.0

    divisao = client.get('/dividir?a=10&b=2')
    assert divisao.status_code == 200
    assert divisao.get_json()['resultado'] == 5.0

    divisao_zero = client.get('/dividir?a=10&b=0')
    assert divisao_zero.status_code == 400
    assert 'Não é possível dividir por zero' in divisao_zero.get_json()['erro']


def test_api_endpoints():
    from fastapi.testclient import TestClient

    app = calculadora.app
    client = app.test_client()
    fastapi_client = TestClient(calculadora.fastapi_app)

    # Flask compatibility surface used by deploy
    r = client.get('/')
    assert r.status_code == 200
    data = r.get_json()
    assert 'mensagem' in data
    assert 'endpoints' in data

    r = client.get('/hello')
    assert r.status_code == 200
    assert r.get_json().get('mensagem') == 'Hello, world! Olá, mundo! Atual2'

    r = client.get('/dump')
    assert r.status_code == 200
    assert r.get_json().get('mensagem') == 'dump endpoint funcionando! Com teste!'

    r = client.get('/somar?a=2&b=3')
    assert r.status_code == 200
    assert r.get_json().get('resultado') == 5.0

    r = client.get('/dividir?a=10&b=2')
    assert r.status_code == 200
    assert r.get_json().get('resultado') == 5.0

    r = client.get('/dividir?a=10&b=0')
    assert r.status_code == 400
    assert 'Não é possível dividir por zero' in r.get_json().get('erro')

    # FastAPI app surface used by the ASGI runtime
    r = fastapi_client.get('/')
    assert r.status_code == 200
    assert 'mensagem' in r.json()

    r = fastapi_client.get('/hello')
    assert r.status_code == 200
    assert r.json().get('mensagem') == 'Hello, world! Olá, mundo! Atual2'

    r = fastapi_client.get('/dump')
    assert r.status_code == 200
    assert r.json().get('mensagem') == 'dump endpoint funcionando! Com teste!'

    r = fastapi_client.get('/somar?a=2&b=3')
    assert r.status_code == 200
    assert r.json().get('resultado') == 5.0

    r = fastapi_client.get('/somar?a=abc&b=2')
    assert r.status_code == 422

    r = fastapi_client.get('/dividir?a=10&b=2')
    assert r.status_code == 200
    assert r.json().get('resultado') == 5.0

    r = fastapi_client.get('/dividir?a=10&b=0')
    assert r.status_code == 400
    assert 'Não é possível dividir por zero' in r.json().get('detail')


@pytest.mark.parametrize("a,b,expected", [
    (0, 0, 0),
    (1e18, 1e18, 2e18),
    (-1e6, 1e6, 0),
    (2.5, 2.5, 5.0),
])
def test_somar_parametrized(a, b, expected):
    assert calculadora.somar(a, b) == expected


@pytest.mark.parametrize("a,b,expected", [
    (10, 2, 5.0),
    (-9, -3, 3.0),
    (7, 2, 3.5),
])
def test_dividir_parametrized(a, b, expected):
    assert calculadora.dividir(a, b) == expected