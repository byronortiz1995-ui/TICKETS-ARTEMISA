import streamlit as st
import xml.etree.ElementTree as ET

st.set_page_config(page_title="Artemisa POS", page_icon="🔧")

# ESTILO DE IMPRESIÓN NIVEL DIOS: Oculta TODO excepto el ticket
st.markdown("""
    <style>
    /* Ocultar en pantalla normal */
    #MainMenu, footer, header {visibility: hidden;}

    @media print {
        /* Ocultar absolutamente todos los elementos de Streamlit */
        div[data-testid="stToolbar"], 
        div[data-testid="stDecoration"], 
        div[data-testid="stStatusWidget"],
        .stApp header, 
        .stFileUploader, 
        .stButton, 
        .stAlert,
        h1, hr,
        div.stMarkdown:not(.ticket-final) {
            display: none !important;
        }

        /* Forzar que el ticket sea lo único y ocupe todo el ancho */
        .ticket-final {
            visibility: visible !important;
            display: block !important;
            position: fixed !important;
            left: 0 !important;
            top: 0 !important;
            width: 100% !important;
            margin: 0 !important;
            padding: 0 !important;
            background-color: white !important;
            color: black !important;
        }

        /* Quitar márgenes de página del navegador */
        @page {
            margin: 0;
            size: auto;
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

        # Estructura del Ticket (Ancho 40)
        l = "-" * 40 + "\n"
        t = f"{emisor.center(40)}\n"
        t += f"{('RUC: ' + ruc_em).center(40)}\n"
        t += l
        t += f"FECHA: {fecha}\n"
        t += f"CLIENTE: {cliente[:31]}\n"
        t += f"RUC/CI: {ruc_cl}\n"
        t += l
        t += f"{'CANT':<5}{'DESCRIP':<15}{'P.U':>8}{'TOTAL':>12}\n"
        t += l

        for det in factura_root.findall('.//detalles/detalle'):
            cant = float(det.find('cantidad').text)
            desc = det.find('descripcion').text[:14]
            p_u = float(det.find('precioUnitario').text)
            sub = float(det.find('precioTotalSinImpuesto').text)
            t += f"{cant:<5.2f}{desc:<15}${p_u:>7.2f}${sub:>11.2f}\n"

        t += l
        t += f"{'TOTAL A PAGAR:':<26}${total_f:>12.2f}\n"
        t += "=" * 40 + "\n"
        t += "        ¡Gracias por su compra!\n"
        t += "         Soporte: Artemisa Tech"

        # EL TICKET FINAL: Usamos una clase única 'ticket-final'
        st.markdown(f'<div class="ticket-final" style="font-family: monospace; white-space: pre; font-size: 11pt; color: black; background-color: white; padding: 5px;">{t}</div>', unsafe_allow_html=True)
        
        st.write("---")
        st.success("✅ ¡Listo! Presiona **Ctrl + P**.")

    except Exception as e:
        st.error(f"Error: {e}")