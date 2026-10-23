# PetProyects_Studies

Repositorio personal donde reúno mis **pet projects** (proyectos personales) y mis **estudios en el área de datos**: análisis exploratorio, preparación y limpieza de datos, *machine learning* y *deep learning*.

Cada proyecto es un ejercicio práctico con el que voy aprendiendo y consolidando conceptos. Por eso los notebooks incluyen explicaciones paso a paso, decisiones justificadas y preguntas de análisis, además del código.

---

## Estructura

Los notebooks están organizados en carpetas según su temática:

```
PetProyects_Studies/
├── 01_Preparacion_de_Datos/      # Extracción, limpieza y preparación de datos
│   ├── T2_LucasMartínez/
│   └── T3_Limpieza_Datos_Lucas_Martinez(1).ipynb
├── 02_Machine_Learning/          # Modelos supervisados
│   ├── Taller_Modelado_Entrega_Lucas_Martinez.ipynb
│   └── Ensemble_Learning/        # Bagging, Boosting y Stacking
├── 03_Deep_Learning/             # Redes neuronales con TensorFlow / Keras
└── Proyectos/                    # Proyectos completos (apps, dashboards)
    └── LucasMartinez_Proyecto_BMI/
```

---

## Contenido

### 📁 01 · Preparación de datos

Carpeta: [`01_Preparacion_de_Datos/`](01_Preparacion_de_Datos/)

| Notebook | Descripción | Herramientas |
|---|---|---|
| [`T2_LucasMartínez.ipynb`](01_Preparacion_de_Datos/T2_LucasMart%C3%ADnez/T2_LucasMart%C3%ADnez.ipynb) | Extracción multifuente: consultas SQL sobre SQLite, enriquecimiento con la API del Banco Mundial y desidentificación de clientes. Genera `dataset_final.csv`. | SQLite, SQL, requests, pandas, hashlib |
| [`T3_Limpieza_Datos_Lucas_Martinez(1).ipynb`](01_Preparacion_de_Datos/T3_Limpieza_Datos_Lucas_Martinez%281%29.ipynb) | Auditoría de calidad, sanitización de tipos, nulos, duplicados y outliers, indicadores de negocio, *encoding* y escalado sin *data leakage*. | pandas, NumPy, scikit-learn |

### 📁 02 · Machine Learning supervisado

Carpeta: [`02_Machine_Learning/`](02_Machine_Learning/)

| Notebook | Descripción | Herramientas |
|---|---|---|
| [`Taller_Modelado_Entrega_Lucas_Martinez.ipynb`](02_Machine_Learning/Taller_Modelado_Entrega_Lucas_Martinez.ipynb) | Comparación de modelos de **regresión** (demanda de bicicletas) y **clasificación** (entregas tardías): métricas, diagnóstico gráfico, matriz de confusión, curvas y efecto del umbral. | scikit-learn, XGBoost, CatBoost |

**Ensemble Learning** — [`02_Machine_Learning/Ensemble_Learning/`](02_Machine_Learning/Ensemble_Learning/) (dataset Breast Cancer Wisconsin)

| Notebook | Descripción | Herramientas |
|---|---|---|
| [`01_Bagging.ipynb`](02_Machine_Learning/Ensemble_Learning/01_Bagging.ipynb) | Árbol de decisión baseline frente a Bagging, bootstrap y efecto del número de estimadores. | scikit-learn |
| [`02_Boosting.ipynb`](02_Machine_Learning/Ensemble_Learning/02_Boosting.ipynb) | AdaBoost y Gradient Boosting: evolución del aprendizaje, *learning rate* y comparación ROC. | scikit-learn |
| [`03_Stacking.ipynb`](02_Machine_Learning/Ensemble_Learning/03_Stacking.ipynb) | Stacking con regresión logística, KNN y SVM como modelos base y regresión logística como meta-modelo; análisis de errores y curvas ROC. | scikit-learn |

### 📁 03 · Deep Learning

Carpeta: [`03_Deep_Learning/`](03_Deep_Learning/)

| Notebook | Descripción | Herramientas |
|---|---|---|
| [`01_Aprendizaje_Autosupervisado_MNIST_EXPLICADO.ipynb`](03_Deep_Learning/01_Aprendizaje_Autosupervisado_MNIST_EXPLICADO.ipynb) | Aprendizaje autosupervisado: autoencoder para eliminar ruido gaussiano en imágenes de MNIST. | TensorFlow / Keras |
| [`02_Transfer_Learning_CIFAR10_MobileNetV2_EXPLICADO.ipynb`](03_Deep_Learning/02_Transfer_Learning_CIFAR10_MobileNetV2_EXPLICADO.ipynb) | *Transfer learning* con MobileNetV2 preentrenada en ImageNet sobre CIFAR-10: *feature extraction*, *data augmentation* y *fine-tuning*. | TensorFlow / Keras |

### 📁 Proyectos · EDA interactivo del BMI (Streamlit)

Carpeta: [`Proyectos/LucasMartinez_Proyecto_BMI/`](Proyectos/LucasMartinez_Proyecto_BMI/)

Aplicación web multipágina para explorar el **Índice de Masa Corporal (BMI)** y su relación con la edad, la actividad física semanal y el tabaquismo, comparando días de semana y fin de semana (900 registros).

| Página | Contenido |
|---|---|
| `Inicio.py` | Carga y validación del CSV, filtros por tipo de día, fumador y edad |
| `pages/1_EDA.py` | EDA descriptivo: estadística descriptiva, distribución del BMI y comparación semana vs. fin de semana |
| `pages/2_Relaciones.py` | Relaciones entre variables, ajustes polinómicos y matriz de correlación |
| `pages/3_Hallazgos.py` | Hallazgos principales (observación → evidencia → interpretación) |

**Tecnologías:** Python, pandas, NumPy, Plotly, Streamlit.

---

## Cómo usar este repositorio

### Notebooks

La mayoría de los notebooks se crearon en **Google Colab** y tienen al inicio el botón *Open in Colab* para abrirlos directamente. También se pueden ejecutar localmente con Jupyter:

```bash
pip install pandas numpy matplotlib scikit-learn xgboost catboost tensorflow requests jupyter
jupyter notebook
```

### Aplicación Streamlit (proyecto BMI)

```bash
pip install streamlit pandas numpy plotly
cd Proyectos/LucasMartinez_Proyecto_BMI
streamlit run Inicio.py
```

En la página de inicio, sube el archivo `datos.csv` incluido en la carpeta y aplica los filtros para navegar por el resto de páginas.

---

## Sobre este repositorio

Este espacio documenta mi proceso de aprendizaje en ciencia de datos. Los proyectos se irán ampliando y mejorando a medida que avance en mis estudios.

**Autor:** Lucas Martínez
