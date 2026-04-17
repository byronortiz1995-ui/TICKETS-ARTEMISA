import streamlit as st
import xml.etree.ElementTree as ET

st.set_page_config(page_title="Artemisa POS", page_icon="🔧")

# CSS DEFINITIVO: Solo el ticket existe para la impresora
st.markdown("""
    <style>
    #MainMenu, footer, header {visibility: hidden;}

    @media print {
        /* Ocultar todo lo que no sea el ticket */
        body * { visibility: hidden; }
        .ticket-print, .ticket-print * { 
            visibility: visible !important; 
        }
        .ticket-print {
            position: absolute !important;
            left: 0 !important;
            top: 0 !important;
            width: 100% !important;
            border: none !important;
        }
        /* Eliminar encabezados y pies de página del navegador */
        @page { margin: 0; }
    }
    </style>
    """, unsafe_allow_html=True)

st.title("🔧 Artemisa XML a Ticket")

uploaded_file = st.file_uploader("Subir XML de Autorización", type=["xml"])

if uploaded_file is not None:
    try:
        xml_data = uploaded_file.read().decode("utf-8").strip()
        root = ET.fromstring(xml_data)
        comprobante_xml_string = root.find('comprobante').text.strip()
        factura_root = ET.fromstring(comprobante_xml_string)
        
        info_t = factura_root.find('infoTributaria')
        info_f = factura_root.find('infoFactura')
        
        # Datos del Ticket
        emisor = info_t.find('razonSocial').text
        ruc_em = info_t.find('ruc').text
        cliente = info_f.find('razonSocialComprador').text
        ruc_cl = info_f.find('identificacionComprador').text
        fecha = info_f.find('fechaEmision').text
        total_f = float(info_f.find('importeTotal').text)

        # DISEÑO DEL TICKET (Ajustado a 40 columnas)
        # ----------------------------------------
        linea = "-" * 40 + "\n"
        t = f"{emisor.center(40)}\n"
        t += f"{('RUC: ' + ruc_em).center(40)}\n"
        t += linea
        t += f"FECHA: {fecha}\n"
        t += f"CLIENTE: {cliente[:31]}\n"
        t += f"RUC/CI: {ruc_cl}\n"
        t += linea
        # Cabecera: CANT(5) DESC(14) P.U(9) TOTAL(12)
        t += f"{'CANT':<5}{'DESCRIPCION':<14}{'P.U':>9}{'TOTAL':>12}\n"
        t += linea

        for det in factura_root.findall('.//detalles/detalle'):
            cant = float(det.find('cantidad').text)
            desc = det.find('descripcion').text[:13]
            p_u = float(det.find('precioUnitario').text)
            sub = float(det.find('precioTotalSinImpuesto').text)
            # Alineación forzada para que el TOTAL quede al final
            t += f"{cant:<5.2f}{desc:<14}${p_u:>8.2f}${sub:>11.2f}\n"

        t += linea
        t += f"{'TOTAL A PAGAR:':<25}${total_f:>14.2f}\n"
        t += "=" * 40 + "\n"
        t += "        ¡Gracias por su compra!\n"
        t += "         Soporte: Artemisa Tech"

        # Mostrar el ticket con la clase que la impresora reconoce
        st.markdown(f'<div class="ticket-print" style="font-family: monospace; white-space: pre; font-size: 11pt; color: black; background-color: white; padding: 10px;">{t}</div>', unsafe_allow_html=True)
        
        st.write("---")
        st.success("✅ ¡Ticket alineado! Presiona **Ctrl + P**.")

    except Exception as e:
        st.error(f"Error: {e}")