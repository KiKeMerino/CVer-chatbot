# Proyectos

## CVer — CV Interactivo con RAG

### Descripción
CVer es una aplicación web que actúa como versión interactiva de mi CV. Está basada en RAG (Retrieval-Augmented Generation) y permite a recruiters hacerme preguntas directamente, como si estuvieran en una entrevista real. El sistema responde en primera persona basándose exclusivamente en la información indexada de mi CV y mi perfil personal.

### Tecnologías utilizadas
Python, Streamlit, OpenAI GPT-4o-mini, OpenAI text-embedding-3-large, ChromaDB, Google Sheets API, gspread, Google Analytics 4.

### Arquitectura y funcionamiento
La app sigue un pipeline RAG clásico: el texto del CV se divide en chunks semánticos y se indexa en ChromaDB como embeddings vectoriales. Cuando el usuario hace una pregunta, se genera su embedding, se recuperan los chunks más relevantes por similitud coseno (top-k), y se construye un prompt con ese contexto para que el LLM responda en primera persona.

### Características principales
La interfaz tiene un modo Chat para recruiters con preguntas sugeridas y un límite de 12 preguntas por sesión. Incluye un panel Admin protegido por contraseña con reindexación forzada de documentos y estadísticas de uso. El sistema de tracking registra visitas y preguntas en Google Sheets, identificando visitantes únicos mediante un fingerprint basado en hash MD5 de IP y User-Agent.

### Despliegue
Desplegado en Streamlit Community Cloud. El frontend está construido con CSS personalizado con estética moderna y oscura.

### Lo que aprendí
Implementación completa de un pipeline RAG desde cero, gestión de vector stores con ChromaDB, diseño de system prompts para mantener el personaje en primera persona, integración con APIs externas (Google Sheets, OpenAI), y despliegue en la nube con gestión de secrets.

---

## Sierra — Predicción de Cobertura de Nieve con LSTM

### Descripción
Sierra es un proyecto de Machine Learning enfocado en la predicción de series temporales de área cubierta por nieve a escala de cuenca hidrográfica, combinando imágenes satelitales con modelos de deep learning. Genera tanto predicciones a nivel de cuenca como mapas de probabilidad de nieve a nivel de píxel.

### Motivación
La predicción precisa de cobertura de nieve es crítica para hidrología y gestión de recursos hídricos, análisis climático y evaluación de riesgos medioambientales. Los enfoques estadísticos tradicionales tienen dificultades para modelar la dinámica temporal no lineal de la evolución de la nieve.

### Tecnologías utilizadas
Python, TensorFlow 2.10 (GPU), LSTM, Optuna, rasterio, GDAL, xarray, pandas, numpy, scikit-learn, matplotlib, seaborn.

### Datos y preprocesamiento
Los datos provienen de ficheros HDF de satélite MODIS (NASA EarthData). El pipeline incluye reproyección de HDF a coordenadas geográficas, cómputo de probabilidad de nieve a nivel de píxel, agregación a nivel de cuenca y limpieza con imputación de outliers por IQR.

### Modelo y metodología
El modelo es un NARX (Nonlinear AutoRegressive with eXogenous inputs) implementado con capas LSTM. Las entradas son el histórico de área cubierta por nieve, variables meteorológicas exógenas y probabilidades de nieve por píxel. La métrica de evaluación principal es el Nash-Sutcliffe Efficiency (NSE). El tuning de hiperparámetros está automatizado con Optuna.

### Resultados
El sistema genera modelos LSTM por cuenca en formato .h5, métricas por cuenca almacenadas en metrics.json, predicciones de series temporales con evaluación de incertidumbre, y visualizaciones tanto de líneas temporales por cuenca como de mapas de calor de probabilidad de nieve a nivel de píxel.

### Lo que aprendí
Procesamiento de datos de teledetección (HDF, GDAL, rasterio), modelado de series temporales con LSTM y arquitecturas NARX, tuning automático de hiperparámetros con Optuna, y diseño de pipelines ML reproducibles orientados a producción.

---

## EasyMoney — Predicción de Propensión de Compra y Segmentación de Clientes

### Descripción
EasyMoney es un proyecto de Data Science end-to-end orientado a mejorar la rentabilidad de campañas de marketing bancario mediante Machine Learning. El sistema predice la propensión de compra de clientes para productos financieros de alto valor y realiza segmentación de clientes para estrategias de marketing dirigido.

### Objetivo de negocio
Identificar los clientes con mayor probabilidad de contratar productos como Planes de Pensiones o Depósitos a Largo Plazo, agruparlos en segmentos accionables para personalizar campañas, y cuantificar el impacto económico de la estrategia ML frente al marketing masivo tradicional.

### Tecnologías utilizadas
Python, scikit-learn, XGBoost, Random Forest, K-Means, pandas, numpy, matplotlib, seaborn.

### Metodología y pipeline
El proyecto sigue un pipeline estructurado de cuatro fases. La primera es limpieza de datos y feature engineering sobre un dataset de aproximadamente 5,9 millones de registros, con tratamiento de valores nulos y optimización de memoria. La segunda es modelado supervisado de propensión con Random Forest y XGBoost, evaluado con AUC-ROC, obteniendo un AUC de 0.93 para predicción de Depósito a Largo Plazo. La tercera es segmentación no supervisada con K-Means, identificando 6 segmentos de clientes con interpretación de negocio. La cuarta es análisis de caso de uso y ROI, simulando una campaña de marketing real.

### Resultados
AUC-ROC de 0.93 en el modelo de propensión. Comparando la estrategia ML frente a la campaña tradicional: la campaña ML capturó aproximadamente 27,3 millones de euros frente a 1,2 millones de la campaña tradicional, lo que supone una mejora de ROI superior a 20 veces. El impacto se traduce en una contribución directa al EBITDA reduciendo costes de adquisición.

### Lo que aprendí
Aplicación de ML a casos de negocio reales con métricas de impacto económico, modelado supervisado y no supervisado en datasets de millones de registros, interpretación de modelos con análisis de feature importance, y comunicación de resultados orientada a negocio.