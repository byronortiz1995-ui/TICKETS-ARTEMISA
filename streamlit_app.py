import streamlit as st
import xml.etree.ElementTree as ET
import pandas as pd

st.set_page_config(page_title="Artemisa POS", page_icon="🔧")
st.title("🔧 Artemisa XML a Ticket")

uploaded_file = st.file_uploader("Arrastra el XML de autorización aquí", type=["xml"])

if uploaded_file is not None:
    try:
        # 1. Limpieza y Lectura del XML
        xml_data = uploaded_file.read().decode("utf-8").strip()
        root = ET.fromstring(xml_data)
        
        # 2. Extracción del Comprobante (CDATA)
        comprobante_xml_string = root.find('comprobante').text.strip()
        factura_root = ET.fromstring(comprobante_xml_string)
        
        # 3. Datos de Cabecera
        info_t = factura_root.find('infoTributaria')
        info_f = factura_root.find('infoFactura')
        
        emisor = info_t.find('razonSocial').text
        ruc_emisor = info_t.find('ruc').text
        cliente = info_f.find('razonSocialComprador').text
        ruc_cliente = info_f.find('identificacionComprador').text
        fecha = info_f.find('fechaEmision').text
        total_final = info_f.find('importeTotal').text

        st.subheader("📋 Formato de Impresión")
        
        # --- DISEÑO SIN FONDOS NEGROS (Texto Plano) ---
        # Usamos st.text para evitar el formato de código oscuro
        encabezado = f"""
        {emisor}
        RUC: {ruc_emisor}
        --------------------------------
        FECHA: {fecha}
        CLIENTE: {cliente}
        RUC/CI: {ruc_cliente}
        --------------------------------
        """
        st.text(encabezado)
        
        # 4. Detalles con Precio Unitario
        detalles = []
        for det in factura_root.findall('.//detalles/detalle'):
            detalles.append({
                "Cant": f"{float(det.find('cantidad').text):.2f}",
                "Producto": det.find('descripcion').text[:20],
                "P. Unit": f"${float(det.find('precioUnitario').text):.2f}",
                "Subtotal": f"${float(det.find('precioTotalSinImpuesto').text):.2f}"
            })
        
        # Mostramos la tabla (Streamlit la muestra con fondo blanco por defecto)
        st.table(pd.DataFrame(detalles))
        
        # Pie del Ticket
        pie = f"""
        --------------------------------
        TOTAL A PAGAR: ${float(total_final):.2f}
        ================================
        ¡Gracias por su confianza!
        Soporte: Artemisa Tech
        """
        st.text(pie)
        
        if st.button("🚀 Confirmar para Impresora"):
            st.success("Listo para imprimir. Presiona Ctrl + P y selecciona tu impresora POS.")

    except Exception as e:
        st.error(f"Error técnico: {e}")