
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

st.set_page_config(page_title="EDA BMI | EDA descriptivo", page_icon="📊", layout="wide")

# ---------------------------------------------------------------------------
# Constantes visuales (colores validados para daltonismo en modo claro y oscuro)
# ---------------------------------------------------------------------------
COLOR_BMI = "#5b6b80"                                         # serie única: BMI total
COLORES_DIA = {"Semana": "#199e70", "Fin de semana": "#7c6ee0"}
ORDEN_DIAS = ["Semana", "Fin de semana"]
ETIQUETAS_FUMADOR = {0: "No fumador", 1: "Fumador"}
COLOR_REFERENCIA = "#898781"                                  # líneas de media/mediana

# ---------------------------------------------------------------------------
# Lectura de datos desde session_state
# ---------------------------------------------------------------------------
if "datos_guardados" not in st.session_state:
    st.warning("⚠️ No hay datos disponibles. Vuelve a **Inicio**, sube el CSV y aplica los filtros.")
    st.page_link("Inicio.py", label="Ir a Inicio", icon="🏠")
    st.stop()

df: pd.DataFrame = st.session_state["datos_guardados"]

st.title("📊 EDA descriptivo del BMI")
st.caption(f"🔎 {st.session_state.get('resumen_filtros', '')}")

if df.empty:
    st.warning("Los filtros actuales no dejan registros. Ajusta los filtros en **Inicio**.")
    st.page_link("Inicio.py", label="Ir a Inicio", icon="🏠")
    st.stop()

# ---------------------------------------------------------------------------
# 1. Estadística descriptiva
# ---------------------------------------------------------------------------
st.header("1 · Estadística descriptiva")

col_tabla, col_comp = st.columns([3, 2])
with col_tabla:
    # describe() solo sobre columnas numéricas (la fecha se resume aparte)
    descriptiva = df.describe(include="number")
    st.dataframe(
        descriptiva.style.format("{:.2f}").format("{:.0f}", subset=pd.IndexSlice[["count"], :])
    )
    st.caption(
        "`smoker` (y `gender`, si existe) son variables 0/1: su media es la proporción de unos. "
        f"Periodo observado: {df['date'].min():%d-%m-%Y} a {df['date'].max():%d-%m-%Y}."
    )

with col_comp:
    # Composición de la muestra: registros por tipo de día y tabaquismo
    composicion = pd.crosstab(
        df["day_type"],
        df["smoker"].map(ETIQUETAS_FUMADOR),
        margins=True,
        margins_name="Total",
    )
    orden_filas = [d for d in ORDEN_DIAS if d in composicion.index] + ["Total"]
    orden_columnas = [c for c in ["No fumador", "Fumador"] if c in composicion.columns] + ["Total"]
    composicion = composicion.reindex(index=orden_filas, columns=orden_columnas)
    composicion.index.name = "Tipo de día"
    composicion.columns.name = None
    st.markdown("**Composición de la muestra (n.º de registros)**")
    st.dataframe(composicion)

# ---------------------------------------------------------------------------
# 2. Distribución del BMI: histograma y boxplot
# ---------------------------------------------------------------------------
st.header("2 · Distribución del BMI")

media, mediana = df["BMI"].mean(), df["BMI"].median()
n_bins = st.slider("Número de intervalos del histograma", min_value=10, max_value=60, value=30, step=5)

col_hist, col_box = st.columns(2)

with col_hist:
    fig_hist = px.histogram(
        df, x="BMI", nbins=n_bins,
        color_discrete_sequence=[COLOR_BMI],
        title="Histograma del BMI (franja gris: rango normal OMS, 18.5–25)",
    )
    # Franja de referencia: rango de BMI "normal" según la OMS (18.5 – 25)
    fig_hist.add_vrect(x0=18.5, x1=25, fillcolor=COLOR_REFERENCIA, opacity=0.12, line_width=0)
    # Media (línea continua) y mediana (línea discontinua). Como suelen estar muy cerca,
    # la etiqueta de la línea que queda a la izquierda se escribe hacia la izquierda y viceversa.
    lado_media = "left" if media >= mediana else "right"
    lado_mediana = "right" if media >= mediana else "left"
    for valor, texto, estilo, lado in [
        (media, f"Media {media:.2f}", "solid", lado_media),
        (mediana, f"Mediana {mediana:.2f}", "dash", lado_mediana),
    ]:
        fig_hist.add_vline(x=valor, line_color=COLOR_REFERENCIA, line_width=2, line_dash=estilo)
        fig_hist.add_annotation(
            x=valor, y=1, yref="paper", yanchor="bottom", xanchor=lado,
            text=f" {texto} ", showarrow=False,
        )
    fig_hist.update_traces(marker_line_width=1, marker_line_color="rgba(255,255,255,0.5)")
    fig_hist.update_layout(bargap=0.05, xaxis_title="BMI (kg/m²)", yaxis_title="Frecuencia")
    st.plotly_chart(fig_hist)

with col_box:
    fig_box = px.box(
        df, x="BMI", points="outliers",
        color_discrete_sequence=[COLOR_BMI],
        hover_data=["age", "hours_wk", "smoker", "day_type"],
        title="Boxplot del BMI",
    )
    fig_box.update_traces(boxmean=True)  # la línea punteada marca la media
    fig_box.update_layout(xaxis_title="BMI (kg/m²)")
    st.plotly_chart(fig_box)

# ---------------------------------------------------------------------------
# 3. Contexto temporal: semana vs. fin de semana
# ---------------------------------------------------------------------------
st.header("3 · Semana vs. fin de semana")

dias_presentes = [d for d in ORDEN_DIAS if d in set(df["day_type"])]

col_comp_box, col_comp_tabla = st.columns([3, 2])

with col_comp_box:
    fig_dia = px.box(
        df, x="day_type", y="BMI", color="day_type", points="outliers",
        category_orders={"day_type": ORDEN_DIAS},
        color_discrete_map=COLORES_DIA,
        hover_data=["age", "hours_wk", "smoker"],
        title="BMI según tipo de día",
    )
    fig_dia.update_traces(boxmean=True)
    fig_dia.update_layout(showlegend=False, xaxis_title="", yaxis_title="BMI (kg/m²)")
    st.plotly_chart(fig_dia)

with col_comp_tabla:
    # Resumen por tipo de día: incluye otras variables para detectar diferencias de composición
    resumen_dia = (
        df.groupby("day_type")
        .agg(
            Registros=("BMI", "size"),
            BMI_medio=("BMI", "mean"),
            BMI_mediana=("BMI", "median"),
            BMI_desv=("BMI", "std"),
            Actividad_media=("hours_wk", "mean"),
            Edad_media=("age", "mean"),
            Pct_fumadores=("smoker", "mean"),
        )
        .reindex(dias_presentes)
    )
    resumen_dia["Pct_fumadores"] *= 100
    resumen_dia = resumen_dia.rename(columns={
        "BMI_medio": "BMI medio", "BMI_mediana": "BMI mediana", "BMI_desv": "BMI desv. est.",
        "Actividad_media": "Actividad (h/sem)", "Edad_media": "Edad media", "Pct_fumadores": "% fumadores",
    })
    resumen_dia.index.name = "Tipo de día"
    st.markdown("**Resumen por tipo de día**")
    st.dataframe(
        resumen_dia.T.style.format("{:.2f}").format("{:.0f}", subset=pd.IndexSlice[["Registros"], :])
    )

# Evolución diaria del BMI promedio, coloreada por tipo de día
diario = (
    df.groupby(["date", "day_type"], as_index=False)
    .agg(BMI=("BMI", "mean"), registros=("BMI", "size"))
    .sort_values("date")
)
fig_tiempo = go.Figure()
fig_tiempo.add_trace(go.Scatter(
    x=diario["date"], y=diario["BMI"], mode="lines",
    line=dict(color=COLOR_REFERENCIA, width=1.5),
    name="Promedio diario", hoverinfo="skip",
))
for dia in dias_presentes:
    sub = diario[diario["day_type"] == dia]
    fig_tiempo.add_trace(go.Scatter(
        x=sub["date"], y=sub["BMI"], mode="markers", name=dia,
        marker=dict(color=COLORES_DIA[dia], size=9, symbol="circle" if dia == "Semana" else "diamond"),
        customdata=sub["registros"],
        hovertemplate="%{x|%d-%m-%Y}<br>BMI promedio: %{y:.2f}<br>Registros: %{customdata}"
                      f"<extra>{dia}</extra>",
    ))
    # Línea horizontal con la media de cada tipo de día
    fig_tiempo.add_hline(
        y=df.loc[df["day_type"] == dia, "BMI"].mean(),
        line_color=COLORES_DIA[dia], line_dash="dot", line_width=2,
    )
fig_tiempo.update_layout(
    title="BMI promedio por día de medición (líneas punteadas: media de cada tipo de día)",
    xaxis_title="Fecha", yaxis_title="BMI promedio",
    legend=dict(orientation="h", yanchor="bottom", y=1.0, xanchor="right", x=1),
)
st.plotly_chart(fig_tiempo)

# ---------------------------------------------------------------------------
# 4. Observaciones (se recalculan con los filtros activos)
# ---------------------------------------------------------------------------
st.header("📝 Observaciones")

# --- Observación 1: forma de la distribución y atípicos
desv = df["BMI"].std()
asimetria = df["BMI"].skew()
if abs(asimetria) < 0.5:
    forma = "aproximadamente simétrica"
else:
    forma = "sesgada a la derecha" if asimetria > 0 else "sesgada a la izquierda"

q1, q3 = df["BMI"].quantile([0.25, 0.75])
iqr = q3 - q1
lim_inf, lim_sup = q1 - 1.5 * iqr, q3 + 1.5 * iqr
atipicos = df[(df["BMI"] < lim_inf) | (df["BMI"] > lim_sup)]
pct_bajo_peso = (df["BMI"] < 18.5).mean() * 100

if atipicos.empty:
    texto_atipicos = "El boxplot **no marca valores atípicos** según la regla de 1.5·IQR."
else:
    texto_atipicos = (
        f"El boxplot marca **{len(atipicos)} valor(es) atípico(s)** (regla 1.5·IQR: fuera de "
        f"[{lim_inf:.1f}, {lim_sup:.1f}]). Corresponden a personas de "
        f"{atipicos['age'].min():.0f}–{atipicos['age'].max():.0f} años, con "
        f"{atipicos['hours_wk'].mean():.1f} h/sem de actividad en promedio y "
        f"{atipicos['smoker'].mean():.0%} de fumadores: son combinaciones extremas de las "
        "variables explicativas, no necesariamente errores de registro."
    )

st.markdown(
    f"**1. Distribución del BMI.** El BMI medio es **{media:.2f}** y la mediana **{mediana:.2f}** "
    f"(desv. estándar {desv:.2f}). Como media y mediana son cercanas y la asimetría es "
    f"{asimetria:.2f}, la distribución es **{forma}**. El centro de la distribución está cerca del "
    f"límite inferior del rango normal de la OMS: el **{pct_bajo_peso:.0f}%** de los registros tiene "
    f"BMI < 18.5. {texto_atipicos}"
)

# --- Observación 2: comparación semana vs. fin de semana
if len(dias_presentes) == 2:
    sem = df[df["day_type"] == "Semana"]
    fin = df[df["day_type"] == "Fin de semana"]
    dif_bmi = fin["BMI"].mean() - sem["BMI"].mean()
    dif_act = fin["hours_wk"].mean() - sem["hours_wk"].mean()
    # ¿La diferencia de actividad "acompaña" a la diferencia de BMI? (más actividad ↔ menor BMI)
    coherente = (dif_bmi < 0 < dif_act) or (dif_act < 0 < dif_bmi)
    texto_explicacion = (
        "Esto es coherente con la relación negativa entre actividad y BMI: la diferencia puede deberse a "
        "**qué personas y conductas se registran** cada tipo de día, y no al tipo de día en sí."
        if coherente else
        "En este subconjunto la actividad física no acompaña la diferencia de BMI, por lo que otras "
        "variables (edad, tabaquismo) podrían explicarla."
    )
    st.markdown(
        f"**2. Semana vs. fin de semana.** El BMI medio es **{sem['BMI'].mean():.2f}** entre semana y "
        f"**{fin['BMI'].mean():.2f}** el fin de semana (una diferencia de {dif_bmi:+.2f} puntos), y las "
        "cajas se solapan casi por completo. Los registros de fin de semana muestran además "
        f"{'más' if dif_act > 0 else 'menos'} actividad física ({fin['hours_wk'].mean():.2f} vs. "
        f"{sem['hours_wk'].mean():.2f} h/sem). {texto_explicacion} Es una **asociación descriptiva, "
        "no evidencia causal**; el fin de semana aporta solo "
        f"{len(fin) / len(df):.0%} de los registros."
    )
else:
    st.markdown(
        "**2. Semana vs. fin de semana.** Con el filtro actual solo hay registros de "
        f"**{dias_presentes[0]}**. Selecciona ambos tipos de día en **Inicio** para compararlos."
    )

# --- Nota de calidad de datos
n_implausibles = int((df["BMI"] < 12).sum())
if n_implausibles:
    st.markdown(
        f"**Nota de calidad de datos.** {n_implausibles} registros tienen BMI < 12, un valor "
        "extremadamente bajo para un adulto (la OMS clasifica < 16 como delgadez severa). No son "
        "atípicos para la regla del IQR, pero sí poco plausibles en la realidad: recuerdan que el "
        "dataset es sintético y conviene tenerlos presentes antes de modelar."
    )
