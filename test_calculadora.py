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


def test_api_endpoints():
    app = calculadora.app
    client = app.test_client()

    # home
    r = client.get('/')
    assert r.status_code == 200
    data = r.get_json()
    assert 'mensagem' in data
    assert 'endpoints' in data

    # hello
    r = client.get('/hello')
    assert r.status_code == 200
    assert r.get_json().get('mensagem') == 'Hello, world! Olá, mundo! Atual2'

    # soma endpoint valid
    r = client.get('/somar?a=2&b=3')
    assert r.status_code == 200
    assert r.get_json().get('resultado') == 5.0

    # soma endpoint invalid param -> 400
    r = client.get('/somar?a=abc&b=2')
    assert r.status_code == 400

    # dividir endpoint valid
    r = client.get('/dividir?a=10&b=2')
    assert r.status_code == 200
    assert r.get_json().get('resultado') == 5.0

    # dividir by zero -> 400
    r = client.get('/dividir?a=10&b=0')
    assert r.status_code == 400
    assert 'Não é possível dividir por zero' in r.get_json().get('erro')


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