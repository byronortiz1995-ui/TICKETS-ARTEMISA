import streamlit as st
import xml.etree.ElementTree as ET
import pandas as pd

st.set_page_config(page_title="Artemisa POS", page_icon="🔧")
st.title("🔧 Artemisa XML a Ticket")

uploaded_file = st.file_uploader("Arrastra el XML de autorización aquí", type=["xml"])

if uploaded_file is not None:
    try:
        # 1. Leer el XML de Autorización
        tree = ET.parse(uploaded_file)
        root = tree.getroot()
        
        # 2. Extraer el CDATA (La factura real está dentro de 'comprobante')
        comprobante_xml_string = root.find('comprobante').text
        factura_root = ET.fromstring(comprobante_xml_string)
        
        # 3. Extraer Datos con el nuevo mapa
        info_t = factura_root.find('infoTributaria')
        info_f = factura_root.find('infoFactura')
        
        emisor = info_t.find('razonSocial').text
        cliente = info_f.find('razonSocialComprador').text
        total = info_f.find('importeTotal').text
        fecha = info_f.find('fechaEmision').text
        ruc_emisor = info_t.find('ruc').text

        # 4. Diseño del Ticket en pantalla
        st.subheader("📋 Vista Previa del Ticket")
        
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
        
        # 5. Extraer Detalles de Productos
        detalles = []
        for det in factura_root.findall('.//detalle'):
            detalles.append({
                "Cant": float(det.find('cantidad').text),
                "Descripción": det.find('descripcion').text[:20],
                "Total": float(det.find('precioTotalSinImpuesto').text)
            })
        
        df = pd.DataFrame(detalles)
        st.table(df)
        
        st.code(f"TOTAL: ${float(total):.2f}\n================================", language="text")
        
        if st.button("🚀 Preparar Impresión"):
            st.balloons()
            st.success("Formato enviado. Presiona Ctrl + P")

    except Exception as e:
        st.error(f"Error al procesar: {e}")