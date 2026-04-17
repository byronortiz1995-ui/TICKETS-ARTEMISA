import streamlit as st
import xml.etree.ElementTree as ET

st.set_page_config(page_title="Artemisa POS", page_icon="🔧")

# ESTILOS CSS: Limpieza total para impresión
st.markdown("""
    <style>
    /* Ocultar elementos de la web en la pantalla */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    
    /* ESTO ES LO MÁS IMPORTANTE: Reglas para la impresora */
    @media print {
        /* Ocultar todo lo que no sea el ticket */
        button, .stButton, .stFileUploader, .stInfo, .stAlert, h1, .stMarkdown:not(.ticket-container) {
            display: none !important;
        }
        
        /* Asegurar que el ticket ocupe el ancho correcto y sea texto negro puro */
        .ticket-container {
            border: none !important;
            margin: 0 !important;
            padding: 0 !important;
            width: 100% !important;
            position: absolute;
            top: 0;
            left: 0;
        }
        
        /* Eliminar márgenes extras de la página de impresión */
        @page {
            margin: 0;
        }
    }
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
        
        info_t = factura_root.find('infoTributaria')
        info_f = factura_root.find('infoFactura')
        
        emisor = info_t.find('razonSocial').text
        ruc_em = info_t.find('ruc').text
        cliente = info_f.find('razonSocialComprador').text
        ruc_cl = info_f.find('identificacionComprador').text
        fecha = info_f.find('fechaEmision').text
        total_f = float(info_f.find('importeTotal').text)

        # Construcción del texto del ticket (Ancho 40 carac. para POS-80)
        t = f"{emisor.center(40)}\n"
        t += f"{('RUC: ' + ruc_em).center(40)}\n"
        t += "-" * 40 + "\n"
        t += f"FECHA: {fecha}\n"
        t += f"CLIENTE: {cliente[:31]}\n"
        t += f"RUC/CI: {ruc_cl}\n"
        t += "-" * 40 + "\n"
        t += f"{'CANT':<5}{'DESCRIPCION':<15}{'P.U':>9}{'TOTAL':>11}\n"
        t += "-" * 40 + "\n"

        for det in factura_root.findall('.//detalles/detalle'):
            cant = float(det.find('cantidad').text)
            desc = det.find('descripcion').text[:14]
            p_uni = float(det.find('precioUnitario').text)
            subt = float(det.find('precioTotalSinImpuesto').text)
            t += f"{cant:<5.2f}{desc:<15}${p_uni:>8.2f}${subt:>10.2f}\n"

        t += "-" * 40 + "\n"
        t += f"{'TOTAL A PAGAR:':<26}${total_f:>12.2f}\n"
        t += "=" * 40 + "\n"
        t += "        ¡Gracias por su compra!\n"
        t += "         Soporte: Artemisa Tech"

        # TICKET VISIBLE (Encerrado en la clase ticket-container)
        st.markdown(f"""
            <div class="ticket-container" style="background-color: white; color: black; padding: 15px; font-family: 'Courier New', Courier, monospace; white-space: pre; line-height: 1.2; border: 1px solid #eee;">
{t}
            </div>
            """, unsafe_allow_html=True)
        
        st.info("💡 **Para imprimir:** Presiona **Ctrl + P**. El sistema automáticamente ocultará todo excepto el ticket.")

    except Exception as e:
        st.error(f"Error al procesar: {e}")