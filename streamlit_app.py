import xml.etree.ElementTree as ET
import win32print
import win32ui
import win32con
from tkinter import filedialog, messagebox
import tkinter as tk

def obtener_texto(nodo, etiqueta):
    """Función de seguridad: si no encuentra la etiqueta, devuelve 'N/A' en vez de fallar"""
    busqueda = nodo.find(etiqueta)
    return busqueda.text.strip() if busqueda is not None and busqueda.text else "N/A"

def enviar_a_impresora(contenido_ticket):
    try:
        nombre_impresora = win32print.GetDefaultPrinter()
        hprinter = win32print.OpenPrinter(nombre_impresora)
        pdc = win32ui.CreateDC()
        pdc.CreatePrinterDC(nombre_impresora)
        pdc.StartDoc("Ticket Artemisa")
        pdc.StartPage()
        
        font = win32ui.CreateFont({"name": "Courier New", "height": 32, "weight": 400})
        pdc.SelectObject(font)
        
        y = 20
        for linea in contenido_ticket.split('\n'):
            pdc.TextOut(10, y, linea)
            y += 35 
            
        pdc.EndPage()
        pdc.EndDoc()
        pdc.DeleteDC()
        messagebox.showinfo("Éxito", "Ticket enviado.")
    except Exception as e:
        messagebox.showerror("Error de Impresora", f"{e}")

def procesar_xml():
    ruta = filedialog.askopenfilename(filetypes=[("Archivos XML", "*.xml")])
    if not ruta: return

    try:
        tree = ET.parse(ruta)
        root = tree.getroot()
        
        # El SRI a veces mete el contenido en una etiqueta 'comprobante' CDATA
        comprobante_nodo = root.find('comprobante')
        if comprobante_nodo is not None:
            f_root = ET.fromstring(comprobante_nodo.text.strip())
        else:
            f_root = root # El XML ya viene limpio

        # Buscamos secciones principales con seguridad
        tributaria = f_root.find('infoTributaria')
        factura = f_root.find('infoFactura')
        
        if tributaria is None or factura is None:
            raise ValueError("El formato del XML no es una Factura estándar del SRI.")

        emisor = obtener_texto(tributaria, 'razonSocial')
        ruc_em = obtener_texto(tributaria, 'ruc')
        cliente = obtener_texto(factura, 'razonSocialComprador')
        ruc_cl = obtener_texto(factura, 'identificacionComprador')
        fecha = obtener_texto(factura, 'fechaEmision')
        total_pago = obtener_texto(factura, 'importeTotal')

        sep = "-" * 40 + "\n"
        t = f"{emisor[:40].center(40)}\n"
        t += f"RUC: {ruc_em}\n".center(40)
        t += sep
        t += f"FECHA: {fecha}\n"
        t += f"CLIENTE: {cliente[:30]}\n"
        t += f"RUC/CI: {ruc_cl}\n"
        t += sep
        t += f"{'CANT':<5}{'DESC':<15}{'TOTAL':>18}\n"
        t += sep

        # Procesar detalles con seguridad
        for det in f_root.findall('.//detalle'):
            cant = obtener_texto(det, 'cantidad')
            desc = obtener_texto(det, 'descripcion')[:14]
            total_det = obtener_texto(det, 'precioTotalSinImpuesto')
            t += f"{cant:<5}{desc:<15}${total_det:>17}\n"

        t += sep
        t += f"{'TOTAL A PAGAR:':<20}${total_pago:>18}\n"
        t += sep
        t += "¡Gracias por su compra!".center(40)

        enviar_a_impresora(t)

    except Exception as e:
        messagebox.showerror("Error en el XML", f"Estructura no reconocida:\n{e}")

# Interfaz
app = tk.Tk()
app.title("Artemisa POS v2.0")
app.geometry("400x250")

tk.Label(app, text="Artemisa POS - Impresión Directa", font=("Arial", 12, "bold")).pack(pady=15)
tk.Button(app, text="Seleccionar y Imprimir XML", command=procesar_xml, bg="#28a745", fg="white", font=("Arial", 10, "bold"), height=2, width=30).pack()
tk.Label(app, text="Soporta formatos SRI 2024-2026", font=("Arial", 8, "italic")).pack(side="bottom", pady=10)

app.mainloop()
