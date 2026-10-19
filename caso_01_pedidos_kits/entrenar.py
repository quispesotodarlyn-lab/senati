"""
CASO 01 | Taller de Machine Learning y Deep Learning - SENATI
Sistema de estimación de pedidos de kits de robótica

Script de entrenamiento: lee datos/datos.csv, separa 80 % entrenamiento / 20 % prueba,
entrena una regresión lineal múltiple (LinearRegression), calcula MAE y R² sobre la
prueba y guarda los coeficientes en modelo.json (lo usa app.py).

Uso (desde esta carpeta):
    python entrenar.py
"""

from pathlib import Path
import json

import pandas as pd
from sklearn.linear_model import LinearRegression
from sklearn.metrics import mean_absolute_error, r2_score
from sklearn.model_selection import train_test_split

# ---------------------------------------------------------------- configuración
CARPETA = Path(__file__).resolve().parent
ARCHIVO_CSV = CARPETA / "datos" / "datos.csv"
ARCHIVO_MODELO = CARPETA / "modelo.json"

COLUMNAS = ['consultas_web', 'inversion_publicidad_soles', 'campana_escolar']      # variables X (entradas)
OBJETIVO = "pedidos_kits"    # variable y (lo que queremos estimar)
UNIDAD_Y = "pedidos por semana"

# Rangos válidos indicados en el enunciado; la web rechaza valores fuera de ellos.
RANGOS = {'consultas_web': (5, 70), 'inversion_publicidad_soles': (0, 1100), 'campana_escolar': (0, 1)}

PROPORCION_PRUEBA = 0.20   # 20 % de las filas se reservan para evaluar
SEMILLA = 42               # misma separación en cada ejecución (resultados repetibles)


def main():
    # -------------------------------------------- Paso 1: leer y revisar el CSV
    # utf-8-sig elimina la marca BOM que Excel agrega al inicio del archivo.
    datos = pd.read_csv(ARCHIVO_CSV, encoding="utf-8-sig")
    print("=== PASO 1. Lectura y revisión del CSV ===")
    print(f"Filas: {len(datos)} | Columnas: {list(datos.columns)}")
    print(datos.head(), "\n")

    ausentes = datos[COLUMNAS + [OBJETIVO]].isna().sum()
    print("Valores ausentes por columna:")
    print(ausentes.to_string(), "\n")
    print(f"Filas duplicadas: {datos.duplicated().sum()}")

    # Limpieza: si hubiera filas con datos ausentes, se descartan (aquí no hay).
    antes = len(datos)
    datos = datos.dropna(subset=COLUMNAS + [OBJETIVO]).drop_duplicates()
    print(f"Filas descartadas por limpieza: {antes - len(datos)}")

    # Comprobamos que los datos reales respetan los rangos del enunciado.
    for columna, (minimo, maximo) in RANGOS.items():
        fuera = ((datos[columna] < minimo) | (datos[columna] > maximo)).sum()
        print(f"{columna}: min={datos[columna].min():g}, max={datos[columna].max():g} "
              f"(rango válido {minimo:g}-{maximo:g}) -> filas fuera: {fuera}")

    # ------------------------------------- Paso 2: variables y separación 80/20
    X = datos[COLUMNAS]
    y = datos[OBJETIVO]
    X_entrenamiento, X_prueba, y_entrenamiento, y_prueba = train_test_split(
        X, y, test_size=PROPORCION_PRUEBA, random_state=SEMILLA
    )
    print("\n=== PASO 2. Separación de datos ===")
    print(f"Entrenamiento: {len(X_entrenamiento)} filas | Prueba: {len(X_prueba)} filas")

    # --------------------------------------------------- Paso 3: entrenar modelo
    modelo = LinearRegression()
    modelo.fit(X_entrenamiento, y_entrenamiento)
    coeficientes = dict(zip(COLUMNAS, modelo.coef_))

    print("\n=== PASO 3. Coeficientes del modelo ===")
    print(f"Intercepto: {modelo.intercept_:.4f} {UNIDAD_Y} (valor cuando todas las X valen 0)")
    for columna, coeficiente in coeficientes.items():
        print(f"{columna}: {coeficiente:.4f} -> si {columna} sube 1 unidad y las demás "
              f"no cambian, {OBJETIVO} cambia {coeficiente:+.4f} {UNIDAD_Y}")

    # ---------------------------------------------------- Paso 4: evaluar (prueba)
    predicciones = modelo.predict(X_prueba)
    mae = mean_absolute_error(y_prueba, predicciones)
    r2 = r2_score(y_prueba, predicciones)
    print("\n=== PASO 4. Evaluación con los datos de prueba ===")
    print(f"MAE = {mae:.3f} {UNIDAD_Y}  (error promedio absoluto)")
    print(f"R²  = {r2:.3f}  (proporción de la variación de {OBJETIVO} que explica el modelo)")

    # ------------------------------------------- Paso 6: guardar modelo.json
    contenido = {
        "caso": "CASO 01",
        "descripcion": "Sistema de estimación de pedidos de kits de robótica",
        "tipo_modelo": "LinearRegression (scikit-learn)",
        "variables": COLUMNAS,
        "objetivo": OBJETIVO,
        "unidad_objetivo": UNIDAD_Y,
        "intercepto": float(modelo.intercept_),
        "coeficientes": {k: float(v) for k, v in coeficientes.items()},
        "rangos": {k: [float(a), float(b)] for k, (a, b) in RANGOS.items()},
        "metricas_prueba": {"MAE": float(mae), "R2": float(r2)},
        "filas": {"total": int(len(datos)),
                  "entrenamiento": int(len(X_entrenamiento)),
                  "prueba": int(len(X_prueba))},
        "separacion": {"proporcion_prueba": PROPORCION_PRUEBA, "random_state": SEMILLA},
        "nota": "Datos simulados. Estimación educativa, no una cifra comercial.",
    }
    with open(ARCHIVO_MODELO, "w", encoding="utf-8") as archivo:
        json.dump(contenido, archivo, indent=2, ensure_ascii=False)
    print(f"\nModelo guardado en: {ARCHIVO_MODELO.name}")


if __name__ == "__main__":
    main()
