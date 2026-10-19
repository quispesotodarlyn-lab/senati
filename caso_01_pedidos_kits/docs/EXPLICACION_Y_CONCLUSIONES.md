# Sistema de estimación de pedidos de kits de robótica

## Explicación del trabajo (10 líneas)

1. Objetivo: estimar los **pedidos semanales de kits de robótica** (y) con regresión lineal múltiple.
2. Variables X: `consultas_web`, `inversion_publicidad_soles` y `campana_escolar` (0/1); `semana` solo identifica filas.
3. Datos: 110 semanas simuladas, sin valores ausentes ni duplicados, dentro de los rangos del enunciado.
4. Reservé 20 % para prueba (22 filas) y entrené con 80 % (88 filas), con `random_state=42` para repetir el resultado.
5. Entrené `LinearRegression`: pedidos ≈ 1.54 + 0.346·consultas + 0.0067·publicidad + 5.02·campaña.
6. Las consultas pesan más: ~3 consultas más se asocian con ~1 pedido más; S/ 100 de publicidad, con ~0.7 pedidos.
7. En prueba obtuve MAE ≈ 2.95 pedidos (error típico de unos 3 por semana) y R² ≈ 0.79 (explica ~79 % de la variación).
8. Guardé el intercepto y los coeficientes en `modelo.json`; la app Flask los lee y aplica la fórmula sin reentrenar.
9. La web valida rangos (consultas 5–70, publicidad S/ 0–1100, campaña 0/1) y no usa JavaScript.
10. Pruebas: 20 consultas/S/ 200/sin campaña ≈ 10 pedidos; 55 consultas/S/ 800/con campaña ≈ 31 pedidos.

## Respuestas a las preguntas del enunciado

**¿Cuál sería el peligro de usar esta predicción sin verificarla?** El peligro es tratar la estimación como una cifra segura: si se compra inventario o se contrata personal según ella, un error de unos pocos pedidos por semana puede causar faltantes o sobrantes. Además, los datos son simulados y el modelo solo conoce tres factores; no ve la competencia, los feriados, el precio ni el stock.

**Resultados de las pruebas obligatorias**

| Prueba | Entrada | Estimación |
|---|---|---|
| 1 | 20 consultas, S/ 200, sin campaña | **≈ 9.8 → 10 pedidos** |
| 2 | 55 consultas, S/ 800, con campaña | **≈ 31.0 → 31 pedidos** |

**¿Tienen sentido?** Sí. La prueba 2 supera a la 1 por mucho, como se espera con más consultas, más publicidad y campaña. Contra semanas parecidas del CSV: las 5 más cercanas a la prueba 1 tuvieron entre 5 y 13 pedidos (promedio 8.4) y las de la prueba 2, entre 22 y 38 (promedio 30.6). Ambas estimaciones caen dentro de esos rangos y a menos de ~1.5 pedidos del promedio de sus vecinas.

**¿Cuándo podría fallar?** (1) Si se usa fuera de los rangos de entrenamiento (consultas 5–70, publicidad S/ 0–1100): el modelo extrapolaría una línea sin respaldo. (2) Si cambia el contexto (nuevo competidor, feriado, quiebre de stock): el modelo no los conoce. (3) En semanas atípicas: el error individual puede superar con facilidad el MAE de ~3 pedidos. (4) Porque los datos son simulados.

## Conclusiones y límites del modelo

- **Datos simulados:** el modelo refleja el generador de datos, no una tienda real; sirve para practicar, no para decidir inventario.
- **Error típico de ~3 pedidos (≈ 15 %):** en una semana cualquiera la estimación puede fallar por más; conviene comunicarla como rango (p. ej. 10 ± 3).
- **Rangos de validez:** fuera de 5–70 consultas y S/ 0–1100 de publicidad, el modelo extrapolaría sin respaldo; por eso la web lo bloquea.
- **Relación lineal:** supone efectos constantes (cada consulta suma lo mismo). Probé agregar términos cuadráticos e interacciones y no mejoró la validación cruzada (R² 0.78 vs 0.80), así que la línea basta para estos datos.
- **Asociación ≠ causa:** el coeficiente de publicidad no demuestra que gastar más produzca más pedidos.
- **Factores ausentes:** precio, competencia, feriados, stock, calidad de las consultas. Con datos reales habría que reentrenar y validar periódicamente.
