from datetime import datetime
import pandas as pd
import streamlit as st

# Configuración de la página web
st.set_page_config(
    page_title="Reporte de Fallas - Mantenimiento C.H",
    page_icon="🔧",
    layout="wide",
)

st.title("🔧 Sistema Integral de Reportes de Fallas C.H")
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

# Departamentos y estructura avanzada de formatos
if "departamentos" not in st.session_state:
  st.session_state["departamentos"] = [
      "Departamento de Mantenimiento CH",
      "Moldes",
      "Administración",
  ]

if "formatos_deptos_avanzado" not in st.session_state:
  st.session_state["formatos_deptos_avanzado"] = {
      "Departamento de Mantenimiento CH": [
          {
              "nombre": "Portamolde",
              "tipo": "Desplegable",
              "opciones": "Portalmolde 1, Portalmolde 2, N.A",
          },
      ],
      "Moldes": [
          {
              "nombre": "Molde Afectado",
              "tipo": "Texto Corto",
              "opciones": "",
          }
      ],
      "Administración": [
          {
              "nombre": "Costo Operativo",
              "tipo": "Texto Corto",
              "opciones": "",
          }
      ],
  }

# Almacenamiento temporal para las rutas o nombres de los archivos vinculados
if "archivos_config" not in st.session_state:
  st.session_state["archivos_config"] = {
      "archivo_viejos": "",
      "archivo_nuevos": "",
  }


# ==============================================================================
# 1. DISEÑADOR DE FORMATOS Y VINCULACIÓN DE ARCHIVOS
# ==============================================================================
if menu == "Diseñador de Formatos por Departamento":
  st.header("🛠️ Diseñador y Gestión de Archivos y Formatos")
  st.write(
      "Configura las preguntas, administra los departamentos y vincula los"
      " documentos para respaldar la información."
  )

  tab1, tab2, tab3, tab4 = st.tabs(
      [
          "📂 Gestión de Archivos (Viejos / Nuevos)",
          "📋 Ver y Modificar Formatos",
          "➕ Agregar Nuevo Campo",
          "🏢 Crear Departamento",
      ]
  )

  # NUEVA PESTAÑA: Botones y configuración de archivos para reportes viejos y nuevos
  with tab1:
    st.subheader("📁 Conexión de Documentos y Respaldos")
    st.write(
        "Define aquí los archivos de Google Sheets o documentos donde se"
        " administrará la información histórica y la nueva."
    )

    archivo_viejos_input = st.text_input(
        "📂 Archivo de Reportes Viejos (Historial / Google Sheets)",
        value=st.session_state["archivos_config"]["archivo_viejos"],
        placeholder=(
            "Pega el nombre o enlace de la hoja con datos anteriores"
        ),
    )

    archivo_nuevos_input = st.text_input(
        "💾 Archivo para Guardar Reportes Nuevos (Google Sheets Destino)",
        value=st.session_state["archivos_config"]["archivo_nuevos"],
        placeholder=(
            "Pega el nombre o enlace de la hoja donde se guardará lo nuevo"
        ),
    )

    if st.button("Guardar Configuración de Archivos"):
      st.session_state["archivos_config"]["archivo_viejos"] = (
          archivo_viejos_input
      )
      st.session_state["archivos_config"]["archivo_nuevos"] = (
          archivo_nuevos_input
      )
      st.success(
          "¡Los enlaces y archivos de respaldo fueron actualizados"
          " exitosamente!"
      )

    st.markdown("---")
    st.info(
        f"📌 **Archivo Viejos Actual:** "
        f"{st.session_state['archivos_config']['archivo_viejos'] or 'No definido'}"
    )
    st.info(
        f"📌 **Archivo Nuevos Actual:** "
        f"{st.session_state['archivos_config']['archivo_nuevos'] or 'No definido'}"
    )

  with tab2:
    depto_sel = st.selectbox(
        "Selecciona el Departamento para ver su formato",
        st.session_state["departamentos"],
        key="ver_depto",
    )
    st.subheader(f"Estructura actual del formato: {depto_sel}")

    campos_actuales = st.session_state["formatos_deptos_avanzado"].get(
        depto_sel, []
    )

    if campos_actuales:
      for idx, campo in enumerate(campos_actuales):
        with st.expander(
            f"📌 Campo {idx + 1}: {campo['nombre']} ({campo['tipo']})"
        ):
          st.write(f"**Tipo de Dato:** {campo['tipo']}")
          if campo["opciones"]:
            st.write(f"**Opciones / Botones:** {campo['opciones']}")
          else:
            st.write("**Opciones / Botones:** Campo de entrada libre")

          if st.button(f"Eliminar este campo", key=f"del_{depto_sel}_{idx}"):
            st.session_state["formatos_deptos_avanzado"][depto_sel].pop(idx)
            st.warning(f"¡Campo '{campo['nombre']}' eliminado con éxito!")
            st.rerun()
    else:
      st.info("Este departamento no tiene campos personalizados configurados.")

  with tab3:
    st.subheader("Añadir un nuevo campo con opciones predeterminadas")
    depto_agregar = st.selectbox(
        "Departamento al que deseas agregar el campo",
        st.session_state["departamentos"],
        key="agregar_depto",
    )

    nombre_campo = st.text_input("Nombre de la Pregunta / Campo")
    tipo_dato = st.selectbox(
        "Selecciona el Tipo de Dato",
        [
            "Texto Corto",
            "Texto Largo (Párrafo)",
            "Desplegable (Opciones/Botones)",
            "Fecha",
        ],
    )

    opciones_campo = ""
    if tipo_dato == "Desplegable (Opciones/Botones)":
      opciones_campo = st.text_area(
          "Escribe las opciones separadas por comas (Ej: Opción 1, Opción 2)"
      )

    if st.button("Guardar e Integrar al Formato"):
      if nombre_campo:
        nuevo_item = {
            "nombre": nombre_campo,
            "tipo": tipo_dato,
            "opciones": opciones_campo,
        }
        if depto_agregar not in st.session_state["formatos_deptos_avanzado"]:
          st.session_state["formatos_deptos_avanzado"][depto_agregar] = []

        st.session_state["formatos_deptos_avanzado"][depto_agregar].append(
            nuevo_item
        )
        st.success(
            f"¡El campo '{nombre_campo}' fue agregado exitosamente al"
            f" formato de {depto_agregar}!"
        )
        st.rerun()
      else:
        st.error("Por favor, ingresa el nombre del campo.")

  with tab4:
    st.subheader("Crear un nuevo departamento")
    nuevo_d = st.text_input(
        "Nombre del nuevo Departamento (Ej. Control de Calidad)"
    )
    if st.button("Registrar Departamento"):
      if nuevo_d and nuevo_d not in st.session_state["departamentos"]:
        st.session_state["departamentos"].append(nuevo_d)
        st.session_state["formatos_deptos_avanzado"][nuevo_d] = []
        st.success(f"¡Departamento '{nuevo_d}' creado con éxito!")
        st.rerun()


# ==============================================================================
# 2. PANEL DE TÉCNICO (Formulario Dinámico Inteligente)
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
          ],
      )
    with col4:
      observaciones = st.text_area(
          "Observaciones o sugerencias sobre fallas futuras"
      )

    respuestas_dinamicas = {}
    config_campos = st.session_state["formatos_deptos_avanzado"].get(
        depto_activo, []
    )

    if config_campos:
      st.markdown("---")
      st.subheader(f"📋 Campos específicos configurados para {depto_activo}")
      for campo in config_campos:
        nombre_c = campo["nombre"]
        tipo_c = campo["tipo"]
        ops_c = campo["opciones"]

        if tipo_c == "Texto Corto":
          respuestas_dinamicas[nombre_c] = st.text_input(f"{nombre_c}")
        elif tipo_c == "Texto Largo (Párrafo)":
          respuestas_dinamicas[nombre_c] = st.text_area(f"{nombre_c}")
        elif tipo_c == "Desplegable (Opciones/Botones)":
          lista_opciones = (
              [op.strip() for op in ops_c.split(",")] if ops_c else ["N/A"]
          )
          respuestas_dinamicas[nombre_c] = st.selectbox(
              f"{nombre_c}", lista_opciones
          )
        elif tipo_c == "Fecha":
          respuestas_dinamicas[nombre_c] = str(
              st.date_input(f"{nombre_c}", value=datetime.today())
          )

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
        for k, v in respuestas_dinamicas.items():
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
