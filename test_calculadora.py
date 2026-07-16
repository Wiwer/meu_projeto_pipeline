import calculadora
import pytest

def test_somar():
    assert calculadora.somar(2, 3) == 5
    assert calculadora.somar(-1, 1) == 0

def test_dividir():
    assert calculadora.dividir(10, 2) == 5.0
    assert calculadora.dividir(9, 3) == 3.0

# Este teste vai falhar se você descomentar a linha abaixo:
# def test_dividir_por_zero():
#     with pytest.raises(ValueError):
#         calculadora.dividir(5, 0)