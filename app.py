import streamlit as st
import pandas as pd
import PyPDF2
import tempfile
import time
import os
import zipfile
from io import BytesIO

st.set_page_config(page_title="Divisor de Liquidaciones", layout="centered")
st.title("📄 Divisor de Liquidaciones por Centro de Costo")

pdf_file = st.file_uploader("📤 Sube el PDF con todas las liquidaciones", type=["pdf"])
excel_file = st.file_uploader("📤 Sube el Excel con columnas 'RUN' y 'Centro Costo'", type=["xlsx"])
delay = st.number_input("⏱ Tiempo de espera entre centros (segundos)", min_value=0, value=10, step=1)

if pdf_file and excel_file:
    if st.button("▶️ Iniciar proceso"):
        with st.spinner("Procesando..."):

            output_dir = tempfile.mkdtemp()
            pdf_path = os.path.join(output_dir, "base.pdf")
            with open(pdf_path, "wb") as f:
                f.write(pdf_file.read())

            df = pd.read_excel(excel_file, dtype=str)
            if "RUN" not in df.columns or "Centro Costo" not in df.columns:
                st.error("❌ El archivo Excel debe tener columnas 'RUN' y 'Centro Costo'.")
                st.stop()

            reader = PyPDF2.PdfReader(pdf_path)
            grupo_centros = df.groupby("Centro Costo")
            pdf_paths = []

            for idx, (centro, grupo) in enumerate(grupo_centros):
                ruts = grupo['RUN'].dropna().astype(str).tolist()
                writer = PyPDF2.PdfWriter()

                for i, page in enumerate(reader.pages):
                    texto = page.extract_text()
                    if texto and any(rut in texto for rut in ruts):
                        writer.add_page(page)

                if writer.pages:
                    safe_name = "".join(c if c.isalnum() or c in " _-" else "_" for c in centro)
                    output_pdf = os.path.join(output_dir, f"{safe_name}.pdf")
                    with open(output_pdf, "wb") as f:
                        writer.write(f)
                    pdf_paths.append(output_pdf)
                    st.success(f"✅ Procesado: {centro}")
                else:
                    st.warning(f"⚠️ No se encontraron páginas para: {centro}")

                if idx < len(grupo_centros) - 1:
                    time.sleep(delay)

            if pdf_paths:
                st.subheader("📦 Descarga de todos los PDFs en un solo archivo ZIP")

                zip_buffer = BytesIO()
                with zipfile.ZipFile(zip_buffer, "w") as zipf:
                    for path in pdf_paths:
                        zipf.write(path, arcname=os.path.basename(path))
                st.download_button(
                    label="⬇️ Descargar ZIP con todas las liquidaciones",
                    data=zip_buffer.getvalue(),
                    file_name="Liquidaciones_Por_Centro.zip",
                    mime="application/zip"
                )
            else:
                st.info("No se generaron archivos PDF.")

        st.success("🎉 ¡Proceso completado!")
