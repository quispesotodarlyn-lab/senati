"""
CASO 01 | Taller de Machine Learning y Deep Learning - SENATI
Sistema de estimación de pedidos de kits de robótica

Aplicación web con Flask (solo Python + HTML + CSS, sin JavaScript).
Lee los coeficientes guardados en modelo.json (creado por entrenar.py), valida los
datos del formulario y calcula la estimación con la fórmula de la regresión lineal:

    y = intercepto + coef_1 * x_1 + coef_2 * x_2 + coef_3 * x_3

Uso (desde esta carpeta):
    python app.py        ->  abrir http://127.0.0.1:5000
"""

from pathlib import Path
import json
import math

from flask import Flask, render_template, request

app = Flask(__name__)
CARPETA = Path(__file__).resolve().parent

# Cargamos el modelo una sola vez al iniciar Flask.
with open(CARPETA / "modelo.json", encoding="utf-8") as archivo:
    MODELO = json.load(archivo)

# Textos que se muestran en la página.
TEXTOS = {'titulo_pestana': 'Pedidos de kits de robótica',
 'subtitulo': 'Caso práctico 1 · Regresión lineal múltiple',
 'titulo': '¿Cuántos kits de robótica nos pedirán esta semana?',
 'introduccion': 'Ingresa las consultas web, la inversión en publicidad y si hay campaña '
                 'escolar para estimar los pedidos semanales.',
 'boton': 'Calcular',
 'etiqueta_resultado': 'Pedidos estimados para la semana',
 'aviso': 'Estimación con datos simulados de práctica. Es un modelo lineal sencillo: úsala '
          'solo como referencia y verifícala con la realidad de la tienda antes de decidir '
          'compras o inventario.'}

# Campos del formulario. Los límites (mínimo y máximo) vienen de modelo.json.
# tipo "numero": se escribe un número | tipo "binario": se elige entre dos opciones 0/1.
CAMPOS = [{'nombre': 'consultas_web',
  'etiqueta': 'Consultas web de la semana',
  'unidad': 'consultas',
  'tipo': 'numero',
  'entero': True,
  'ejemplo': 'Ej.: 20'},
 {'nombre': 'inversion_publicidad_soles',
  'etiqueta': 'Inversión en publicidad',
  'unidad': 'soles',
  'tipo': 'numero',
  'ejemplo': 'Ej.: 200'},
 {'nombre': 'campana_escolar',
  'etiqueta': '¿Hay campaña escolar?',
  'unidad': '',
  'tipo': 'binario',
  'opciones': [(0, 'No (0)'), (1, 'Sí (1)')]}]


def leer_numero(texto):
    """Convierte el texto del formulario en número. Devuelve None si no es válido."""
    try:
        numero = float(texto.strip().replace(",", "."))
    except ValueError:
        return None
    # float("nan") y float("inf") se convierten sin error, pero no son datos útiles.
    return numero if math.isfinite(numero) else None


def validar(formulario):
    """Valida todos los campos. Devuelve (valores_numericos, errores_por_campo)."""
    valores, errores = {}, {}
    for campo in CAMPOS:
        nombre = campo["nombre"]
        texto = formulario.get(nombre, "").strip()

        if texto == "":
            errores[nombre] = "Este campo es obligatorio."
            continue

        if campo["tipo"] == "binario":
            validas = [str(valor) for valor, _ in campo["opciones"]]
            if texto not in validas:
                errores[nombre] = "Elige una de las opciones de la lista."
            else:
                valores[nombre] = float(texto)
            continue

        numero = leer_numero(texto)
        minimo, maximo = MODELO["rangos"][nombre]
        if numero is None:
            errores[nombre] = "Escribe un número válido (por ejemplo, 25)."
        elif campo.get("entero") and not numero.is_integer():
            errores[nombre] = "Escribe un número entero."
        elif not minimo <= numero <= maximo:
            errores[nombre] = (f"Fuera de rango: escribe un valor entre "
                               f"{minimo:g} y {maximo:g} {campo['unidad']}.")
        else:
            valores[nombre] = numero
    return valores, errores


def calcular(valores):
    """Aplica la fórmula del modelo. Devuelve (estimación, aporte de cada variable)."""
    aportes = []
    total = MODELO["intercepto"]
    for variable in MODELO["variables"]:
        aporte = MODELO["coeficientes"][variable] * valores[variable]
        aportes.append((variable, aporte))
        total += aporte
    return total, aportes


def preparar_resultado(valores):
    """Arma lo que muestra la página: estimación, margen de error y detalle del cálculo."""
    estimacion, aportes = calcular(valores)
    pedidos = max(0.0, estimacion)   # una cantidad negativa de pedidos no tiene sentido
    mae = MODELO["metricas_prueba"]["MAE"]
    etiquetas = {c["nombre"]: c["etiqueta"] for c in CAMPOS}
    filas = [{"etiqueta": f"{etiquetas[v]} ({MODELO['coeficientes'][v]:.4f} × {valores[v]:g})",
              "aporte": f"{a:+.2f} pedidos"} for v, a in aportes]
    return {
        "principal": f"{round(pedidos)} pedidos de kits",
        "margen": (f"Valor sin redondear: {pedidos:.1f} pedidos. Error típico del modelo en los "
                   f"datos de prueba (MAE): ± {mae:.1f} pedidos por semana."),
        "intercepto": f"{MODELO['intercepto']:+.2f} pedidos",
        "aportes": filas,
        "total": f"{estimacion:.2f} pedidos",
    }


@app.route("/", methods=["GET", "POST"])
def inicio():
    # Al abrir la página, los campos binarios empiezan en su primera opción.
    escritos = {c["nombre"]: (str(c["opciones"][0][0]) if c["tipo"] == "binario" else "")
                for c in CAMPOS}
    errores, resultado = {}, None

    # POST significa que la persona pulsó el botón del formulario.
    if request.method == "POST":
        escritos = {c["nombre"]: request.form.get(c["nombre"], "") for c in CAMPOS}
        valores, errores = validar(request.form)
        if not errores:
            resultado = preparar_resultado(valores)

    return render_template("index.html", textos=TEXTOS, campos=CAMPOS, modelo=MODELO,
                           escritos=escritos, errores=errores, resultado=resultado)


if __name__ == "__main__":
    # debug=True solo se usa al practicar en la computadora.
    app.run(debug=True)
