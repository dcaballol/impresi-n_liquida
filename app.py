import streamlit as st
import pandas as pd
import PyPDF2
import tempfile
import time
import os
import platform

st.set_page_config(page_title="Divisor de Liquidaciones", layout="centered")
st.title("📄 Divisor de Liquidaciones por Centro de Costo")

# Subida de archivos
pdf_file = st.file_uploader("📤 Sube el PDF con todas las liquidaciones", type=["pdf"])
excel_file = st.file_uploader("📤 Sube el Excel con columnas 'RUN' y 'Centro Costo'", type=["xlsx"])
delay = st.number_input("⏱ Tiempo de espera entre centros (segundos)", min_value=0, value=10, step=1)
imprimir = st.checkbox("🖨️ Imprimir automáticamente cada PDF")

if pdf_file and excel_file:
    if st.button("▶️ Iniciar proceso"):
        with st.spinner("Procesando..."):

            output_dir = tempfile.mkdtemp()
            pdf_path = os.path.join(output_dir, "base.pdf")
            with open(pdf_path, "wb") as f:
                f.write(pdf_file.read())

            df = pd.read_excel(excel_file, dtype=str)
            if "RUN" not in df.columns or "Centro Costo" not in df.columns:
                st.error("❌ El archivo Excel debe tener columnas llamadas exactamente 'RUN' y 'Centro Costo'.")
                st.stop()

            reader = PyPDF2.PdfReader(pdf_path)
            grupo_centros = df.groupby("Centro Costo")
            pdf_links = []

            for idx, (centro, grupo) in enumerate(grupo_centros):
                ruts = grupo['RUN'].dropna().astype(str).tolist()
                writer = PyPDF2.PdfWriter()

                for i, page in enumerate(reader.pages):
                    texto = page.extract_text()
                    if texto and any(rut in texto for rut in ruts):
                        writer.add_page(page)

                if writer.pages:
                    output_pdf = os.path.join(output_dir, f"{centro}.pdf")
                    with open(output_pdf, "wb") as f:
                        writer.write(f)

                    st.success(f"✅ Centro '{centro}' procesado.")
                    pdf_links.append((centro, output_pdf))

                    if imprimir and platform.system() == "Windows":
                        try:
                            os.startfile(output_pdf, "print")
                            st.info(f"🖨️ PDF enviado a impresora: {centro}")
                        except Exception as e:
                            st.warning(f"⚠️ No se pudo imprimir {centro}: {e}")
                else:
                    st.warning(f"⚠️ No se encontraron páginas para el centro '{centro}'.")

                if idx < len(grupo_centros) - 1:
                    time.sleep(delay)

            st.subheader("📥 Descarga de PDFs generados")
            for centro, path in pdf_links:
                with open(path, "rb") as file:
                    st.download_button(
                        label=f"Descargar PDF: {centro}",
                        data=file,
                        file_name=os.path.basename(path),
                        mime="application/pdf"
                    )

        st.success("🎉 ¡Proceso completado con éxito!")
