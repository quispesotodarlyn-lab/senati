# SENATI · Taller de Regresión con Machine Learning — Casos prácticos intermedios

Dos proyectos independientes de **regresión lineal múltiple** (scikit-learn) con una aplicación web en
**Flask + HTML + CSS** (sin JavaScript). Cada carpeta se ejecuta por separado.

| Caso | Qué estima | Variables X | MAE | R² |
|---|---|---|---|---|
| [Caso 01 · Pedidos de kits de robótica](caso_01_pedidos_kits/) | pedidos semanales | consultas web, inversión en publicidad, campaña escolar (0/1) | 2.95 pedidos | 0.791 |
| [Caso 02 · Transporte agrícola](caso_02_transporte_agricola/) | costo del viaje (S/) | distancia, carga, vía no asfaltada (0/1) | S/ 17.79 | 0.977 |

Cada caso contiene: datos, cuaderno ejecutado, script de entrenamiento, `modelo.json`, app Flask,
pruebas automáticas, capturas y documentación (ver el `README.md` de cada carpeta).

> **Aviso:** todos los datos son simulados y las estimaciones son de práctica; no sirven para cotizar ni decidir compras.

## Inicio rápido

```bash
cd caso_01_pedidos_kits          # o caso_02_transporte_agricola
pip install -r requirements.txt
python app.py                    # http://127.0.0.1:5000
```

*Instructor: Ing. Gunar Castro Iñigo · SENATI, Escuela de Tecnologías de la Información.*
