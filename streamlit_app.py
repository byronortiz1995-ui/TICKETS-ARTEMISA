import streamlit as st
import xml.etree.ElementTree as ET

st.set_page_config(page_title="Artemisa POS", page_icon="🔧")

# Ocultamos los menús de Streamlit para que no salgan en la impresión
st.markdown("""
    <style>
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    </style>
    """, unsafe_allow_html=True)

st.title("🔧 Artemisa XML a Ticket")

uploaded_file = st.file_uploader("Arrastra el XML de autorización aquí", type=["xml"])

if uploaded_file is not None:
    try:
        xml_data = uploaded_file.read().decode("utf-8").strip()
        root = ET.fromstring(xml_data)
        comprobante_xml_string = root.find('comprobante').text.strip()
        factura_root = ET.fromstring(comprobante_xml_string)
        
        # Datos de Cabecera
        info_t = factura_root.find('infoTributaria')
        info_f = factura_root.find('infoFactura')
        
        emisor = info_t.find('razonSocial').text
        ruc_em = info_t.find('ruc').text
        cliente = info_f.find('razonSocialComprador').text
        ruc_cl = info_f.find('identificacionComprador').text
        fecha = info_f.find('fechaEmision').text
        total_f = float(info_f.find('importeTotal').text)

        # CONSTRUCCIÓN DEL TICKET (Ancho para POS-80)
        # Usamos pre-format para que cada espacio cuente
        t = f"{emisor.center(40)}\n"
        t += f"{('RUC: ' + ruc_em).center(40)}\n"
        t += "-" * 40 + "\n"
        t += f"FECHA: {fecha}\n"
        t += f"CLIENTE: {cliente[:31]}\n"
        t += f"RUC/CI: {ruc_cl}\n"
        t += "-" * 40 + "\n"
        t += f"{'CANT':<6}{'DESCRIPCION':<16}{'P.U':>8}{'TOTAL':>10}\n"
        t += "-" * 40 + "\n"

        for det in factura_root.findall('.//detalles/detalle'):
            cant = float(det.find('cantidad').text)
            desc = det.find('descripcion').text[:15]
            p_uni = float(det.find('precioUnitario').text)
            subt = float(det.find('precioTotalSinImpuesto').text)
            t += f"{cant:<6.2f}{desc:<16}${p_uni:>7.2f}${subt:>9.2f}\n"

        t += "-" * 40 + "\n"
        t += f"{'TOTAL A PAGAR:':<28}${total_f:>11.2f}\n"
        t += "=" * 40 + "\n"
        t += "        ¡Gracias por su compra!\n"
        t += "         Soporte: Artemisa Tech"

        # MOSTRAR TICKET PROFESIONAL
        st.markdown(f"""
            <div style="background-color: white; color: black; padding: 10px; font-family: monospace; white-space: pre; line-height: 1.2; border: 1px solid #ddd;">
{t}
            </div>
            """, unsafe_allow_html=True)
        
        st.write("---")
        st.info("Presiona **Ctrl + P** para imprimir directamente.")

    except Exception as e:
        st.error(f"Error al generar el ticket: {e}")