import streamlit as st
import xml.etree.ElementTree as ET

st.set_page_config(page_title="Artemisa POS", page_icon="🔧")
st.title("🔧 Artemisa XML a Ticket")

uploaded_file = st.file_uploader("Arrastra el XML de autorización aquí", type=["xml"])

if uploaded_file is not None:
    try:
        # 1. Limpieza y Lectura
        xml_data = uploaded_file.read().decode("utf-8").strip()
        root = ET.fromstring(xml_data)
        comprobante_xml_string = root.find('comprobante').text.strip()
        factura_root = ET.fromstring(comprobante_xml_string)
        
        # 2. Datos de Cabecera
        info_t = factura_root.find('infoTributaria')
        info_f = factura_root.find('infoFactura')
        
        emisor = info_t.find('razonSocial').text
        ruc_em = info_t.find('ruc').text
        cliente = info_f.find('razonSocialComprador').text
        ruc_cl = info_f.find('identificacionComprador').text
        fecha = info_f.find('fechaEmision').text
        total_f = float(info_f.find('importeTotal').text)

        st.subheader("📋 Formato Final para Impresión")

        # 3. Construcción del Ticket en Texto Plano (Ancho 40 carac.)
        # Esto asegura que no haya fondos negros ni gráficos extraños
        cuerpo_ticket = f"{emisor[:40]}\n"
        cuerpo_ticket += f"RUC: {ruc_em}\n"
        cuerpo_ticket += "-" * 40 + "\n"
        cuerpo_ticket += f"FECHA: {fecha}\n"
        cuerpo_ticket += f"CLIENTE: {cliente[:31]}\n"
        cuerpo_ticket += f"RUC/CI: {ruc_cl}\n"
        cuerpo_ticket += "-" * 40 + "\n"
        cuerpo_ticket += f"{'CANT':<6}{'DESCRIPCION':<18}{'P.U':>7}{'TOTAL':>9}\n"
        cuerpo_ticket += "-" * 40 + "\n"

        for det in factura_root.findall('.//detalles/detalle'):
            cant = float(det.find('cantidad').text)
            desc = det.find('descripcion').text[:17]
            p_uni = float(det.find('precioUnitario').text)
            subt = float(det.find('precioTotalSinImpuesto').text)
            cuerpo_ticket += f"{cant:<6.2f}{desc:<18}${p_uni:>6.2f}${subt:>8.2f}\n"

        cuerpo_ticket += "-" * 40 + "\n"
        cuerpo_ticket += f"{'TOTAL A PAGAR:':<30}${total_f:>9.2f}\n"
        cuerpo_ticket += "=" * 40 + "\n"
        cuerpo_ticket += "      ¡Gracias por su confianza!\n"
        cuerpo_ticket += "        Soporte: Artemisa Tech"

        # Mostramos el ticket con st.text para que sea fondo blanco y texto negro
        st.text(cuerpo_ticket)
        
        # Botón de ayuda para impresión
        st.info("Para imprimir: Selecciona el texto de arriba, presiona Ctrl+P y en 'Ajustes' asegúrate de desactivar 'Gráficos de fondo'.")

    except Exception as e:
        st.error(f"Error técnico: {e}")