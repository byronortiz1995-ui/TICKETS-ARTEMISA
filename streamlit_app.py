import streamlit as st
import xml.etree.ElementTree as ET

st.set_page_config(page_title="Artemisa POS", page_icon="🔧")

# CSS OPTIMIZADO: Muestra SOLO el ticket al imprimir
st.markdown("""
    <style>
    /* Ocultar elementos molestos en la pantalla normal */
    #MainMenu, footer, header {visibility: hidden;}

    /* REGLAS DE IMPRESIÓN */
    @media print {
        /* Ocultar ABSOLUTAMENTE TODO */
        body * {
            visibility: hidden;
            margin: 0;
        }
        /* Mostrar SOLO el contenedor del ticket y su contenido */
        .printable-ticket, .printable-ticket * {
            visibility: visible;
        }
        .printable-ticket {
            position: absolute;
            left: 0;
            top: 0;
            width: 100%;
            color: black !important;
            background-color: white !important;
            font-size: 12pt;
        }
        /* Quitar pie de página del navegador (URL, fecha) */
        @page {
            margin: 0.5cm;
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

        # Construcción del texto (Ajustado a 40 caracteres para POS-80)
        linea = "-" * 40 + "\n"
        t = f"{emisor.center(40)}\n"
        t += f"{('RUC: ' + ruc_em).center(40)}\n"
        t += linea
        t += f"FECHA: {fecha}\n"
        t += f"CLIENTE: {cliente[:31]}\n"
        t += f"RUC/CI: {ruc_cl}\n"
        t += linea
        t += f"{'CANT':<5}{'DESCRIPCION':<15}{'P.U':>8}{'TOTAL':>12}\n"
        t += linea

        for det in factura_root.findall('.//detalles/detalle'):
            cant = float(det.find('cantidad').text)
            desc = det.find('descripcion').text[:14]
            p_uni = float(det.find('precioUnitario').text)
            subt = float(det.find('precioTotalSinImpuesto').text)
            t += f"{cant:<5.2f}{desc:<15}${p_uni:>7.2f}${subt:>11.2f}\n"

        t += linea
        t += f"{'TOTAL A PAGAR:':<25}${total_f:>14.2f}\n"
        t += "=" * 40 + "\n"
        t += "        ¡Gracias por su compra!\n"
        t += "         Soporte: Artemisa Tech"

        # EL TICKET (Contenedor con clase printable-ticket)
        st.markdown(f"""
            <div class="printable-ticket" style="background-color: white; color: black; padding: 10px; font-family: 'Courier New', Courier, monospace; white-space: pre; line-height: 1.2;">
{t}
            </div>
            """, unsafe_allow_html=True)
        
        st.write("---")
        st.info("✅ Ticket generado. Presiona **Ctrl + P** para imprimir.")

    except Exception as e:
        st.error(f"Error al procesar: {e}")