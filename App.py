from datetime import datetime
import pandas as pd
import streamlit as st

# Configuración de la página web
st.set_page_config(
    page_title="Sistema de Gestión y Bitácoras", page_icon="🔧", layout="wide"
)

st.title("🔧 Sistema Integral de Bitácoras y Mantenimiento")
st.markdown("---")

# Menú lateral para separar los módulos principales
menu = st.sidebar.selectbox(
    "Selecciona el Módulo",
    [
        "Panel de Técnico / Departamento",
        "Panel de Administración General",
        "Diseñador de Formatos por Departamento",
    ],
)

# Inicializar Base de Datos General de Reportes en memoria
if "bitacora_general" not in st.session_state:
  st.session_state["bitacora_general"] = pd.DataFrame(
      columns=[
          "Fecha",
          "Departamento",
          "Quien_Reporta",
          "Equipo_o_Zona",
          "Diagnostico",
          "Solucion",
          "Repuesto",
      ]
  )

# Inicializar Departamentos predeterminados y sus campos específicos
if "departamentos" not in st.session_state:
  st.session_state["departamentos"] = [
      "Moldes",
      "Mantenimiento",
      "Administración de Mantenimiento",
  ]

if "formatos_deptos" not in st.session_state:
  st.session_state["formatos_deptos"] = {
      "Moldes": ["Molde Afectado", "Detalle de Talla"],
      "Mantenimiento": ["Tipo de Falla Eléctrica/Mecánica", "Tiempo Muerto"],
      "Administración de Mantenimiento": ["Observación de Supervisor", "Costo"],
  }


# ==============================================================================
# 1. DISEÑADOR DE FORMATOS (Crear, modificar y borrar campos ordenadamente)
# ==============================================================================
if menu == "Diseñador de Formatos por Departamento":
  st.header("🛠️ Creador y Diseñador de Formatos")
  st.write(
      "Aquí puedes crear nuevos departamentos o agregar/quitar campos de los"
      " formatos."
  )

  tab1, tab2 = st.tabs(["Crear / Modificar Campos", "Crear Nuevo Departamento"])

  with tab1:
    depto_seleccionado = st.selectbox(
        "Selecciona el Departamento a configurar",
        st.session_state["departamentos"],
    )
    st.write(
        f"Campos actuales para el formato de **{depto_seleccionado}**:"
    )

    campos_actuales = st.session_state["formatos_deptos"].get(
        depto_seleccionado, []
    )

    if campos_actuales:
      for c in campos_actuales:
        st.markdown(f"- 📌 {c}")
    else:
      st.info("Este departamento no tiene campos extra configurados.")

    st.markdown("---")
    nuevo_campo = st.text_input(
        f"Agregar nuevo campo al formato de {depto_seleccionado}"
    )
    if st.button("Añadir Campo al Formato"):
      if nuevo_campo and nuevo_campo not in campos_actuales:
        st.session_state["formatos_deptos"][depto_seleccionado].append(
            nuevo_campo
        )
        st.success(
            f"¡Campo '{nuevo_campo}' agregado al formato de"
            f" {depto_seleccionado}!"
        )
        st.rerun()

    if campos_actuales:
      st.markdown("---")
      campo_a_borrar = st.selectbox(
          "Selecciona un campo para ELIMINAR", campos_actuales
      )
      if st.button("Eliminar Campo Seleccionado"):
        st.session_state["formatos_deptos"][depto_seleccionado].remove(
            campo_a_borrar
        )
        st.warning(f"Se ha eliminado el campo '{campo_a_borrar}'.")
        st.rerun()

  with tab2:
    nuevo_depto = st.text_input("Nombre del nuevo Departamento (Ej. Calidad)")
    if st.button("Crear Departamento"):
      if nuevo_depto and nuevo_depto not in st.session_state["departamentos"]:
        st.session_state["departamentos"].append(nuevo_depto)
        st.session_state["formatos_deptos"][nuevo_depto] = [
            "Observación General"
        ]
        st.success(f"¡Departamento '{nuevo_depto}' creado con éxito!")
        st.rerun()


# ==============================================================================
# 2. PANEL DE TÉCNICO / DEPARTAMENTO (Formulario Dinámico Único)
# ==============================================================================
elif menu == "Panel de Técnico / Departamento":
  st.header("📝 Registro de Reporte por Departamento")

  depto_activo = st.selectbox(
      "Selecciona tu Departamento", st.session_state["departamentos"]
  )
  st.info(f"Estás llenando el formato correspondiente a: **{depto_activo}**")

  with st.form(f"form_{depto_activo}"):
    col1, col2 = st.columns(2)

    with col1:
      fecha = st.date_input("Fecha del reporte", value=datetime.today())
      quien_reporta = st.text_input("Nombre de quien reporta")
      equipo_zona = st.text_input("Máquina / Zona / Área afectada")

    with col2:
      diagnostico = st.text_area("Diagnóstico / Descripción del problema")
      solucion = st.text_area("Solución aplicada / Trabajo realizado")
      repuesto = st.text_input("Repuestos o materiales utilizados (Opcional)")

    respuestas_extras = {}
    campos_configurados = st.session_state["formatos_deptos"].get(
        depto_activo, []
    )

    if campos_configurados:
      st.markdown("---")
      st.subheader(f"📋 Campos específicos de {depto_activo}")
      for campo in campos_configurados:
        respuestas_extras[campo] = st.text_input(f"Dato requerido: [{campo}]")

    enviar = st.form_submit_button("Guardar Reporte del Departamento")

    if enviar:
      if not quien_reporta or not equipo_zona:
        st.error(
            "Por favor, completa al menos tu nombre y la máquina/zona afectada."
        )
      else:
        fila_datos = {
            "Fecha": str(fecha),
            "Departamento": depto_activo,
            "Quien_Reporta": quien_reporta,
            "Equipo_o_Zona": equipo_zona,
            "Diagnostico": diagnostico,
            "Solucion": solucion,
            "Repuesto": (
                repuesto if repuesto else "Ninguno"
            ),
        }
        for k, v in respuestas_extras.items():
          fila_datos[k] = v

        nueva_fila_df = pd.DataFrame([fila_datos])
        st.session_state["bitacora_general"] = pd.concat(
            [st.session_state["bitacora_general"], nueva_fila_df],
            ignore_index=True,
            sort=False,
        )
        st.success(
            f"¡Reporte de {depto_activo} guardado exitosamente en el sistema!"
        )


# ==============================================================================
# 3. PANEL DE ADMINISTRACIÓN GENERAL (Ver todo centralizado)
# ==============================================================================
elif menu == "Panel de Administración General":
  st.header("📊 Panel de Administración y Control Central")

  df_total = st.session_state["bitacora_general"]

  if df_total.empty:
    st.info(
        "Aún no hay reportes registrados en ningún departamento. Usa el panel"
        " de técnico para registrar algunos."
    )
  else:
    col_m1, col_m2, col_m3 = st.columns(3)
    col_m1.metric("Total de Reportes", len(df_total))
    col_m2.metric(
        "Departamentos Activos", df_total["Departamento"].nunique()
    )
    col_m3.metric("Áreas/Máquinas Atendidas", df_total["Equipo_o_Zona"].nunique())

    st.markdown("---")
    st.subheader("Filtro y Control de Historial")

    filtro_depto = st.selectbox(
        "Filtrar vista por Departamento",
        ["Todos los Departamentos"] + list(st.session_state["departamentos"]),
    )

    if filtro_depto != "Todos los Departamentos":
      df_vista = df_total[df_total["Departamento"] == filtro_depto]
    else:
      df_vista = df_total

    st.dataframe(df_vista, use_container_width=True)

    st.markdown("---")
    if st.button("⚠️ Borrar toda la base de datos de reportes"):
      st.session_state["bitacora_general"] = pd.DataFrame(
          columns=[
              "Fecha",
              "Departamento",
              "Quien_Reporta",
              "Equipo_o_Zona",
              "Diagnostico",
              "Solucion",
              "Repuesto",
          ]
      )
      st.rerun()
