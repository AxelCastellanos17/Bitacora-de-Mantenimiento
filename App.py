from datetime import datetime
import pandas as pd
import streamlit as st

# Configuración de la página web
st.set_page_config(
    page_title="Control de Mantenimientos y Bitácora",
    page_icon="🔧",
    layout="wide",
)

st.title("🔧 Sistema de Gestión y Mantenimiento de Moldes")
st.markdown("---")

# Menú lateral para separar vistas
menu = st.sidebar.selectbox(
    "Selecciona el Módulo", ["Panel del Técnico (Reportes)", "Administración"]
)

# Base de datos simulada en memoria (puedes ver y registrar al momento)
if "bitacora" not in st.session_state:
  st.session_state["bitacora"] = pd.DataFrame(
      columns=[
          "Fecha",
          "Quien_Reporta",
          "Maquina",
          "Molde",
          "Diagnostico",
          "Solucion",
          "Repuesto",
      ]
  )

# ==========================================
# 1. PANEL DEL TÉCNICO (Formulario de Uso)
# ==========================================
if menu == "Panel del Técnico (Reportes)":
  st.header("📝 Registro de Mantenimiento y Uso en Máquina")
  st.write(
      "Llena los siguientes datos tal como lo haces habitualmente en tu"
      " bitácora:"
  )

  with st.form("form_tecnico"):
    col1, col2 = st.columns(2)

    with col1:
      fecha = st.date_input("Fecha del reporte", value=datetime.today())
      quien_reporta = st.selectbox(
          "Quién reporta",
          [
              "Ismael Reyes",
              "Axel Castellanos",
              "Isaac Reyes",
              "Jonnathan Alberto",
              "Arnold",
          ],
      )
      maquina = st.selectbox(
          "Equipo / Máquina",
          [
              "Maquina 1",
              "Maquina 9",
              "Maquina 10",
              "Maquina 11",
              "Maquina 12",
              "Maquina 13",
          ],
      )

    with col2:
      molde = st.text_input(
          "Detalle de Talla / Molde (Ej. G1437 - Se bajó talla 38 y se subió"
          " 41)"
      )
      diagnostico = st.selectbox(
          "Diagnóstico / Tipo de Falla",
          [
              "Problema con Guia",
              "Problema con valvulas",
              "Defecto en Imagen",
              "Tornillo roto",
              "Mantenimiento Preventivo",
              "Otro",
          ],
      )
      repuesto = st.selectbox(
          "Repuesto o Insumos utilizados",
          ["Ninguno", "Gas", "Oxigeno", "Válvulas", "Tornillos", "Buffe"],
      )

    solucion = st.text_area(
        "Descripción del Trabajo Realizado / Solución"
    )

    submit_btn = st.form_submit_button("Guardar Reporte en el Sistema")

    if submit_btn:
      nueva_fila = pd.DataFrame({
          "Fecha": [str(fecha)],
          "Quien_Reporta": [quien_reporta],
          "Maquina": [maquina],
          "Molde": [molde],
          "Diagnostico": [diagnostico],
          "Solucion": [solucion],
          "Repuesto": [repuesto],
      })

      st.session_state["bitacora"] = pd.concat(
          [st.session_state["bitacora"], nueva_fila], ignore_index=True
      )
      st.success("¡Reporte guardado exitosamente en el sistema!")

# ==========================================
# 2. PANEL DE ADMINISTRACIÓN (Gestión)
# ==========================================
elif menu == "Administración":
  st.header("📊 Panel de Administración y Planificación")

  df_registros = st.session_state["bitacora"]

  if df_registros.empty:
    st.info(
        "Aún no hay reportes registrados en esta sesión. Ve al 'Panel del"
        " Técnico' para hacer una prueba."
    )
  else:
    c1, c2, c3 = st.columns(3)
    c1.metric("Total de Registros", len(df_registros))
    c2.metric(
        "Reportes con Repuestos",
        len(df_registros[df_registros["Repuesto"] != "Ninguno"]),
    )
    c3.metric(
        "Máquinas Registradas", df_registros["Maquina"].nunique()
    )

    st.markdown("---")
    st.subheader("Historial Completo de Mantenimientos")

    maquina_filtro = st.selectbox(
        "Filtrar por Máquina", ["Todas"] + list(df_registros["Maquina"].unique())
    )

    if maquina_filtro != "Todas":
      df_filtrado = df_registros[df_registros["Maquina"] == maquina_filtro]
    else:
      df_filtrado = df_registros

    st.dataframe(df_filtrado, use_container_width=True)
