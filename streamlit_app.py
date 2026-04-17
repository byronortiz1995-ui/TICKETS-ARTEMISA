import streamlit as st
import xml.etree.ElementTree as ET

st.set_page_config(page_title="Artemisa POS", page_icon="🔧")

# CSS DEFINITIVO: Oculta solo lo innecesario
st.markdown("""
    <style>
    #MainMenu, footer, header {visibility: hidden;}
    
    @media print {
        /* Ocultamos los componentes de Streamlit específicamente */
        .stFileUploader, .stButton, .stAlert, .stHeader, h1, hr, .stMarkdown:not(.printable-ticket) {
            display: none !important;
        }
        
        /* Ajustamos el ticket para que sea lo único visible */
        .printable-ticket {
            visibility: visible !important;
            position: absolute !important;
            left: 0 !important;
            top: 0 !important;
            width: 100% !important;
            border: none !important;
            font-size: 10pt !important; /* Ajuste de tamaño para POS-80 */
        }

        /* Eliminamos bordes y sombras del navegador */
        div[data-testid="stVerticalBlock"] > div:has(.printable-ticket) {
            padding: 0 !important;
        }
    }
    </style>
    """, unsafe_allow_html=True)

st.title("🔧 Artemisa XML a Ticket")

uploaded_file = st.file_uploader("Sube el XML aquí", type=["xml"])

if uploaded_file is not None:
    try:
        xml_data = uploaded_file.read().decode("utf-8").strip()
        root = ET.fromstring(xml_data)
        comprobante_xml_string = root.find('comprobante').text.strip()
        factura_root = ET.fromstring(comprobante_xml_string)
        
        info_t = factura_root.find('infoTributaria')
        info_f = factura_root.find('infoFactura')
        
        emisor = info_t.find('razonSocial').text
        ruc_em = info_t.find('ruc').text
        cliente = info_f.find('razonSocialComprador').text
        ruc_cl = info_f.find('identificacionComprador').text
        fecha = info_f.find('fechaEmision').text
        total_f = float(info_f.find('importeTotal').text)

        # Diseño del Ticket (Ancho 40 carac.)
        linea = "-" * 40 + "\n"
        t = f"{emisor.center(40)}\n"
        t += f"{('RUC: ' + ruc_em).center(40)}\n"
        t += linea
        t += f"FECHA: {fecha}\n"
        t += f"CLIENTE: {cliente[:31]}\n"
        t += f"RUC/CI: {ruc_cl}\n"
        t += linea
        t += f"{'CANT':<6}{'DESCRIP':<14}{'P.U':>8}{'TOTAL':>11}\n"
        t += linea

        for det in factura_root.findall('.//detalles/detalle'):
            cant = float(det.find('cantidad').text)
            desc = det.find('descripcion').text[:13]
            p_uni = float(det.find('precioUnitario').text)
            subt = float(det.find('precioTotalSinImpuesto').text)
            t += f"{cant:<6.2f}{desc:<14}${p_uni:>7.2f}${subt:>10.2f}\n"

        t += linea
        t += f"{'TOTAL A PAGAR:':<26}${total_f:>13.2f}\n"
        t += "=" * 40 + "\n"
        t += "        ¡Gracias por su compra!\n"
        t += "         Soporte: Artemisa Tech"

        # Contenedor del ticket
        st.markdown(f'<div class="printable-ticket" style="background-color: white; color: black; font-family: monospace; white-space: pre; line-height: 1.2; padding: 5px;">{t}</div>', unsafe_allow_html=True)
        
        st.write("---")
        st.success("✅ Generado con éxito. Usa **Ctrl + P** para imprimir.")

    except Exception as e:
        st.error(f"Error: {e}")