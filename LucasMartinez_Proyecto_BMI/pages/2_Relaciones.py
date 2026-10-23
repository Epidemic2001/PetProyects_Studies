
import numpy as np
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

st.set_page_config(page_title="EDA BMI | Relaciones", page_icon="🔗", layout="wide")

# ---------------------------------------------------------------------------
# Constantes (colores validados para daltonismo; la forma del marcador refuerza el color)
# ---------------------------------------------------------------------------
ETIQUETAS_FUMADOR = {0: "No fumador", 1: "Fumador"}
ORDEN_FUMADOR = ["No fumador", "Fumador"]
COLORES_FUMADOR = {"No fumador": "#2a78d6", "Fumador": "#d95926"}
SIMBOLOS_FUMADOR = {"No fumador": "circle", "Fumador": "diamond"}
VARIABLES_CORR = ["age", "hours_wk", "smoker", "BMI"]
NOMBRES = {"age": "Edad (años)", "hours_wk": "Actividad física (h/semana)", "BMI": "BMI (kg/m²)"}
# Escala divergente azul–gris–rojo: el gris neutro marca correlación 0
ESCALA_DIVERGENTE = [
    [0.00, "#3987e5"], [0.25, "#9ec5f4"], [0.50, "#f0efec"], [0.75, "#f2a19f"], [1.00, "#e34948"],
]


# ---------------------------------------------------------------------------
# Funciones auxiliares
# ---------------------------------------------------------------------------
def se_puede_ajustar(x: pd.Series, grado: int) -> bool:
    """Un polinomio de grado g necesita más de g valores distintos de x."""
    return len(x) > grado + 1 and x.nunique() > grado


def r2_polinomio(x: pd.Series, y: pd.Series, grado: int) -> float:
    """R² de un ajuste polinomial por mínimos cuadrados (1 = lineal, 2 = cuadrático)."""
    if not se_puede_ajustar(x, grado):
        return np.nan
    pred = np.polyval(np.polyfit(x, y, grado), x)
    ss_tot = ((y - y.mean()) ** 2).sum()
    return 1 - ((y - pred) ** 2).sum() / ss_tot if ss_tot > 0 else np.nan


def pendiente(x: pd.Series, y: pd.Series) -> float:
    """Pendiente de la recta de mínimos cuadrados (cambio de BMI por unidad de x)."""
    return np.polyfit(x, y, 1)[0] if se_puede_ajustar(x, 1) else np.nan


def intensidad(r: float) -> str:
    """Traduce |r| a una etiqueta cualitativa aproximada."""
    a = abs(r)
    if np.isnan(a):
        return "no calculable"
    if a < 0.1:
        return "prácticamente nula"
    if a < 0.3:
        return "débil"
    if a < 0.5:
        return "moderada"
    if a < 0.7:
        return "moderada a fuerte"
    return "fuerte"


def resumen_relacion(datos: pd.DataFrame, x: str) -> dict:
    """Calcula la evidencia numérica de la relación x → BMI."""
    res = {
        "r de Pearson": datos[x].corr(datos["BMI"]),
        "ρ de Spearman": datos[x].corr(datos["BMI"], method="spearman"),
        "R² lineal": r2_polinomio(datos[x], datos["BMI"], 1),
        "R² cuadrático": r2_polinomio(datos[x], datos["BMI"], 2),
    }
    for grupo in ORDEN_FUMADOR:
        sub = datos[datos["Tabaquismo"] == grupo]
        res[f"r {grupo}"] = sub[x].corr(sub["BMI"]) if len(sub) > 2 else np.nan
        res[f"Pendiente {grupo}"] = pendiente(sub[x], sub["BMI"])
    return res


def grafico_dispersion(datos: pd.DataFrame, x: str, grado: int) -> go.Figure:
    """Scatterplot x vs. BMI con color y forma según tabaquismo.

    grado: 0 = sin tendencia, 1 = recta, 2 = parábola (ajustadas por grupo).
    """
    fig = px.scatter(
        datos, x=x, y="BMI",
        color="Tabaquismo", symbol="Tabaquismo",
        color_discrete_map=COLORES_FUMADOR, symbol_map=SIMBOLOS_FUMADOR,
        category_orders={"Tabaquismo": ORDEN_FUMADOR},
        opacity=0.7,
        hover_data=["age", "hours_wk", "day_type"],
        labels=NOMBRES,
        title=f"{NOMBRES[x]} vs. BMI",
    )
    fig.update_traces(marker=dict(size=8, line=dict(width=0.5, color="rgba(255,255,255,0.7)")))

    if grado:  # líneas de tendencia por grupo (lineal o cuadrática)
        tipo = "lineal" if grado == 1 else "cuadrática"
        for grupo in ORDEN_FUMADOR:
            sub = datos[datos["Tabaquismo"] == grupo]
            if not se_puede_ajustar(sub[x], grado):
                continue
            coef = np.polyfit(sub[x], sub["BMI"], grado)
            xs = np.linspace(sub[x].min(), sub[x].max(), 100)
            fig.add_trace(go.Scatter(
                x=xs, y=np.polyval(coef, xs), mode="lines",
                line=dict(color=COLORES_FUMADOR[grupo], width=3),
                name=f"Tendencia {tipo} · {grupo}",
                hoverinfo="skip",
            ))

    fig.update_layout(legend=dict(orientation="h", yanchor="top", y=-0.2, x=0, title_text=""))
    return fig


def texto_no_linealidad(datos: pd.DataFrame, x: str, ev: dict) -> str:
    """Describe la curvatura comparando el ajuste cuadrático con el lineal."""
    ganancia = ev["R² cuadrático"] - ev["R² lineal"]
    if np.isnan(ganancia):
        return "No hay suficientes valores distintos para evaluar la curvatura."
    if ganancia > 0.02:
        curvatura = np.polyfit(datos[x], datos["BMI"], 2)[0]
        sentido = "hacia arriba (convexa)" if curvatura > 0 else "hacia abajo (cóncava)"
        return (
            f"**hay evidencia de curvatura**: el R² sube de {ev['R² lineal']:.3f} (recta) a "
            f"{ev['R² cuadrático']:.3f} (parábola) y la nube se curva {sentido}."
        )
    return (
        f"la relación es **aproximadamente lineal**: la parábola apenas mejora a la recta "
        f"(R² {ev['R² lineal']:.3f} → {ev['R² cuadrático']:.3f})."
    )


def texto_grupos(ev: dict, unidad: str, n_grupos: int) -> str:
    """Compara las pendientes de fumadores y no fumadores."""
    if n_grupos < 2:
        return "Con el filtro actual hay un solo grupo de tabaquismo, así que no se pueden comparar."
    p_no, p_si = ev["Pendiente No fumador"], ev["Pendiente Fumador"]
    if abs(p_no - p_si) > 0.3 * max(abs(p_no), abs(p_si)):
        return (
            f"Las pendientes difieren entre grupos ({p_no:+.2f} en no fumadores vs. {p_si:+.2f} en "
            f"fumadores por {unidad}): las rectas **no son paralelas**, lo que sugiere una interacción con el tabaquismo."
        )
    return (
        f"Las pendientes son parecidas ({p_no:+.2f} vs. {p_si:+.2f} por {unidad}): las rectas son casi "
        "paralelas y el tabaquismo desplaza el nivel del BMI más que la forma de la relación."
    )


# ---------------------------------------------------------------------------
# Lectura de datos desde session_state
# ---------------------------------------------------------------------------
if "datos_guardados" not in st.session_state:
    st.warning("⚠️ No hay datos disponibles. Vuelve a **Inicio**, sube el CSV y aplica los filtros.")
    st.page_link("Inicio.py", label="Ir a Inicio", icon="🏠")
    st.stop()

df: pd.DataFrame = st.session_state["datos_guardados"]

st.title("🔗 Relaciones entre variables")
st.caption(f"🔎 {st.session_state.get('resumen_filtros', '')}")

if len(df) < 5:
    st.warning("Se necesitan al menos 5 registros para estudiar relaciones. Amplía los filtros en **Inicio**.")
    st.page_link("Inicio.py", label="Ir a Inicio", icon="🏠")
    st.stop()

# Columna con etiquetas legibles para la leyenda (no modifica el DataFrame guardado)
datos = df.assign(Tabaquismo=df["smoker"].map(ETIQUETAS_FUMADOR))
grupos_presentes = [g for g in ORDEN_FUMADOR if g in set(datos["Tabaquismo"])]

# ---------------------------------------------------------------------------
# 1. Scatterplots
# ---------------------------------------------------------------------------
st.header("1 · Diagramas de dispersión")

opcion_tendencia = st.radio(
    "Línea de tendencia por grupo de tabaquismo",
    ["Ninguna", "Lineal", "Cuadrática"],
    index=1,
    horizontal=True,
    help="Compara la recta con la curva: si la cuadrática se aparta claramente, hay no linealidad.",
)
grado = {"Ninguna": 0, "Lineal": 1, "Cuadrática": 2}[opcion_tendencia]

ev_edad = resumen_relacion(datos, "age")
ev_act = resumen_relacion(datos, "hours_wk")

col_edad, col_act = st.columns(2)
with col_edad:
    st.plotly_chart(grafico_dispersion(datos, "age", grado))
    st.caption(f"r de Pearson = {ev_edad['r de Pearson']:.2f} · ρ de Spearman = {ev_edad['ρ de Spearman']:.2f}")
with col_act:
    st.plotly_chart(grafico_dispersion(datos, "hours_wk", grado))
    st.caption(f"r de Pearson = {ev_act['r de Pearson']:.2f} · ρ de Spearman = {ev_act['ρ de Spearman']:.2f}")

# ---------------------------------------------------------------------------
# 2. Tabla de evidencia numérica
# ---------------------------------------------------------------------------
st.header("2 · Evidencia numérica")
evidencia = pd.DataFrame({"Edad → BMI": ev_edad, "Actividad física → BMI": ev_act})
orden_filas = ["r de Pearson", "ρ de Spearman", "r No fumador", "r Fumador",
               "R² lineal", "R² cuadrático", "Pendiente No fumador", "Pendiente Fumador"]
col_tabla, col_nota = st.columns([3, 2])
# Las filas de un grupo ausente (p. ej., si se filtró solo un grupo) quedan vacías y se omiten
evidencia = evidencia.reindex(orden_filas).dropna(how="all")
col_tabla.dataframe(evidencia.style.format("{:.3f}"))
col_nota.caption(
    "Si el R² cuadrático supera claramente al lineal, la relación tiene curvatura. "
    "Pendientes distintas entre grupos indican que el efecto depende del tabaquismo (interacción). "
    "Pendiente = cambio promedio del BMI por cada año (edad) o por cada hora semanal (actividad)."
)

# ---------------------------------------------------------------------------
# 3. Matriz de correlaciones
# ---------------------------------------------------------------------------
st.header("3 · Matriz de correlaciones")

col_mapa, col_guia = st.columns([3, 2])
with col_guia:
    metodo = st.radio(
        "Coeficiente",
        ["Pearson", "Spearman"],
        horizontal=True,
        help="Pearson mide asociación lineal; Spearman, asociación monótona (basada en rangos).",
    )
    st.markdown(
        """
**Cómo leerla**
- Rojo: asociación positiva · Azul: negativa · Gris: cercana a 0.
- `smoker` es binaria: su correlación con el BMI equivale a una diferencia de medias estandarizada (punto-biserial).
- Si Pearson y Spearman son parecidos, la relación es **monótona**, pero eso no dice si es **recta o curva**.
"""
    )

with col_mapa:
    # Si un filtro deja una variable constante (p. ej., solo fumadores), su correlación no existe
    variables = [v for v in VARIABLES_CORR if datos[v].nunique() > 1]
    matriz = datos[variables].corr(method=metodo.lower())
    fig_corr = px.imshow(
        matriz, text_auto=".2f", zmin=-1, zmax=1,
        color_continuous_scale=ESCALA_DIVERGENTE,
        title=f"Correlación de {metodo} — variables numéricas principales",
    )
    fig_corr.update_traces(textfont=dict(color="#0b0b0b", size=14))
    fig_corr.update_layout(coloraxis_colorbar=dict(title="r"))
    st.plotly_chart(fig_corr)
    excluidas = sorted(set(VARIABLES_CORR) - set(variables))
    if excluidas:
        st.caption(f"Se omiten {', '.join(excluidas)} porque son constantes con los filtros actuales.")

# ---------------------------------------------------------------------------
# 4. Discusión (los números se recalculan con los filtros activos)
# ---------------------------------------------------------------------------
st.header("📝 Discusión de las relaciones")

# Valores atípicos del BMI (regla 1.5·IQR) y datos poco plausibles
q1, q3 = datos["BMI"].quantile([0.25, 0.75])
lim_sup = q3 + 1.5 * (q3 - q1)
lim_inf = q1 - 1.5 * (q3 - q1)
atipicos = datos[(datos["BMI"] > lim_sup) | (datos["BMI"] < lim_inf)]
bajos = datos[datos["BMI"] < 12]
ceros_act = int((datos["hours_wk"] == 0).sum())

# ¿Los atípicos siguen la tendencia general? Se comparan con una regresión lineal múltiple
# (edad + actividad + tabaquismo) mediante sus residuos estandarizados.
explicativas = [c for c in ["age", "hours_wk", "smoker"] if datos[c].nunique() > 1]
X = np.column_stack([np.ones(len(datos))] + [datos[c].to_numpy(float) for c in explicativas])
coeficientes, *_ = np.linalg.lstsq(X, datos["BMI"].to_numpy(float), rcond=None)
residuos = datos["BMI"].to_numpy(float) - X @ coeficientes
residuos_z = pd.Series(residuos / (residuos.std() or 1.0), index=datos.index)
nombres_modelo = {"age": "edad", "hours_wk": "actividad", "smoker": "tabaquismo"}
texto_modelo = " + ".join(nombres_modelo[c] for c in explicativas)

if atipicos.empty:
    texto_atip_edad = "No hay BMI atípicos según la regla 1.5·IQR en este subconjunto."
else:
    n_sup = int((atipicos["BMI"] > lim_sup).sum())
    z_max = residuos_z.loc[atipicos.index].abs().max()
    texto_atip_edad = (
        f"Hay {len(atipicos)} BMI atípicos según la regla 1.5·IQR ({n_sup} sobre {lim_sup:.1f} y "
        f"{len(atipicos) - n_sup} bajo {lim_inf:.1f}): personas de "
        f"{atipicos['age'].min():.0f}–{atipicos['age'].max():.0f} años, "
        f"{atipicos['smoker'].mean():.0%} fumadoras, con {atipicos['hours_wk'].mean():.1f} h/sem de "
        "actividad en promedio. "
        + (
            f"Frente a una regresión lineal ({texto_modelo}) sus residuos son moderados "
            f"(|z| ≤ {z_max:.1f}): siguen la tendencia general, así que parecen casos extremos y no errores."
            if z_max < 3 else
            f"Algunos se alejan de lo que predice una regresión lineal ({texto_modelo}) "
            f"(|z| hasta {z_max:.1f}): conviene revisarlos antes de modelar."
        )
    )

if bajos.empty:
    texto_atip_act = "No se observan BMI extremadamente bajos (< 12) en este subconjunto."
else:
    texto_atip_act = (
        f"En el extremo derecho hay {len(bajos)} registros con BMI < 12 (valores poco plausibles), "
        f"todos con {bajos['hours_wk'].min():.1f}–{bajos['hours_wk'].max():.1f} h/sem: la recta sigue "
        "bajando sin un 'piso' fisiológico, algo que un modelo lineal extrapolaría sin advertirlo."
    )
if ceros_act:
    texto_atip_act += f" Además, {ceros_act} registros tienen 0 h/sem (posible valor mínimo de la escala)."

st.subheader("Edad y BMI")
st.markdown(
    f"""
- **Dirección:** {'positiva' if ev_edad['r de Pearson'] > 0 else 'negativa'} — a mayor edad, {'mayor' if ev_edad['r de Pearson'] > 0 else 'menor'} BMI en promedio.
- **Intensidad aproximada:** {intensidad(ev_edad['r de Pearson'])} (r = {ev_edad['r de Pearson']:.2f}; ρ = {ev_edad['ρ de Spearman']:.2f}).
- **No linealidad:** {texto_no_linealidad(datos, 'age', ev_edad)} {texto_grupos(ev_edad, 'año', len(grupos_presentes))}
- **Valores atípicos:** {texto_atip_edad}
"""
)

st.subheader("Actividad física y BMI")
st.markdown(
    f"""
- **Dirección:** {'negativa' if ev_act['r de Pearson'] < 0 else 'positiva'} — a más horas de actividad, {'menor' if ev_act['r de Pearson'] < 0 else 'mayor'} BMI en promedio.
- **Intensidad aproximada:** {intensidad(ev_act['r de Pearson'])} (r = {ev_act['r de Pearson']:.2f}; ρ = {ev_act['ρ de Spearman']:.2f}).
- **No linealidad:** {texto_no_linealidad(datos, 'hours_wk', ev_act)} {texto_grupos(ev_act, 'hora semanal', len(grupos_presentes))}
- **Valores atípicos:** {texto_atip_act}
"""
)

st.subheader("Tabaquismo y BMI")
if len(grupos_presentes) == 2:
    medias = datos.groupby("Tabaquismo")["BMI"].mean()
    r_pb = datos["smoker"].corr(datos["BMI"])            # correlación punto-biserial (Pearson)
    r_smoker_act = datos["smoker"].corr(datos["hours_wk"])
    p_no, p_si = ev_act["Pendiente No fumador"], ev_act["Pendiente Fumador"]
    if abs(p_no - p_si) > 0.3 * max(abs(p_no), abs(p_si)):
        texto_forma = (
            f"en actividad física, además, la pendiente cambia ({p_no:+.2f} vs. {p_si:+.2f} por hora), "
            "así que el tabaquismo **modifica** la relación y no solo el nivel del BMI."
        )
    else:
        texto_forma = "las pendientes son similares, así que el tabaquismo desplaza sobre todo el **nivel** del BMI."
    st.markdown(
        f"""
- **Dirección:** los fumadores tienen un BMI medio **{'mayor' if medias['Fumador'] > medias['No fumador'] else 'menor'}** ({medias['Fumador']:.2f} vs. {medias['No fumador']:.2f}; diferencia {medias['Fumador'] - medias['No fumador']:+.2f}).
- **Intensidad aproximada:** {intensidad(r_pb)} (correlación punto-biserial = {r_pb:.2f}).
- **Forma:** en ambos scatterplots la nube de fumadores está desplazada respecto de la de no fumadores; {texto_forma}
- **Precaución:** la correlación entre `smoker` y `hours_wk` es {r_smoker_act:.2f}; si los grupos difieren en actividad, parte de la diferencia de BMI podría deberse a ella y no al tabaquismo en sí.
"""
    )
else:
    st.markdown("Con el filtro actual hay un solo grupo de tabaquismo. Selecciona ambos en **Inicio** para compararlos.")
