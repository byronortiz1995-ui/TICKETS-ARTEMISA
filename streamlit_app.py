import streamlit as st
import xml.etree.ElementTree as ET
import pandas as pd

# 1. Configuración de Marca (Artemisa)
st.set_page_config(page_title="Artemisa XML Ticket", layout="centered")
st.title("🔧 Artemisa XML a Ticket")
st.markdown("### Arrastra tu factura XML aquí abajo")

# 2. El Cargador de Archivos (Arrastrar y soltar)
uploaded_file = st.file_uploader("Sube el XML del SRI", type=["xml"])

if uploaded_file is not None:
    try:
        # 3. Lectura del XML
        tree = ET.parse(uploaded_file)
        root = tree.getroot()
        
        # Extraer info básica
        info_t = root.find('.//infoTributaria')
        emisor = info_t.find('razonSocial').text
        clave = info_t.find('claveAcceso').text
        
        # 4. Vista Previa Estilo Ticket
        st.subheader("📋 Vista Previa del Ticket (80mm)")
        
        with st.container():
            st.code(f"""
================================
       {emisor[:25]}
================================
RUC: {info_t.find('ruc').text}
Clave: {clave[:20]}...
--------------------------------
            """, language="text")
            
            # Tabla de productos
            items = []
            for d in root.findall('.//detalle'):
                items.append({
                    "Cant": d.find('cantidad').text,
                    "Descripción": d.find('descripcion').text[:20],
                    "Total": d.find('precioTotalSinImpuesto').text
                })
            
            st.table(pd.DataFrame(items))
            
        # 5. Botón de Acción
        if st.button("🚀 Generar para Impresora POS"):
            st.success("Formato listo. Presiona Ctrl+P y elige tu impresora térmica.")

    except Exception as e:
        st.error(f"Error: Asegúrate de que el XML sea una factura válida del SRI. ({e})")