# CASO PRÁCTICO INTERMEDIO 1 — SENATI

**Sistema de estimación de pedidos de kits de robótica**

Una tienda educativa quiere anticipar pedidos semanales. El número de consultas y la inversión publicitaria pueden asociarse con más ventas; el indicador de campaña escolar toma 0 o 1.

**Datos:** `datos.csv`. Son **simulados**, no registros reales.

## Trabajo que realizará el estudiante
1. Abrir el CSV e identificar las variables X: consultas_web, inversion_publicidad_soles, campana_escolar; y: pedidos_kits.
2. Explorar datos, verificar ausentes y separar 80% entrenamiento / 20% prueba.
3. Entrenar `LinearRegression` y mostrar los coeficientes con explicación.
4. Calcular MAE y R² sobre prueba, y comentar qué significan en las unidades del problema.
5. Crear `app.py`, `templates/index.html` y `static/estilos.css` con **Python, Flask, HTML y CSS solamente**.
6. Guardar los coeficientes en `modelo.json`; mostrar la predicción en la página después de pulsar un botón.
7. Validar rangos: consultas de 5 a 70, publicidad de S/ 0 a S/ 1100, campaña 0/1.
8. Hacer mínimo dos pruebas: Semana con 20 consultas, S/ 200 y sin campaña; Semana con 55 consultas, S/ 800 y con campaña.
9. Entregar capturas, CSV, código comentado, una explicación de 10 líneas y conclusiones sobre límites del modelo.

## Rúbrica (20 puntos)
- Lectura y limpieza del CSV (3)
- Variables elegidas, ajuste y separación train/test (5)
- Interpretación de MAE y R² (4)
- Interfaz Flask usable sin JavaScript (5)
- Pruebas, comentarios y documentación (3)

**No se entrega una solución final de estos retos:** están diseñados para evaluar lo aprendido en los cuatro proyectos resueltos.
