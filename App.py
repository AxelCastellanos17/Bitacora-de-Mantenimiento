from datetime import datetime, timedelta
import io
import os
import pandas as pd
import streamlit as st

st.set_page_config(
    page_title="Reporte de Fallas - Mantenimiento C.H",
    page_icon="🔧",
    layout="wide",
)

st.title("🔧 Sistema Integral de Reportes de Fallas C.H")
st.markdown("---")

menu = st.sidebar.selectbox(
    "Selecciona el Módulo",
    [
        "Panel de Técnico (Reporte de Falla)",
        "Panel de Administración",
        "Diseñador de Formatos por Departamento",
    ],
)

EXCEL_FILE = "Bitacora.xlsx"

if "bitacora_general" not in st.session_state:
  if os.path.exists(EXCEL_FILE):
    try:
      st.session_state["bitacora_general"] = pd.read_excel(EXCEL_FILE)
    except:
      st.session_state["bitacora_general"] = pd.DataFrame()
  else:
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
          }
      ],
      "Moldes": [{"nombre": "Molde Afectado", "tipo": "Texto Corto", "opciones": ""}],
      "Administración": [
          {"nombre": "Costo Operativo", "tipo": "Texto Corto", "opciones": ""}
      ],
  }

  st.sidebar.markdown("---")
st.sidebar.subheader("📢 Reportes de la Semana")

df_general = st.session_state["bitacora_general"]
if not df_general.empty and "Fecha" in df_general.columns:
  try:
    df_general["Fecha_Dt"] = pd.to_datetime(df_general["Fecha"], errors="coerce")
    hoy = datetime.today()
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
      for idx, row in df_semana.tail(5).iterrows():
        st.sidebar.markdown(
            f"🛠️ **{row.get('Maquina', 'N/A')}** - *{row.get('Diagnostico', 'N/A')}*"
        )
    else:
      st.sidebar.info("Sin reportes esta semana.")
  except:
    pass

if menu == "Diseñador de Formatos por Departamento":
  st.header("🛠️ Diseñador y Gestión de Formatos")
  tab1, tab2, tab3 = st.tabs(
      ["📋 Ver Formatos", "➕ Agregar Campo", "🏢 Crear Departamento"]
  )

  with tab1:
    depto_sel = st.selectbox(
        "Selecciona el Departamento", st.session_state["departamentos"]
    )
    st.subheader(f"Estructura: {depto_sel}")
    campos = st.session_state["formatos_deptos_avanzado"].get(depto_sel, [])
    if campos:
      for c in campos:
        st.write(f"📌 {c['nombre']} ({c['tipo']})")
    else:
      st.info("Sin campos personalizados.")

  with tab2:
    d_ing = st.selectbox(
        "Departamento para agregar", st.session_state["departamentos"]
    )
    n_campo = st.text_input("Nombre del Campo")
    t_dato = st.selectbox(
        "Tipo", ["Texto Corto", "Texto Largo", "Desplegable", "Fecha"]
    )
    ops = st.text_area("Opciones (si es desplegable, separadas por coma)")
    if st.button("Guardar Campo"):
      if n_campo:
        st.session_state["formatos_deptos_avanzado"][d_ing].append(
            {"nombre": n_campo, "tipo": t_dato, "opciones": ops}
        )
        st.success("¡Campo agregado!")
        st.rerun()

  with tab3:
    nuevo_dep = st.text_input("Nombre del nuevo departamento")
    if st.button("Crear Departamento"):
      if nuevo_dep and nuevo_dep not in st.session_state["departamentos"]:
        st.session_state["departamentos"].append(nuevo_dep)
        st.session_state["formatos_deptos_avanzado"][nuevo_dep] = []
        st.success(f"¡Departamento {nuevo_dep} creado!")
        st.rerun()

elif menu == "Panel de Técnico (Reporte de Falla)":
  st.header("📝 Registro de Reporte de Fallas")
  depto_activo = st.selectbox(
      "Selecciona el Departamento", st.session_state["departamentos"]
  )

  with st.form("form_falla"):
    c1, c2 = st.columns(2)
    with c1:
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
          "Máquina",
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
    with c2:
      seccion = st.selectbox(
          "Sección",
          ["Inyector", "Mesa", "Central Hidraulica", "Gabinete Electrico", "N/A"],
      )
      campo_t = st.selectbox(
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
      h_ini = st.text_input("Hora Inicial (Ej. 08:00 AM)")
      h_fin = st.text_input("Hora Final (Ej. 09:30 AM)")

    diagnostico = st.text_area("Diagnóstico de la falla")
    solucion = st.text_area("Acciones realizadas / Solución")
    repuesto = st.selectbox(
        "Requiere Repuesto", ["N/A", "Fusible 6A", "Tornillo M10"]
    )
    observaciones = st.text_area("Observaciones")

    enviar = st.form_submit_button("Enviar Reporte")
    if enviar:
      if not diagnostico:
        st.error("Escribe el diagnóstico.")
      else:
        nueva_fila = {
            "Fecha": str(fecha),
            "Departamento": depto_activo,
            "Turno": turno,
            "Quien_Reporta": quien_reporta,
            "Maquina": maquina,
            "Seccion_Maquina": seccion,
            "Campo_Trabajo": campo_t,
            "Diagnostico": diagnostico,
            "Solucion": solucion,
            "Repuesto": repuesto,
            "Hora_Inicial": h_ini,
            "Hora_Final": h_fin,
            "Observaciones": observaciones,
        }
        df_nuevo = pd.DataFrame([nueva_fila])
        st.session_state["bitacora_general"] = pd.concat(
            [st.session_state["bitacora_general"], df_nuevo],
            ignore_index=True,
        )
        try:
          st.session_state["bitacora_general"].to_excel(EXCEL_FILE, index=False)
        except Exception as ex:
          st.warning(f"Guardado local con advertencia: {ex}")
        st.success("¡Reporte enviado y guardado con éxito!")

elif menu == "Panel de Administración":
  st.header("📊 Panel de Administración y Control")

  col_d, col_a = st.columns(2)
  with col_d:
    df_all = st.session_state["bitacora_general"]
    if not df_all.empty:
      output = io.BytesIO()
      with pd.ExcelWriter(output, engine="openpyxl") as writer:
        df_all.to_excel(writer, index=False, sheet_name="Reportes")
      st.download_button(
          "📥 Descargar Respaldo Excel",
          data=output.getvalue(),
          file_name="Bitacora_Mantenimiento.xlsx",
          mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
      )

  with col_a:
    archivo_subido = st.file_uploader(
        "📂 Abrir archivo Excel de Bitácora", type=["xlsx"]
    )
    if archivo_subido is not None:
      try:
        st.session_state["bitacora_general"] = pd.read_excel(archivo_subido)
        st.success(
            f"✅ Archivo abierto ({len(st.session_state['bitacora_general'])}"
            " registros)"
        )
      except Exception as e:
        st.error(f"Error al abrir: {e}")

    if st.button("🔄 Refrescar"):
      if os.path.exists(EXCEL_FILE):
        st.session_state["bitacora_general"] = pd.read_excel(EXCEL_FILE)
      st.rerun()

  st.markdown("---")
  df_all = st.session_state["bitacora_general"]
  st.subheader("🔍 Filtros y Estadísticas")

  f1, f2 = st.columns(2)
  with f1:
    deptos = (
        ["Todos"] + list(df_all["Departamento"].dropna().unique())
        if not df_all.empty and "Departamento" in df_all.columns
        else ["Todos"]
    )
    f_dep = st.selectbox("Filtrar Departamento", deptos)
  with f2:
    maqs = (
        ["Todas"] + list(df_all["Maquina"].dropna().unique())
        if not df_all.empty and "Maquina" in df_all.columns
        else ["Todas"]
    )
    f_maq = st.selectbox("Filtrar Máquina", maqs)

  df_view = df_all.copy() if not df_all.empty else pd.DataFrame()
  if not df_view.empty:
    if f_dep != "Todos":
      df_view = df_view[df_view["Departamento"] == f_dep]
    if f_maq != "Todas":
      df_view = df_view[df_view["Maquina"] == f_maq]

  st.markdown("---")
  st.metric("Registros Encontrados", len(df_view))
  st.dataframe(df_view, use_container_width=True)

  st.markdown("---")
  st.subheader("📈 Gráfica de Fallas")
  if not df_view.empty and "Maquina" in df_view.columns:
    st.bar_chart(df_view["Maquina"].value_counts())
  else:
    df_cero = pd.DataFrame({"Máquinas": ["Sin datos"], "Cantidad": [0]}).set_index(
        "Máquinas"
    )
    st.bar_chart(df_cero)
