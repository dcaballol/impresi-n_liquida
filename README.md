# 📄 Divisor de Liquidaciones por Centro de Costo

Esta aplicación Streamlit permite separar e imprimir automáticamente las liquidaciones de sueldo en formato PDF, agrupadas por centro de costo a partir de un archivo Excel con RUTs.

## ✅ ¿Qué hace?

1. Lee un PDF con TODAS las liquidaciones.
2. Lee un Excel con columnas:
   - `RUN`: RUT de cada trabajador
   - `Centro Costo`: nombre del centro al que pertenece
3. Agrupa los RUTs por centro de costo.
4. Genera un PDF por grupo (centro de costo).
5. (Opcional) Imprime automáticamente cada grupo por separado.
6. Permite descargar los PDFs generados uno por uno.

## ▶️ ¿Cómo usar?

1. Sube el PDF con todas las liquidaciones.
2. Sube el Excel con los RUTs y centro de costo.
3. Configura el tiempo de espera entre impresiones (opcional).
4. Marca la opción de impresión automática si lo deseas.
5. Haz clic en **Iniciar proceso**.

## 🖨️ Requisitos

- Para impresión automática, debes estar en **Windows** con una impresora predeterminada configurada.
- Para ejecutar localmente:
```bash
pip install -r requirements.txt
streamlit run app.py
```

## 🚀 Despliegue en Streamlit Cloud

Sube este repositorio a GitHub y conéctalo a [https://streamlit.io/cloud](https://streamlit.io/cloud). Listo.
