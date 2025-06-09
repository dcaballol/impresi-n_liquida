import streamlit as st
import pandas as pd
import PyPDF2
import tempfile
import time
import os
import zipfile
from io import BytesIO

st.set_page_config(page_title="Divisor de Liquidaciones", layout="centered")
st.title("📄 Divisor de Liquidaciones por Centro de Costo (Orden Real por Índice)")

pdf_file = st.file_uploader("📤 Sube el PDF con todas las liquidaciones", type=["pdf"])
excel_file = st.file_uploader("📤 Sube el Excel con columnas 'Indice', 'RUN' y 'Centro Costo'", type=["xlsx"])
delay = st.number_input("⏱ Tiempo de espera entre centros (segundos)", min_value=0, value=10, step=1)

if pdf_file and excel_file:
    if st.button("▶️ Iniciar proceso"):
        with st.spinner("Procesando..."):

            output_dir = tempfile.mkdtemp()
            pdf_path = os.path.join(output_dir, "base.pdf")
            with open(pdf_path, "wb") as f:
                f.write(pdf_file.read())

            df = pd.read_excel(excel_file, dtype=str)
            if not all(col in df.columns for col in ["Indice", "RUN", "Centro Costo"]):
                st.error("❌ El archivo Excel debe tener columnas 'Indice', 'RUN' y 'Centro Costo'.")
                st.stop()

            df["Indice"] = pd.to_numeric(df["Indice"], errors="coerce")
            df = df.dropna(subset=["Indice"]).sort_values(by="Indice")
            grupo_centros = df.groupby("Centro Costo", sort=False)

            reader = PyPDF2.PdfReader(pdf_path)
            paginas_pdf = list(reader.pages)
            paginas_texto = [page.extract_text() or "" for page in paginas_pdf]

            pdf_paths = []

            for idx, (centro, grupo) in enumerate(grupo_centros):
                grupo = grupo.sort_values(by="Indice")
                ruts = grupo['RUN'].dropna().astype(str).tolist()
                writer = PyPDF2.PdfWriter()
                paginas_utilizadas = set()

                for rut in ruts:
                    for i, texto in enumerate(paginas_texto):
                        if i not in paginas_utilizadas and rut in texto:
                            writer.add_page(paginas_pdf[i])
                            paginas_utilizadas.add(i)
                            break  # Salta al siguiente RUT después de encontrar su página

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
