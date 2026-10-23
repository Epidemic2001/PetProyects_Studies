
import streamlit as st

st.set_page_config(page_title="EDA BMI | Hallazgos", page_icon="💡", layout="wide")

st.title("💡 Hallazgos principales")

st.info(
    "Los hallazgos se redactaron con el **dataset completo** (900 registros medidos entre el "
    "02-03-2026 y el 24-05-2026: 656 de semana y 244 de fin de semana; 31% fumadores). "
    "Las páginas **EDA** y **Relaciones** recalculan las cifras según los filtros activos."
)

# Aviso si hay filtros activos que dejan fuera parte de los datos
if "datos_guardados" in st.session_state and "datos_originales" in st.session_state:
    n_filtrados = len(st.session_state["datos_guardados"])
    n_totales = len(st.session_state["datos_originales"])
    if n_filtrados < n_totales:
        st.caption(
            f"🔎 Tus filtros actuales incluyen {n_filtrados} de {n_totales} registros; "
            "los hallazgos de esta página se refieren al total."
        )

st.markdown(
    "**Pregunta guía:** ¿cómo se relaciona el BMI con la edad, la actividad física y el "
    "tabaquismo, y qué diferencias descriptivas aparecen entre semana y fin de semana?"
)

# ---------------------------------------------------------------------------
# Hallazgos (Observación → Evidencia → Interpretación)
# ---------------------------------------------------------------------------
HALLAZGOS = [
    {
        "titulo": "1 · La actividad física es la variable más asociada al BMI, y de forma casi lineal",
        "observacion": "A más horas de actividad física semanal, menor BMI. La nube de puntos desciende "
                       "de manera pareja, sin curvas marcadas.",
        "evidencia": "r de Pearson = −0.63 y ρ de Spearman = −0.60, la asociación más intensa del conjunto. "
                     "La recta indica ≈ −1.8 puntos de BMI por cada hora semanal adicional; ajustar una "
                     "parábola casi no mejora el ajuste (R² 0.391 → 0.395). En no fumadores, el BMI medio "
                     "baja de forma escalonada de 23.4 (≤ 1 h/sem) a 11.8 (> 6 h/sem).",
        "interpretacion": "La actividad física es la mejor candidata para entrar como término lineal en un "
                          "modelo de regresión. Al ser datos observacionales, describe una asociación: no "
                          "demuestra que aumentar la actividad reduzca el BMI.",
    },
    {
        "titulo": "2 · La edad se asocia positivamente con el BMI, pero la relación es curva",
        "observacion": "El BMI aumenta con la edad, aunque casi no cambia hasta los ~35 años y luego sube "
                       "cada vez más rápido.",
        "evidencia": "r = 0.59 (ρ = 0.57). En no fumadores, el BMI medio por tramo de edad es 15.8 (18–25), "
                     "15.8 (26–35), 17.1 (36–45), 18.8 (46–55) y 22.0 (56–65). El término cuadrático eleva el "
                     "R² de 0.349 a 0.387, y los residuos de una recta dibujan una U: +1.1 en el tramo más "
                     "joven, −0.95 en 36–45 años y +0.9 en el tramo mayor.",
        "interpretacion": "Una recta subestima el BMI en los extremos de edad y lo sobrestima en edades medias. "
                          "Conviene representar la edad con un término cuadrático (age²) o con tramos.",
    },
    {
        "titulo": "3 · El tabaquismo eleva el BMI y cambia la relación con la actividad física",
        "observacion": "Los fumadores tienen un BMI más alto a cualquier edad y nivel de actividad, y la "
                       "actividad física se asocia con una baja menor del BMI en ellos.",
        "evidencia": "BMI medio de 22.26 en fumadores vs. 17.92 en no fumadores (+4.3; ≈ +3.4 al comparar "
                     "personas de igual edad y actividad). Pendiente de la actividad: −1.86 por hora en no "
                     "fumadores vs. −1.17 en fumadores; con más de 6 h/sem el BMI medio es 11.8 vs. 19.6. "
                     "La correlación edad–BMI es mayor en fumadores (0.79 vs. 0.61).",
        "interpretacion": "Hay una **interacción** actividad × tabaquismo: las rectas no son paralelas. Una "
                          "única relación lineal para todos no representa bien los datos; el modelo debería "
                          "permitir pendientes distintas por grupo.",
    },
    {
        "titulo": "4 · La diferencia entre semana y fin de semana es pequeña y descriptiva",
        "observacion": "El fin de semana el BMI medio es levemente menor, pero en esos días también se "
                       "registra más actividad física.",
        "evidencia": "BMI medio de 18.71 el fin de semana vs. 19.45 entre semana (−0.73), con cajas casi "
                     "superpuestas. La actividad es mayor el fin de semana (3.69 vs. 3.08 h/sem), mientras "
                     "que la edad (42.5 vs. 41.2) y el % de fumadores (32% vs. 30%) son similares. Al "
                     "comparar registros de igual edad, actividad y tabaquismo, la diferencia desaparece "
                     "(≈ −0.01). Las correlaciones con el BMI son casi idénticas en ambos tipos de día.",
        "interpretacion": "La diferencia se explica por la composición de los registros (más actividad), no "
                          "por el tipo de día. Es una asociación descriptiva, no un efecto causal del fin de "
                          "semana, y `day_type` no parece necesario en un modelo que ya incluya la actividad.",
    },
    {
        "titulo": "5 · Los valores atípicos siguen las tendencias, pero hay BMI poco plausibles",
        "observacion": "Los BMI más altos corresponden a perfiles extremos coherentes con las tendencias; en el "
                       "otro extremo aparecen valores muy bajos que difícilmente se observarían en la realidad.",
        "evidencia": "5 atípicos según la regla 1.5·IQR (BMI ≥ 29.9): todos fumadores de 63–65 años con "
                     "≤ 1.4 h/sem de actividad. Además, 25 registros tienen BMI < 12 (la OMS considera < 16 "
                     "delgadez severa): todos no fumadores de 18–41 años con 5.1–6.9 h/sem. El BMI tiene "
                     "media 19.25, mediana 19.07 y el 44% de los registros está bajo 18.5.",
        "interpretacion": "Los atípicos no parecen errores y no conviene eliminarlos sin justificación. Los BMI "
                          "< 12 muestran que la tendencia lineal continúa sin un 'piso' fisiológico, lo que "
                          "refleja la naturaleza sintética del dataset y es un límite que tendrá cualquier "
                          "modelo lineal al extrapolar.",
    },
]

st.header("Hallazgos")
for hallazgo in HALLAZGOS:
    with st.expander(f"**{hallazgo['titulo']}**", expanded=True):
        st.markdown(
            f"""
* **Observación:** {hallazgo['observacion']}
* **Evidencia:** {hallazgo['evidencia']}
* **Interpretación:** {hallazgo['interpretacion']}
"""
        )

st.success(
    "**Respuesta a la pregunta guía.** El BMI aumenta con la edad (de forma curva), disminuye con la "
    "actividad física (de forma casi lineal) y es mayor en fumadores, en quienes además la actividad se "
    "asocia con una baja menor del BMI. La diferencia entre semana y fin de semana es pequeña y se explica "
    "por la mayor actividad registrada el fin de semana."
)

# ---------------------------------------------------------------------------
# Conexión con el modelado
# ---------------------------------------------------------------------------
st.header("🔭 Conexión con el modelado")

PREGUNTAS = [
    (
        "¿Qué variable parece tener una relación aproximadamente lineal con el BMI?",
        "**La actividad física (`hours_wk`).** Su nube desciende de forma pareja, el término cuadrático no "
        "mejora el ajuste (R² 0.391 → 0.395) y los promedios del BMI por tramo de horas bajan en escalones "
        "de tamaño similar.",
    ),
    (
        "¿Qué relación presenta mayor evidencia de no linealidad?",
        "**Edad–BMI.** La relación es convexa: casi plana hasta los ~35 años y creciente después. El R² "
        "cuadrático supera claramente al lineal (0.349 → 0.387) y los residuos de la recta forman una U.",
    ),
    (
        "¿El comportamiento es igual para fumadores y no fumadores?",
        "**No.** Los fumadores tienen un BMI más alto a igual edad y actividad (≈ +3.4 puntos) y la pendiente "
        "de la actividad es más suave (−1.17 vs. −1.86 por hora). Con la edad las pendientes son parecidas "
        "(0.18 vs. 0.16 por año), pero la relación es más estrecha en fumadores (r = 0.79 vs. 0.61).",
    ),
    (
        "¿Una matriz de correlación es suficiente para describir todas las relaciones encontradas?",
        "**No.** Pearson resume cada par con un solo número que supone una recta: no muestra la curvatura "
        "de la edad, oculta que la pendiente de la actividad cambia según tabaquismo (−0.63 global vs. −0.70 "
        "y −0.53 por grupo), no incluye el contexto temporal (`day_type`) ni revela atípicos o valores "
        "implausibles. Que Pearson y Spearman se parezcan indica relaciones monótonas, pero no su forma. "
        "Hacen falta los scatterplots y el análisis por grupos.",
    ),
    (
        "¿Qué relación sería interesante modelar posteriormente mediante regresión?",
        "**BMI en función de la actividad física, la edad y el tabaquismo, con interacción actividad × "
        "tabaquismo y un término cuadrático para la edad.** Como referencia (ajuste sobre la misma muestra, "
        "aún sin validar), un modelo lineal simple con las tres variables alcanza R² ≈ 0.91; agregar age² "
        "lo lleva a ≈ 0.96 y la interacción a ≈ 0.97. Habrá que confirmarlo con datos de prueba y revisar "
        "los residuos, en especial en los BMI < 12.",
    ),
]

for numero, (pregunta, respuesta) in enumerate(PREGUNTAS, start=1):
    st.markdown(f"**{numero}. {pregunta}**")
    st.markdown(respuesta)

