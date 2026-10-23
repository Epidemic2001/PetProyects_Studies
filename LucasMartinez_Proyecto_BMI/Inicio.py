
import io

import pandas as pd
import streamlit as st


st.set_page_config(page_title="EDA BMI | Inicio", page_icon="🩺", layout="wide")

COLUMNAS_REQUERIDAS = ["date", "day_type", "age", "hours_wk", "smoker", "BMI"]
ETIQUETAS_FUMADOR = {0: "No fumador", 1: "Fumador"}
ORDEN_DIAS = ["Semana", "Fin de semana"]

# Claves "permanentes" de session_state donde se guardan los filtros elegidos.
FILTROS = ["filtro_dia", "filtro_fumador", "filtro_edad"]



@st.cache_data(show_spinner="Leyendo el archivo...")
def cargar_datos(contenido: bytes) -> tuple[pd.DataFrame, int]:
    df = pd.read_csv(io.BytesIO(contenido))
    df.columns = df.columns.str.strip()

    faltantes = [c for c in COLUMNAS_REQUERIDAS if c not in df.columns]
    if faltantes:
        raise ValueError(f"al archivo le faltan las columnas: {', '.join(faltantes)}")

    # Conversión de tipos (lo que no se pueda convertir queda como NaN)
    df["date"] = pd.to_datetime(df["date"], errors="coerce")
    for col in ["age", "hours_wk", "smoker", "BMI"]:
        df[col] = pd.to_numeric(df[col], errors="coerce")

    n_inicial = len(df)
    df = df.dropna(subset=COLUMNAS_REQUERIDAS).copy()
    df["day_type"] = df["day_type"].astype(str).str.strip()
    df["smoker"] = df["smoker"].astype(int)
    df = df.sort_values("date").reset_index(drop=True)
    return df, n_inicial - len(df)


def reiniciar_filtros() -> None:
    for clave in FILTROS:
        st.session_state.pop(clave, None)


def preparar_filtro(clave: str, por_defecto) -> None:
    if clave not in st.session_state:
        st.session_state[clave] = por_defecto
    st.session_state[f"_{clave}"] = st.session_state[clave]


def guardar_filtro(clave: str) -> None:
    st.session_state[clave] = st.session_state[f"_{clave}"]


def delta_vs_total(valor: float, total: float):
    diferencia = valor - total
    return None if abs(diferencia) < 0.005 else f"{diferencia:+.2f} vs. total"


# ---------------------------------------------------------------------------
# Encabezado
# ---------------------------------------------------------------------------
st.title("🩺 EDA interactivo del Índice de Masa Corporal (BMI)")
st.markdown(
    "**Pregunta guía:** ¿cómo se relaciona el BMI con la **edad**, la **actividad física** "
    "y el **tabaquismo**, y qué diferencias descriptivas aparecen entre **semana y fin de semana**?"
)

# ---------------------------------------------------------------------------
# 1. Carga del archivo
# ---------------------------------------------------------------------------
archivo = st.file_uploader(
    "Sube el archivo CSV con los datos",
    type=["csv"],
    help="Columnas esperadas: " + ", ".join(COLUMNAS_REQUERIDAS),
)

if archivo is not None:
    try:
        df_original, n_descartadas = cargar_datos(archivo.getvalue())
    except Exception as error:  # CSV mal formado, columnas faltantes, codificación, etc.
        st.error(f"No se pudo leer el archivo: {error}")
        st.stop()

    # Si se sube un archivo distinto al anterior, los filtros vuelven a su valor por defecto
    id_archivo = f"{archivo.name}-{archivo.size}"
    if st.session_state.get("id_archivo") != id_archivo:
        reiniciar_filtros()
    st.session_state["id_archivo"] = id_archivo
    st.session_state["nombre_archivo"] = archivo.name
    st.session_state["datos_originales"] = df_original

    if n_descartadas:
        st.caption(f"⚠️ Se descartaron {n_descartadas} filas con valores faltantes o no válidos.")

elif "datos_originales" in st.session_state:
    # Al volver desde otra página el file_uploader aparece vacío, pero los datos
    # siguen en session_state: se reutilizan para no obligar a subirlos otra vez.
    df_original = st.session_state["datos_originales"]
    col_info, col_boton = st.columns([5, 1], vertical_alignment="center")
    col_info.info(
        f"Trabajando con **{st.session_state['nombre_archivo']}**, cargado anteriormente. "
        "Puedes subir otro archivo para reemplazarlo."
    )
    if col_boton.button("Descartar datos"):
        for clave in ["datos_originales", "datos_guardados", "nombre_archivo",
                      "id_archivo", "resumen_filtros", *FILTROS]:
            st.session_state.pop(clave, None)
        st.rerun()

else:
    st.warning(
        "👋 **Aún no hay datos para analizar.** Sube el archivo CSV (por ejemplo, `datos.csv`) "
        "para habilitar los filtros, los indicadores y las páginas de análisis."
    )
    st.stop()  # Nada de lo que sigue se ejecuta sin datos

# ---------------------------------------------------------------------------
# 2. Filtros en la barra lateral
# ---------------------------------------------------------------------------
st.sidebar.header("🎛️ Filtros")

tipos_dia = set(df_original["day_type"])
opciones_dia = [d for d in ORDEN_DIAS if d in tipos_dia] + sorted(tipos_dia - set(ORDEN_DIAS))
opciones_fumador = sorted(df_original["smoker"].unique().tolist())
edad_min, edad_max = int(df_original["age"].min()), int(df_original["age"].max())

# a) Tipo de día
preparar_filtro("filtro_dia", opciones_dia)
dias = st.sidebar.multiselect(
    "Tipo de día",
    options=opciones_dia,
    key="_filtro_dia",
    on_change=guardar_filtro,
    args=("filtro_dia",),
)

# b) Condición de tabaquismo
preparar_filtro("filtro_fumador", opciones_fumador)
fumador = st.sidebar.multiselect(
    "Condición de tabaquismo",
    options=opciones_fumador,
    format_func=lambda v: ETIQUETAS_FUMADOR.get(v, str(v)),
    key="_filtro_fumador",
    on_change=guardar_filtro,
    args=("filtro_fumador",),
)

# c) Rango de edad
preparar_filtro("filtro_edad", (edad_min, edad_max))
edad = st.sidebar.slider(
    "Rango de edad (años)",
    min_value=edad_min,
    max_value=edad_max,
    key="_filtro_edad",
    on_change=guardar_filtro,
    args=("filtro_edad",),
)

st.sidebar.button("↺ Restablecer filtros", on_click=reiniciar_filtros)

# ---------------------------------------------------------------------------
# 3. Aplicación de filtros y guardado en session_state
# ---------------------------------------------------------------------------
df_filtrado = df_original[
    df_original["day_type"].isin(dias)
    & df_original["smoker"].isin(fumador)
    & df_original["age"].between(edad[0], edad[1])
].reset_index(drop=True)

# Punto clave del flujo entre páginas: las páginas de pages/ leen esta clave.
st.session_state["datos_guardados"] = df_filtrado

# Texto breve con los filtros activos, para mostrarlo en las demás páginas
texto_dias = ", ".join(dias) or "ninguno"
texto_fumador = ", ".join(ETIQUETAS_FUMADOR.get(v, str(v)) for v in fumador) or "ninguno"
st.session_state["resumen_filtros"] = (
    f"{len(df_filtrado)} de {len(df_original)} registros · Día: {texto_dias} · "
    f"Tabaquismo: {texto_fumador} · Edad: {edad[0]}–{edad[1]} años"
)
st.sidebar.caption(f"**{len(df_filtrado)}** de {len(df_original)} registros cumplen los filtros.")

# ---------------------------------------------------------------------------
# 4. Indicadores clave
# ---------------------------------------------------------------------------
st.subheader("Indicadores del subconjunto filtrado")

if df_filtrado.empty:
    st.warning("Ningún registro cumple los filtros actuales. Amplía la selección en la barra lateral.")
    st.stop()

bmi_prom, bmi_total = df_filtrado["BMI"].mean(), df_original["BMI"].mean()
act_prom, act_total = df_filtrado["hours_wk"].mean(), df_original["hours_wk"].mean()


col1, col2, col3 = st.columns(3)
col1.metric(
    "Registros filtrados",
    f"{len(df_filtrado):,}".replace(",", "."),
    help=f"De un total de {len(df_original)} registros en el archivo.",
)
col2.metric(
    "BMI promedio",
    f"{bmi_prom:.2f}",
    delta=delta_vs_total(bmi_prom, bmi_total),
    delta_color="off",
    help="Índice de Masa Corporal promedio (kg/m²) del subconjunto filtrado.",
)
col3.metric(
    "Actividad física promedio",
    f"{act_prom:.2f} h/sem",
    delta=delta_vs_total(act_prom, act_total),
    delta_color="off",
    help="Horas de actividad física por semana (hours_wk).",
)
st.caption("Cuando hay filtros activos, el valor bajo cada indicador lo compara con el total del archivo.")

# ---------------------------------------------------------------------------
# 5. Vista previa, diccionario de variables y navegación
# ---------------------------------------------------------------------------
with st.expander("👀 Vista previa de los datos filtrados"):
    st.dataframe(
        df_filtrado,
        hide_index=True,
        column_config={"date": st.column_config.DateColumn("date", format="DD/MM/YYYY")},
    )

with st.expander("📖 Diccionario de variables"):
    st.markdown(
        """
| Variable | Descripción |
|---|---|
| `age` | Edad de la persona (años) |
| `hours_wk` | Horas de actividad física por semana |
| `smoker` | Tabaquismo: 0 = no fumador, 1 = fumador |
| `BMI` | Índice de Masa Corporal (variable objetivo) |
| `date` | Fecha de medición |
| `day_type` | Semana / Fin de semana |
"""
    )

st.markdown("#### Continúa el análisis")
nav1, nav2, nav3 = st.columns(3)
with nav1:
    st.page_link("pages/1_EDA.py", label="EDA descriptivo", icon="📊")
with nav2:
    st.page_link("pages/2_Relaciones.py", label="Relaciones entre variables", icon="🔗")
with nav3:
    st.page_link("pages/3_Hallazgos.py", label="Hallazgos principales", icon="💡")
