from datetime import datetime, timedelta
import io
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


# CARGA DIRECTA Y ACTUALIZADA DESDE GITHUB
try:
  st.session_state["bitacora_general"] = pd.read_excel("Bitacora.xlsx")
except Exception as e:
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
      "Moldes": [{"nombre": "Molde Afectado", "tipo": "Texto Corto", "opciones": ""}],
      "Administración": [
          {"nombre": "Costo Operativo", "tipo": "Texto Corto", "opciones": ""}
      ],
  }


# ==============================================================================
# BARRA LATERAL: REPORTE RÁPIDO DE LA SEMANA (SÁBADO A SÁBADO)
# ==============================================================================
st.sidebar.markdown("---")
st.sidebar.subheader("📢 Reportes de la Semana (Sáb - Sáb)")

df_general = st.session_state["bitacora_general"]

if not df_general.empty:
  try:
    df_general["Fecha_Dt"] = pd.to_datetime(df_general["Fecha"], errors="coerce")
    hoy = datetime.today()

    dias_hasta_sabado = (5 - hoy.weekday()) % 7
    if dias_hasta_sabado == 0 and hoy.hour < 23:
      sabado_inicio = hoy - timedelta(days=7)
    else:
      sabado_inicio = hoy - timedelta(days=(hoy.weekday() - 5) % 7)

    sabado_inicio = sabado_inicio.replace(
        hour=0, minute=0, second=0, microsecond=0
    )
    sabado_fin = sabado_inicio + timedelta(days=7)

    df_semana = df_general[
        (df_general["Fecha_Dt"] >= sabado_inicio)
        & (df_general["Fecha_Dt"] < sabado_fin)
    ]

    if not df_semana.empty:
      st.sidebar.write(
          f"Del {sabado_inicio.strftime('%d/%m')} al"
          f" {sabado_fin.strftime('%d/%m')}"
      )
      for idx, row in df_semana.tail(5).iterrows():
        with st.sidebar.container():
          st.markdown(
              f"🛠️ **{row.get('Maquina', 'N/A')}**"
              f" ({row.get('Departamento', 'N/A')})"
              f"\n\n📝 *{row.get('Diagnostico', 'N/A')}*"
              f"\n\n👤 *Rep: {row.get('Quien_Reporta', 'N/A')}* | 🕒"
              f" *{row.get('Fecha', 'N/A')}*"
          )
          st.markdown("---")
    else:
      st.sidebar.info("No hay reportes en este ciclo semanal.")
  except:
    st.sidebar.info("Revisa el formato de tus fechas en Excel.")
else:
  st.sidebar.info("Esperando nuevos reportes...")


# ==============================================================================
# 1. DISEÑADOR DE FORMATOS
# ==============================================================================
if menu == "Diseñador de Formatos por Departamento":
  st.header("🛠️ Diseñador y Gestión de Formatos")

  tab1, tab2, tab3 = st.tabs(
      ["📋 Ver y Modificar Formatos", "➕ Agregar Nuevo Campo", "🏢 Crear Departamento"]
  )

  with tab1:
    depto_sel = st.selectbox(
        "Selecciona el Departamento",
        st.session_state["departamentos"],
        key="ver_depto",
    )
    st.subheader(f"Estructura del formato: {depto_sel}")
    campos_actuales = st.session_state["formatos_deptos_avanzado"].get(
        depto_sel, []
    )

    if campos_actuales:
      for idx, campo in enumerate(campos_actuales):
        with st.expander(
            f"📌 Campo {idx + 1}: {campo['nombre']} ({campo['tipo']})"
        ):
          st.write(f"**Tipo:** {campo['tipo']}")
          if campo["opciones"]:
            st.write(f"**Opciones:** {campo['opciones']}")
          if st.button(f"Eliminar campo", key=f"del_{depto_sel}_{idx}"):
            st.session_state["formatos_deptos_avanzado"][depto_sel].pop(idx)
            st.warning("¡Campo eliminado!")
            st.rerun()
    else:
      st.info("Este departamento no tiene campos personalizados.")

  with tab2:
    st.subheader("Añadir un nuevo campo")
    depto_agregar = st.selectbox(
        "Departamento", st.session_state["departamentos"], key="agregar_depto"
    )
    nombre_campo = st.text_input("Nombre de la Pregunta / Campo")
    tipo_dato = st.selectbox(
        "Tipo de Dato",
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
          "Opciones separadas por comas (Ej: Opción 1, Opción 2)"
      )

    if st.button("Guardar e Integrar"):
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
        st.success(f"¡Campo '{nombre_campo}' agregado con éxito!")
        st.rerun()
      else:
        st.error("Ingresa el nombre del campo.")

  with tab3:
    st.subheader("Crear un nuevo departamento")
    nuevo_d = st.text_input("Nombre del Departamento")
    if st.button("Registrar Departamento"):
      if nuevo_d and nuevo_d not in st.session_state["departamentos"]:
        st.session_state["departamentos"].append(nuevo_d)
        st.session_state["formatos_deptos_avanzado"][nuevo_d] = []
        st.success(f"¡Departamento '{nuevo_d}' creado!")
        st.rerun()


# ==============================================================================
# 2. PANEL DE TÉCNICO (Formulario)
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
      observaciones = st.text_area("Observaciones sobre fallas futuras")

    respuestas_dinamicas = {}
    config_campos = st.session_state["formatos_deptos_avanzado"].get(
        depto_activo, []
    )

    if config_campos:
      st.markdown("---")
      st.subheader(f"📋 Campos específicos para {depto_activo}")
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
          respuestas_dinamicals[nombre_c] = str(
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
        st.success("¡Reporte enviado y registrado con éxito!")


# ==============================================================================
# 3. PANEL DE ADMINISTRACIÓN (Con Filtros y Nombres de Técnicos Asegurados)
# ==============================================================================
elif menu == "Panel de Administración":
  st.header("📊 Panel de Administración y Control Central")

  col_desc, col_act = st.columns(2)
  with col_desc:
    df_all = st.session_state["bitacora_general"]
    if not df_all.empty:
      output = io.BytesIO()
      with pd.ExcelWriter(output, engine="openpyxl") as writer:
        df_export = df_all.drop(
            columns=[col for col in ["Fecha_Dt"] if col in df_all.columns]
        )
        df_export.to_excel(
            writer, index=False, sheet_name="Reportes_Mantenimiento"
        )
      excel_data = output.getvalue()

      st.download_button(
          label="📥 Descargar Respaldo Actualizado",
          data=excel_data,
          file_name=f"Bitacora_Mantenimiento_{datetime.today().strftime('%Y-%m-%d')}.xlsx",
          mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
      )

  with col_act:
    if st.button("🔄 Actualizar / Refrescar Datos"):
      st.rerun()

  st.markdown("---")
  df_all = st.session_state["bitacora_general"]

  # ==========================================================================
  # SECCIÓN DE FILTROS CON NOMBRES DE TÉCNICOS Y OPCIONES FIJAS
  # ==========================================================================
  st.subheader("🔍 Filtros de Búsqueda y Gráfica")

  f_col1, f_col2, f_col3 = st.columns(3)

  with f_col1:
    deptos_disponibles = (
        ["Todos"] + list(df_all["Departamento"].dropna().unique())
        if not df_all.empty and "Departamento" in df_all.columns
        else ["Todos"]
    )
    filtro_depto = st.selectbox("Filtrar por Departamento", deptos_disponibles)

    maquinas_disponibles = (
        ["Todas"]
        + [
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
        ]
        + (
            list(df_all["Maquina"].dropna().unique())
            if not df_all.empty and "Maquina" in df_all.columns
            else []
        )
    )
    # Eliminar duplicados manteniendo el orden
    maquinas_disponibles = list(dict.fromkeys(maquinas_disponibles))
    filtro_maquina = st.selectbox("Filtrar por Máquina", maquinas_disponibles)

  with f_col2:
    # Lista predeterminada de técnicos oficiales + los que vengan en el archivo
    tecnicos_oficiales = [
        "Carlos Castellanos",
        "Axel Castellanos",
        "Manuel Hernandez",
        "Bayron Enamorado",
        "Arnold Matute",
        "Ismael Castellanos",
        "Isaac Bejarano",
        "Jonathan Alberto",
        "Gabriel Rivas",
    ]
    tecnicos_en_datos = (
        list(df_all["Quien_Reporta"].dropna().unique())
        if not df_all.empty and "Quien_Reporta" in df_all.columns
        else []
    )
    tecnicos_disponibles = ["Todos"] + list(
        dict.fromkeys(tecnicos_oficiales + tecnicos_en_datos)
    )

    filtro_tecnico = st.selectbox(
        "Filtrar por Quién Reporta", tecnicos_disponibles
    )

    filtro_diag = st.text_input("Buscar en Diagnóstico", "")

  with f_col3:
    filtro_sol = st.text_input("Buscar en Solución", "")

    st.write("**Filtrar por Rango de Fechas:**")
    try:
      if not df_all.empty:
        df_all["Fecha_Temp"] = pd.to_datetime(df_all["Fecha"], errors="coerce")
        min_f = (
            df_all["Fecha_Temp"].min().date()
            if not df_all["Fecha_Temp"].isna().all()
            else datetime.today().date()
        )
        max_f = (
            df_all["Fecha_Temp"].max().date()
            if not df_all["Fecha_Temp"].isna().all()
            else datetime.today().date()
        )
        rango_fechas = st.date_input("Rango", [min_f, max_f])
      else:
        rango_fechas = st.date_input(
            "Rango", [datetime.today().date(), datetime.today().date()]
        )
    except:
      rango_fechas = []

  # APLICACIÓN DE LOS FILTROS SI HAY DATOS
  if df_all.empty:
    st.info(
        "No hay registros en el archivo Bitacora.xlsx o el archivo está vacío."
        " Sube algunos reportes desde el panel de técnico o verifica que tu"
        " archivo tenga datos."
    )
  else:
    df_view = df_all.copy()

    if filtro_depto != "Todos" and "Departamento" in df_view.columns:
      df_view = df_view[df_view["Departamento"] == filtro_depto]

    if filtro_maquina != "Todas" and "Maquina" in df_view.columns:
      df_view = df_view[df_view["Maquina"] == filtro_maquina]

    if filtro_tecnico != "Todos" and "Quien_Reporta" in df_view.columns:
      df_view = df_view[df_view["Quien_Reporta"] == filtro_tecnico]

    if filtro_diag and "Diagnostico" in df_view.columns:
      df_view = df_view[
          df_view["Diagnostico"].str.contains(filtro_diag, case=False, na=False)
      ]

    if filtro_sol and "Solucion" in df_view.columns:
      df_view = df_view[
          df_view["Solucion"].str.contains(filtro_sol, case=False, na=False)
      ]

    if len(rango_fechas) == 2 and "Fecha_Temp" in df_view.columns:
      f_inicio, f_fin = rango_fechas
      df_view = df_view[
          (df_view["Fecha_Temp"].dt.date >= f_inicio)
          & (df_view["Fecha_Temp"].dt.date <= f_fin)
      ]

    if "Fecha_Temp" in df_view.columns:
      df_view = df_view.drop(columns=["Fecha_Temp"])

    st.markdown("---")

    # MÉTRICAS DINÁMICAS
    c1, c2, c3 = st.columns(3)
    c1.metric("Reportes Filtrados", len(df_view))
    c2.metric(
        "Departamentos en Vista",
        df_view["Departamento"].nunique()
        if "Departamento" in df_view.columns
        else 0,
    )
    c3.metric(
        "Máquinas en Vista",
        df_view["Maquina"].nunique() if "Maquina" in df_view.columns else 0,
    )

    st.markdown("---")
    st.subheader("📋 Historial de Registros Filtrados")
    st.dataframe(df_view, use_container_width=True)

    # GRÁFICA DINÁMICA
    st.markdown("---")
    st.subheader("📈 Estadísticas de Fallas (Según Filtros Aplicados)")
    if not df_view.empty and "Maquina" in df_view.columns:
      conteo_maquinas = df_view["Maquina"].value_counts()
      st.bar_chart(conteo_maquinas)
    else:
      st.info(
          "No hay suficientes datos bajo los filtros seleccionados para mostrar"
          " la gráfica."
      )
