import streamlit as st
import xml.etree.ElementTree as ET
import pandas as pd

st.set_page_config(page_title="Artemisa POS", page_icon="🔧")
st.title("🔧 Artemisa XML a Ticket")

uploaded_file = st.file_uploader("Arrastra el XML de autorización aquí", type=["xml"])

if uploaded_file is not None:
    try:
        # --- EL TRUCO PARA EL ERROR ---
        # Leemos el contenido y quitamos espacios en blanco al inicio y final
        xml_data = uploaded_file.read().decode("utf-8").strip()
        root = ET.fromstring(xml_data)
        
        # Extraer el CDATA (La factura real)
        comprobante_xml_string = root.find('comprobante').text.strip()
        factura_root = ET.fromstring(comprobante_xml_string)
        
        # --- EXTRACCIÓN DE DATOS ---
        info_t = factura_root.find('infoTributaria')
        info_f = factura_root.find('infoFactura')
        
        emisor = info_t.find('razonSocial').text
        ruc_emisor = info_t.find('ruc').text
        cliente = info_f.find('razonSocialComprador').text
        fecha = info_f.find('fechaEmision').text
        total = info_f.find('importeTotal').text

        st.subheader("📋 Vista Previa del Ticket")
        
        # Formato de ticket para la pantalla
        ticket_header = f"""
================================
      {emisor[:30]}
      RUC: {ruc_emisor}
================================
FECHA: {fecha}
CLIENTE: {cliente[:25]}
--------------------------------
        """
        st.code(ticket_header, language="text")
        
        detalles = []
        for det in factura_root.findall('.//detalle'):
            detalles.append({
                "Cant": float(det.find('cantidad').text),
                "Descripción": det.find('descripcion').text[:20],
                "Total": float(det.find('precioTotalSinImpuesto').text)
            })
        
        st.table(pd.DataFrame(detalles))
        st.code(f"TOTAL: ${float(total):.2f}\n================================", language="text")
        
        if st.button("🚀 Preparar Impresión"):
            st.balloons()
            st.success("Formato listo. Presiona Ctrl+P")

    except Exception as e:
        st.error(f"Error al procesar: {e}")