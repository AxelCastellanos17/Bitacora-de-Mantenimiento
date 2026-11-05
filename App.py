from datetime import datetime
import pandas as pd
import streamlit as st

# Configuración de la página web
st.set_page_config(
    page_title="Reporte de Fallas - Mantenimiento C.H",
    page_icon="🔧",
    layout="wide",
)

st.title("🔧 Reportes de Fallas de Maquinas C.H")
st.markdown("---")

# Menú lateral para navegar entre módulos
menu = st.sidebar.selectbox(
    "Selecciona el Módulo",
    [
        "Panel de Técnico (Reporte de Falla)",
        "Panel de Administración",
        "Diseñador de Formatos por Departamento",
    ],
)

# Base de datos general en memoria
if "bitacora_general" not in st.session_state:
  st.session_state["bitacora_general"] = pd.DataFrame(
      columns=[
          "Fecha",
          "Departamento",
          "Turno",
          "Quien_Reporta",
          "Maquina",
          "Seccion_Maquina",
          "Campo_Trabajo",
          "Diagnostico",
          "Solucion",
          "Repuesto",
          "Hora_Inicial",
          "Hora_Final",
          "Observaciones",
      ]
  )

# Departamentos y sus campos configurables
if "departamentos" not in st.session_state:
  st.session_state["departamentos"] = [
      "Departamento de Mantenimiento CH",
      "Moldes",
      "Administración",
  ]

if "formatos_deptos" not in st.session_state:
  st.session_state["formatos_deptos"] = {
      "Departamento de Mantenimiento CH": ["Portamolde", "Tiempo Muerto"],
      "Moldes": ["Molde Afectado", "Detalle de Talla"],
      "Administración": ["Costo Operativo", "Supervisor a Cargo"],
  }


# ==============================================================================
# 1. DISEÑADOR DE FORMATOS
# ==============================================================================
if menu == "Diseñador de Formatos por Departamento":
  st.header("🛠️ Diseñador y Gestor de Formatos")
  st.write(
      "Agrega o elimina campos personalizados para cada departamento según tus"
      " necesidades."
  )

  tab1, tab2 = st.tabs(["Gestionar Campos", "Crear Nuevo Departamento"])

  with tab1:
    depto_sel = st.selectbox(
        "Selecciona el Departamento", st.session_state["departamentos"]
    )
    st.write(f"Campos actuales en **{depto_sel}**:")

    campos_act = st.session_state["formatos_deptos"].get(depto_sel, [])
    for c in campos_act:
      st.markdown(f"- 📌 {c}")

    st.markdown("---")
    nuevo_c = st.text_input(f"Nuevo campo para {depto_sel}")
    if st.button("Añadir Campo"):
      if nuevo_c and nuevo_c not in campos_act:
        st.session_state["formatos_deptos"][depto_sel].append(nuevo_c)
        st.success(f"¡Campo '{nuevo_c}' agregado!")
        st.rerun()

    if campos_act:
      st.markdown("---")
      a_borrar = st.selectbox("Campo a eliminar", campos_act)
      if st.button("Eliminar Campo"):
        st.session_state["formatos_deptos"][depto_sel].remove(a_borrar)
        st.warning(f"Se eliminó el campo '{a_borrar}'.")
        st.rerun()

  with tab2:
    nuevo_d = st.text_input("Nombre del nuevo Departamento")
    if st.button("Crear Departamento"):
      if nuevo_d and nuevo_d not in st.session_state["departamentos"]:
        st.session_state["departamentos"].append(nuevo_d)
        st.session_state["formatos_deptos"][nuevo_d] = ["Observación General"]
        st.success(f"¡Departamento '{nuevo_d}' creado!")
        st.rerun()


# ==============================================================================
# 2. PANEL DE TÉCNICO (Formulario idéntico a tu Google Form)
# ==============================================================================
elif menu == "Panel de Técnico (Reporte de Falla)":
  st.header("📝 Registro de Reporte de Fallas")

  depto_activo = st.selectbox(
      "Selecciona el Departamento", st.session_state["departamentos"]
  )
  st.info(f"Formato activo para: **{depto_activo}**")

  with st.form("form_reporte_fallas"):
    col1, col2 = st.columns(2)

    with col1:
      fecha = st.date_input("Fecha", value=datetime.today())
      turno = st.selectbox("Turno", ["Turno Diurno", "Turno Nocturno"])
      quien_reporta = st.selectbox(
          "Quién Reporta",
          [
              "Carlos Castellanos",
              "Axel Castellanos",
              "Manuel Hernandez",
              "Bayron Enamorado",
              "Arnold Matute",
              "Ismael Castellanos",
              "Isaac Bejarano",
              "Jonathan Alberto",
              "Gabriel Rivas",
          ],
      )
      maquina = st.selectbox(
          "Maquina",
          [
              "Todas Las Maquinas",
              "Maquina 1",
              "Maquina 6",
              "Maquina 8",
              "Maquina 9",
              "Maquina 10",
              "Maquina 11",
              "Maquina 12",
              "Maquina 13",
              "Moldes",
              "Trabajo en Edificio",
              "Molinos C.H",
              "Molino 7G",
          ],
      )

    with col2:
      seccion_maquina = st.selectbox(
          "Sección de Maquina",
          [
              "Inyector",
              "Mesa",
              "Central Hidraulica",
              "Gabinete Electrico",
              "N/A",
          ],
      )
      campo_trabajo = st.selectbox(
          "Campo de Trabajo",
          [
              "Electrico",
              "Mecanico",
              "Hidraulico",
              "Refrigeración",
              "Procesos",
              "Neumatico",
              "N/A",
          ],
      )
      hora_inicial = st.text_input("Hora Inicial de Falla (Ej. 08:00 AM)")
      hora_final = st.text_input("Hora Final de Falla (Ej. 09:30 AM)")

    st.markdown("---")
    diagnostico = st.text_area(
        "Diagnostico o Trabajo asignado (Especifique la falla)"
    )
    solucion = st.text_area(
        "Acciones realizadas (Descripción breve del trabajo)"
    )

    col3, col4 = st.columns(2)
    with col3:
      repuesto = st.selectbox(
          "Requiere Repuesto o Insumo",
          [
              "N/A",
              "Fusibles de 6A Ceramico",
              "Fusible de 12 A Ceramico",
              "Fusible de 25 A Ceramico",
              "Tornillo M10",
              "Tornillo M12",
              "Tornillo M8",
              "Fitting de 1/8 Manguera 6",
              "Fitting de 1/4 Manguera 6",
              "Fitting de 1/8 Manguera 8",
              "Fitting de 1/4 Manguera 8",
          ],
      )
    with col4:
      observaciones = st.text_area(
          "Observaciones o sugerencias sobre fallas futuras"
      )

    # Campos dinámicos extras creados por el administrador
    extras = {}
    cfg = st.session_state["formatos_deptos"].get(depto_activo, [])
    if cfg:
      st.markdown("---")
      st.subheader(f"📋 Campos específicos para {depto_activo}")
      for fld in cfg:
        extras[fld] = st.text_input(f"Dato requerido: [{fld}]")

    enviar = st.form_submit_button("Enviar Reporte")

    if enviar:
      if not diagnostico:
        st.error("Por favor, especifica el diagnóstico de la falla.")
      else:
        fila = {
            "Fecha": str(fecha),
            "Departamento": depto_activo,
            "Turno": turno,
            "Quien_Reporta": quien_reporta,
            "Maquina": maquina,
            "Seccion_Maquina": seccion_maquina,
            "Campo_Trabajo": campo_trabajo,
            "Diagnostico": diagnostico,
            "Solucion": solucion,
            "Repuesto": repuesto,
            "Hora_Inicial": hora_inicial,
            "Hora_Final": hora_final,
            "Observaciones": observaciones,
        }
        for k, v in extras.items():
          fila[k] = v

        st.session_state["bitacora_general"] = pd.concat(
            [st.session_state["bitacora_general"], pd.DataFrame([fila])],
            ignore_index=True,
            sort=False,
        )
        st.success("¡Reporte enviado y registrado con éxito en el sistema!")


# ==============================================================================
# 3. PANEL DE ADMINISTRACIÓN
# ==============================================================================
elif menu == "Panel de Administración":
  st.header("📊 Panel de Administración y Control Central")

  df_all = st.session_state["bitacora_general"]

  if df_all.empty:
    st.info("Aún no hay reportes registrados.")
  else:
    c1, c2, c3 = st.columns(3)
    c1.metric("Total de Reportes", len(df_all))
    c2.metric("Departamentos", df_all["Departamento"].nunique())
    c3.metric("Máquinas con Falla", df_all["Maquina"].nunique())

    st.markdown("---")
    filtro = st.selectbox(
        "Filtrar por Departamento",
        ["Todos"] + list(st.session_state["departamentos"]),
    )

    if filtro != "Todos":
      df_view = df_all[df_all["Departamento"] == filtro]
    else:
      df_view = df_all

    st.dataframe(df_view, use_container_width=True)

    st.markdown("---")
    if st.button("⚠️ Borrar Base de Datos"):
      st.session_state["bitacora_general"] = pd.DataFrame(
          columns=[
              "Fecha",
              "Departamento",
              "Turno",
              "Quien_Reporta",
              "Maquina",
              "Seccion_Maquina",
              "Campo_Trabajo",
              "Diagnostico",
              "Solucion",
              "Repuesto",
              "Hora_Inicial",
              "Hora_Final",
              "Observaciones",
          ]
      )
      st.rerun()
