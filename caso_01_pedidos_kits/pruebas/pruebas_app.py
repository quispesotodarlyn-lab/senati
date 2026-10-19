"""
CASO 01 | Pruebas de la aplicación Flask y del modelo.

Ejecutar desde la carpeta del caso:
    python pruebas/pruebas_app.py
(No necesita levantar el servidor: usa el cliente de pruebas de Flask.)
"""

from pathlib import Path
import sys
import unittest

import pandas as pd
from sklearn.linear_model import LinearRegression
from sklearn.model_selection import train_test_split

RAIZ = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RAIZ))

import app as aplicacion  # noqa: E402  (se importa después de ajustar sys.path)

# Las dos pruebas obligatorias del enunciado: (nombre, valores del formulario)
PRUEBAS_OBLIGATORIAS = [('Prueba 1: semana con 20 consultas, S/ 200 y sin campaña',
  {'consultas_web': '20', 'inversion_publicidad_soles': '200', 'campana_escolar': '0'}),
 ('Prueba 2: semana con 55 consultas, S/ 800 y con campaña',
  {'consultas_web': '55', 'inversion_publicidad_soles': '800', 'campana_escolar': '1'})]

# Un formulario válido que se modifica en cada prueba de validación.
BASE_VALIDA = {'consultas_web': '30', 'inversion_publicidad_soles': '500', 'campana_escolar': '1'}


def estimacion_con_sklearn(valores):
    """Reentrena con scikit-learn (misma separación 80/20) para comparar con la web."""
    datos = pd.read_csv(RAIZ / "datos" / "datos.csv", encoding="utf-8-sig")
    columnas = aplicacion.MODELO["variables"]
    objetivo = aplicacion.MODELO["objetivo"]
    semilla = aplicacion.MODELO["separacion"]["random_state"]
    X_ent, _, y_ent, _ = train_test_split(datos[columnas], datos[objetivo],
                                          test_size=0.20, random_state=semilla)
    modelo = LinearRegression().fit(X_ent, y_ent)
    fila = pd.DataFrame([{c: float(valores[c]) for c in columnas}])
    return float(modelo.predict(fila)[0])


class PruebasModelo(unittest.TestCase):
    def test_modelo_json_coincide_con_sklearn(self):
        for nombre, valores in PRUEBAS_OBLIGATORIAS:
            web, _ = aplicacion.calcular({k: float(v) for k, v in valores.items()})
            esperado = estimacion_con_sklearn(valores)
            self.assertAlmostEqual(web, esperado, places=6, msg=nombre)

    def test_metricas_guardadas(self):
        metricas = aplicacion.MODELO["metricas_prueba"]
        self.assertGreater(metricas["R2"], 0.5)
        self.assertGreater(metricas["MAE"], 0)


class PruebasWeb(unittest.TestCase):
    def setUp(self):
        self.cliente = aplicacion.app.test_client()

    def test_pagina_inicial(self):
        respuesta = self.cliente.get("/")
        html = respuesta.get_data(as_text=True)
        self.assertEqual(respuesta.status_code, 200)
        self.assertNotIn("<script", html.lower())          # sin JavaScript
        for campo in aplicacion.CAMPOS:
            self.assertIn(f'name="{campo["nombre"]}"', html)

    def test_pruebas_obligatorias_dan_resultado(self):
        for nombre, valores in PRUEBAS_OBLIGATORIAS:
            respuesta = self.cliente.post("/", data=valores)
            html = respuesta.get_data(as_text=True)
            numericos = {k: float(v) for k, v in valores.items()}
            principal = aplicacion.preparar_resultado(numericos)["principal"]
            self.assertIn('class="resultado"', html, nombre)
            self.assertIn(principal, html, nombre)

    def test_rechaza_fuera_de_rango(self):
        for campo in aplicacion.CAMPOS:
            if campo["tipo"] != "numero":
                continue
            minimo, maximo = aplicacion.MODELO["rangos"][campo["nombre"]]
            for valor in (minimo - 1, maximo + 1):
                datos = dict(BASE_VALIDA, **{campo["nombre"]: str(valor)})
                html = self.cliente.post("/", data=datos).get_data(as_text=True)
                self.assertIn("Fuera de rango", html)
                self.assertNotIn('class="resultado"', html)

    def test_acepta_limites_exactos(self):
        for campo in aplicacion.CAMPOS:
            if campo["tipo"] != "numero":
                continue
            minimo, maximo = aplicacion.MODELO["rangos"][campo["nombre"]]
            for valor in (minimo, maximo):
                datos = dict(BASE_VALIDA, **{campo["nombre"]: f"{valor:g}"})
                html = self.cliente.post("/", data=datos).get_data(as_text=True)
                self.assertIn('class="resultado"', html)

    def test_rechaza_texto_vacio_nan_e_infinito(self):
        nombre = next(c["nombre"] for c in aplicacion.CAMPOS if c["tipo"] == "numero")
        for malo in ("", "abc", "nan", "inf", "-inf", "1e999"):
            datos = dict(BASE_VALIDA, **{nombre: malo})
            html = self.cliente.post("/", data=datos).get_data(as_text=True)
            self.assertIn("mensaje-error", html, f"entrada: {malo!r}")
            self.assertNotIn('class="resultado"', html, f"entrada: {malo!r}")

    def test_rechaza_opcion_binaria_invalida(self):
        nombre = next(c["nombre"] for c in aplicacion.CAMPOS if c["tipo"] == "binario")
        for malo in ("2", "-1", "si", ""):
            datos = dict(BASE_VALIDA, **{nombre: malo})
            html = self.cliente.post("/", data=datos).get_data(as_text=True)
            self.assertIn("mensaje-error", html)
            self.assertNotIn('class="resultado"', html)

    def test_acepta_coma_decimal(self):
        nombre = next(c["nombre"] for c in aplicacion.CAMPOS
                      if c["tipo"] == "numero" and not c.get("entero"))
        datos = dict(BASE_VALIDA, **{nombre: str(BASE_VALIDA[nombre]).replace(".", ",") + ",5"})
        html = self.cliente.post("/", data=datos).get_data(as_text=True)
        self.assertIn('class="resultado"', html)

    def test_consultas_deben_ser_enteras(self):
        datos = dict(BASE_VALIDA, consultas_web="20.5")
        html = self.cliente.post("/", data=datos).get_data(as_text=True)
        self.assertIn("número entero", html)
        self.assertNotIn('class="resultado"', html)


def mostrar_resultados_obligatorios():
    """Imprime los valores devueltos por el sistema en las dos pruebas del enunciado."""
    print("RESULTADOS DE LAS PRUEBAS OBLIGATORIAS")
    print("=" * 60)
    for nombre, valores in PRUEBAS_OBLIGATORIAS:
        numericos = {k: float(v) for k, v in valores.items()}
        estimacion, _ = aplicacion.calcular(numericos)
        resultado = aplicacion.preparar_resultado(numericos)
        print(f"{nombre}")
        print(f"  Entradas   : {valores}")
        print(f"  Estimación : {estimacion:.4f} {aplicacion.MODELO['unidad_objetivo']}")
        print(f"  Se muestra : {resultado['principal']}  |  {resultado['margen']}")
    print("=" * 60)


if __name__ == "__main__":
    mostrar_resultados_obligatorios()
    unittest.main(verbosity=2)
