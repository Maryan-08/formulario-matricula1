# -*- coding: utf-8 -*-
"""Untitled3.ipynb

Automatically generated by Colab.

Original file is located at
    https://colab.research.google.com/drive/15V1oJZkmM-h4vWXs3p0GOB8yZC2YKy1O
"""

import streamlit as st
import pandas as pd
import re
from datetime import datetime, date
import os

# Configuración inicial
os.makedirs("documentos", exist_ok=True)
st.set_page_config(page_title="Formulario de Matrícula", layout="centered")
st.title("📄 Formulario de Matrícula Preescolar")

# Clave para vista administrativa
ADMIN_KEY = "admin123"
admin_view = False

# -------------------- FUNCIONES --------------------

def solo_letras(campo, etiqueta):
    if campo and not re.match(r"^[a-zA-ZáéíóúÁÉÍÓÚñÑ\s]+$", campo):
        st.warning(f"{etiqueta} solo debe contener letras.")
        return ""
    return campo.strip()

def solo_numeros(campo, etiqueta, max_len=20):
    if campo and (not campo.isdigit() or len(campo) > max_len):
        st.warning(f"{etiqueta} debe contener solo números y máximo {max_len} dígitos.")
        return ""
    return campo.strip()

def validar_archivo(file, etiqueta):
    if file is not None and file.size > 10 * 1024 * 1024:
        st.error(f"⚠️ El archivo de {etiqueta} excede los 10 MB permitidos.")
        return None
    return file

def guardar_doc(file, nombre, doc_id):
    if file:
        ext = file.name.split(".")[-1]
        archivo = f"{doc_id}_{nombre}.{ext}"
        path = os.path.join("documentos", archivo)
        with open(path, "wb") as f:
            f.write(file.read())
        return archivo
    return ""

# -------------------- FORMULARIO --------------------

with st.form("formulario"):
    st.subheader("🧒 Información del Estudiante")

    primer_nombre = solo_letras(st.text_input("Primer nombre"), "Primer nombre")
    segundo_nombre = solo_letras(st.text_input("Segundo nombre"), "Segundo nombre")
    primer_apellido = solo_letras(st.text_input("Primer apellido"), "Primer apellido")
    segundo_apellido = solo_letras(st.text_input("Segundo apellido"), "Segundo apellido")

    tipo_doc_est = st.selectbox("Tipo de documento", ["Registro Civil", "Tarjeta de Identidad", "Otro"])
    if tipo_doc_est == "Otro":
        tipo_doc_otro = solo_letras(st.text_input("Especifica otro tipo de documento"), "Tipo de documento")
        tipo_doc_est = tipo_doc_otro if tipo_doc_otro else tipo_doc_est

    num_doc_est = solo_numeros(st.text_input("Número de documento del estudiante (solo números, máx. 20 dígitos)"), "Documento del estudiante")

    fecha_nac = st.date_input("Fecha de nacimiento", min_value=date(2000, 1, 1), max_value=date.today())
    lugar_nac = st.text_input("Lugar de nacimiento").strip()
    edad = st.number_input("Edad", min_value=3, max_value=6, step=1)
    grupo_etnico = st.selectbox("Grupo étnico", ["Indígena", "Afro", "ROM", "Otro"])
    discapacidad = st.text_input("Condición especial (escriba 'Ninguna' si no aplica)").strip()
    nivel = st.selectbox("Nivel a matricular", ["Prejardín", "Jardín", "Transición"])

    st.subheader("👤 Acudiente")

    nombre_acu = solo_letras(st.text_input("Nombre completo del acudiente"), "Nombre del acudiente")
    parentesco = st.selectbox("Parentesco", ["Madre", "Padre", "Tío/a", "Abuelo/a", "Otro"])
    if parentesco == "Otro":
        parentesco_otro = solo_letras(st.text_input("Especifica el parentesco"), "Parentesco")
        parentesco = parentesco_otro if parentesco_otro else parentesco

    doc_acu = solo_numeros(st.text_input("Número de documento del acudiente"), "Documento del acudiente")
    tel = st.text_input("Teléfono de contacto").strip()
    correo = st.text_input("Correo electrónico").strip()
    direccion = st.text_input("Dirección de residencia").strip()
    barrio = st.text_input("Barrio o vereda").strip()
    estrato = st.selectbox("Estrato socioeconómico", ["1", "2", "3", "4", "5", "6"])
    vive_junto = st.radio("¿Vive con el estudiante?", ["Sí", "No"])

    st.subheader("📎 Documentos (máx. 10 MB por archivo)")

    doc_rc = validar_archivo(st.file_uploader("Registro civil", type=["pdf", "jpg", "png"]), "Registro civil")
    doc_cedula = validar_archivo(st.file_uploader("Cédula del acudiente", type=["pdf", "jpg", "png"]), "Cédula del acudiente")
    doc_eps = validar_archivo(st.file_uploader("Certificado EPS o Sisbén", type=["pdf", "jpg", "png"]), "EPS/Sisbén")
    doc_vac = validar_archivo(st.file_uploader("Certificado de vacunación", type=["pdf", "jpg", "png"]), "Vacunación")
    doc_recibo = validar_archivo(st.file_uploader("Recibo de servicio público", type=["pdf", "jpg", "png"]), "Recibo")
    doc_adicional = validar_archivo(st.file_uploader("Certificado adicional (grupo étnico/discapacidad)", type=["pdf", "jpg", "png"]), "Certificado adicional")

    enviado = st.form_submit_button("✅ Enviar inscripción")

# -------------------- VALIDACIÓN Y GUARDADO --------------------

    if enviado:
        campos_obligatorios = [
            primer_nombre, segundo_nombre, primer_apellido, segundo_apellido,
            tipo_doc_est, num_doc_est, lugar_nac, discapacidad,
            nombre_acu, parentesco, doc_acu, tel, correo, direccion, barrio
        ]
        archivos_obligatorios = [doc_rc, doc_cedula, doc_eps, doc_vac, doc_recibo]

        if "" in campos_obligatorios or any(a is None for a in archivos_obligatorios):
            st.error("⚠️ Por favor completa todos los campos y adjunta los documentos requeridos.")
        else:
            archivo_excel = "encuestas.xlsx"
            doc_ya_registrado = False
            if os.path.exists(archivo_excel):
                df_existente = pd.read_excel(archivo_excel)
                if num_doc_est in df_existente["N° doc estudiante"].astype(str).values:
                    doc_ya_registrado = True

            if doc_ya_registrado:
                st.error("⚠️ Ya existe una inscripción con ese número de documento.")
            else:
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                doc_id = f"{primer_nombre}_{primer_apellido}_{num_doc_est}_{timestamp}".replace(" ", "_")

                archivo_rc = guardar_doc(doc_rc, "registro_civil", doc_id)
                archivo_cedula = guardar_doc(doc_cedula, "cedula_acudiente", doc_id)
                archivo_eps = guardar_doc(doc_eps, "eps", doc_id)
                archivo_vac = guardar_doc(doc_vac, "vacunacion", doc_id)
                archivo_recibo = guardar_doc(doc_recibo, "recibo", doc_id)
                archivo_adicional = guardar_doc(doc_adicional, "adicional", doc_id)

                data = {
                    "Fecha": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                    "Primer nombre": primer_nombre,
                    "Segundo nombre": segundo_nombre,
                    "Primer apellido": primer_apellido,
                    "Segundo apellido": segundo_apellido,
                    "Tipo doc estudiante": tipo_doc_est,
                    "N° doc estudiante": num_doc_est,
                    "Fecha nacimiento": fecha_nac,
                    "Lugar nacimiento": lugar_nac,
                    "Edad": edad,
                    "Grupo étnico": grupo_etnico,
                    "Condición especial": discapacidad,
                    "Nivel": nivel,
                    "Nombre acudiente": nombre_acu,
                    "Parentesco": parentesco,
                    "Doc acudiente": doc_acu,
                    "Teléfono": tel,
                    "Correo": correo,
                    "Dirección": direccion,
                    "Barrio/vereda": barrio,
                    "Estrato": estrato,
                    "Vive con estudiante": vive_junto,
                    "Archivo RC": archivo_rc,
                    "Archivo EPS": archivo_eps,
                    "Archivo Cédula": archivo_cedula,
                    "Archivo Vacunación": archivo_vac,
                    "Archivo Recibo": archivo_recibo,
                    "Archivo Adicional": archivo_adicional
                }

                try:
                    df_existente = pd.read_excel(archivo_excel)
                    df_nuevo = pd.concat([df_existente, pd.DataFrame([data])], ignore_index=True)
                except FileNotFoundError:
                    df_nuevo = pd.DataFrame([data])

                df_nuevo.to_excel(archivo_excel, index=False)
                st.success("✅ Inscripción enviada correctamente.")

# -------------------- VISTA ADMIN --------------------

st.markdown("---")
clave_ingresada = st.text_input("🔒 Clave de administrador", type="password")
if clave_ingresada == ADMIN_KEY:
    st.success("🔐 Modo administrador activado.")
    try:
        df = pd.read_excel("encuestas.xlsx")
        st.subheader("📊 Registros recientes")
        st.dataframe(df.tail(10))

        with open("encuestas.xlsx", "rb") as file:
            st.download_button("📥 Descargar Excel completo", file, file_name="encuestas.xlsx")

        st.subheader("📎 Descargar documentos individuales")
        seleccion = st.selectbox("Selecciona estudiante:", df["Primer nombre"] + " " + df["Primer apellido"])
        fila = df[df["Primer nombre"] + " " + df["Primer apellido"] == seleccion].iloc[0]

        docs = {
            "Registro civil": fila.get("Archivo RC", ""),
            "Cédula acudiente": fila.get("Archivo Cédula", ""),
            "EPS o Sisbén": fila.get("Archivo EPS", ""),
            "Vacunación": fila.get("Archivo Vacunación", ""),
            "Recibo público": fila.get("Archivo Recibo", ""),
            "Certificado adicional": fila.get("Archivo Adicional", "")
        }

        for nombre, archivo in docs.items():
            ruta = os.path.join("documentos", archivo)
            if archivo and os.path.isfile(ruta):
                with open(ruta, "rb") as file:
                    st.download_button(f"📄 Descargar {nombre}", file, file_name=archivo)
            else:
                st.write(f"⚠️ {nombre}: No cargado.")

    except Exception:
        st.warning("No hay registros disponibles aún.")
else:
    if clave_ingresada and clave_ingresada != ADMIN_KEY:
        st.error("❌ Clave incorrecta. No tienes acceso a la vista administrativa.")