from datetime import datetime
import io
import os
import pandas as pd
import plotly.graph_objects as go
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

# ENLACE CSV DE GOOGLE SHEETS
GOOGLE_SHEET_CSV_URL = "https://docs.google.com/spreadsheets/d/e/2PACX-1vSH5iUS_32swVnDY1r7_1WcUagclXiaERsSplqKazMPSPeOfAN214d6DR5e1wLjLr_YO5HYJgB43F9P/pub?gid=1350106078&single=true&output=csv"


# FUNCIÓN PARA CALCULAR SEGUNDOS, MINUTOS Y HORAS DECIMALES
def calcular_tiempo_falla(df):
  try:
    if "Hora_Inicial" in df.columns and "Hora_Final" in df.columns:
      t_ini = pd.to_datetime(
          df["Hora_Inicial"], errors="coerce", format="mixed"
      )
      t_fin = pd.to_datetime(df["Hora_Final"], errors="coerce", format="mixed")

      diferencia = t_fin - t_ini
      diferencia = diferencia.apply(
          lambda x: (
              x + pd.Timedelta(days=1)
              if pd.notna(x) and x.total_seconds() < 0
              else x
          )
      )

      df["_Segundos_Totales"] = diferencia.dt.total_seconds().fillna(0)
      df["Minutos_Muertos"] = df["_Segundos_Totales"] / 60
      df["Horas_Decimales"] = df["_Segundos_Totales"] / 3600
    else:
      df["_Segundos_Totales"] = 0
      df["Minutos_Muertos"] = 0
      df["Horas_Decimales"] = 0
  except Exception:
    df["_Segundos_Totales"] = 0
    df["Minutos_Muertos"] = 0
    df["Horas_Decimales"] = 0
  return df


# FUNCIÓN DE CONVERSIÓN Y LIMPIEZA
def cargar_y_limpiar_datos(fuente):
  try:
    if isinstance(fuente, str) and fuente.startswith("http"):
      df = pd.read_csv(fuente, encoding="utf-8")
    elif isinstance(fuente, str) and os.path.exists(fuente):
      df = pd.read_excel(fuente)
    elif hasattr(fuente, "name"):
      nombre = fuente.name.lower()
      if nombre.endswith(".csv"):
        df = pd.read_csv(fuente, encoding="latin-1")
      else:
        df = pd.read_excel(fuente)
    else:
      df = pd.DataFrame(fuente)

    if df.empty:
      return pd.DataFrame()

    df.columns = df.columns.astype(str).str.strip()

    mapa_columnas = {
        "maquina": "Maquina",
        "máquina": "Maquina",
        "equipos": "Maquina",
        "equipo": "Maquina",
        "fecha": "Fecha",
        "dia": "Fecha",
        "turno": "Turno",
        "quien reporta": "Quien_Reporta",
        "reporta": "Quien_Reporta",
        "técnico": "Quien_Reporta",
        "tecnico": "Quien_Reporta",
        "diagnostico": "Diagnostico",
        "diagnóstico": "Diagnostico",
        "falla": "Diagnostico",
        "descripcion": "Diagnostico",
        "descripción de falla": "Diagnostico",
        "solucion": "Solucion",
        "solución": "Solucion",
        "tiempo de falla": "Tiempo de Falla",
        "tiempo muerto": "Tiempo de Falla",
        "hora inicial de falla": "Hora_Inicial",
        "hora inici": "Hora_Inicial",
        "hora final de falla": "Hora_Final",
    }

    nuevo_mapeo = {}
    for col in df.columns:
      col_lower = col.lower()
      if col_lower in mapa_columnas:
        nuevo_mapeo[col] = mapa_columnas[col_lower]
    df = df.rename(columns=nuevo_mapeo)

    for col in df.columns:
      df[col] = df[col].astype(str).str.strip()
      df[col] = df[col].replace(
          ["nan", "None", "NAT", "NaT", "NaN", ""], "N/A"
      )

    columnas_requeridas = [
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
        "Tiempo de Falla",
    ]

    for col in columnas_requeridas:
      if col not in df.columns:
        if col == "Tiempo de Falla":
          df[col] = "00:00:00"
        else:
          df[col] = "N/A"

    df = calcular_tiempo_falla(df)
    return df
  except Exception as e:
    return pd.DataFrame()


# PERSISTENCIA AUTOMÁTICA CON GOOGLE SHEETS
if "bitacora_general" not in st.session_state:
  if GOOGLE_SHEET_CSV_URL.strip() != "":
    st.session_state["bitacora_general"] = cargar_y_limpiar_datos(
        GOOGLE_SHEET_CSV_URL
    )
    st.session_state["fuente_activa"] = "Google Sheets (Sincronizado)"
  else:
    st.session_state["bitacora_general"] = pd.DataFrame()
    st.session_state["fuente_activa"] = "Sin fuente configurada"

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

# 1. DISEÑADOR DE FORMATOS
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

# 2. PANEL DE TÉCNICO
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
            "Tiempo de Falla": "01:00:00",
        }
        df_nuevo = pd.DataFrame([nueva_fila])
        df_nuevo = calcular_tiempo_falla(df_nuevo)
        st.session_state["bitacora_general"] = pd.concat(
            [st.session_state["bitacora_general"], df_nuevo],
            ignore_index=True,
        )
        st.success("¡Reporte agregado con éxito a la sesión actual!")

# 3. PANEL DE ADMINISTRACIÓN
elif menu == "Panel de Administración":
  st.header("📊 Panel de Administración y Control")

  df_all = st.session_state["bitacora_general"]
  total_reg = len(df_all)

  # Barra superior compacta
  b1, b2, b3 = st.columns([2, 1, 1])
  with b1:
    st.caption(f"🟢 **Google Sheets:** {total_reg} registros sincronizados")
  with b2:
    if st.button("🔄 Sincronizar", use_container_width=True):
      if GOOGLE_SHEET_CSV_URL.strip() != "":
        st.session_state["bitacora_general"] = cargar_y_limpiar_datos(
            GOOGLE_SHEET_CSV_URL
        )
        st.success("¡Actualizado!")
        st.rerun()
  with b3:
    if not df_all.empty:
      output = io.BytesIO()
      with pd.ExcelWriter(output, engine="openpyxl") as writer:
        df_all.to_excel(writer, index=False, sheet_name="Reportes")
      st.download_button(
          "📥 Descargar Excel",
          data=output.getvalue(),
          file_name="Bitacora_Mantenimiento.xlsx",
          mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
          use_container_width=True,
      )

  # ============================================================================
  # PANEL DE FILTROS Y CONFIGURACIÓN (COMPACTO Y BLINDAD
  # ============================================================================
  columnas_disponibles = (
      list(df_all.columns)
      if not df_all.empty
      else [
          "Semana",
          "Fecha",
          "Turno",
          "Maquina",
          "Quien_Reporta",
          "Descripción de Falla",
      ]
  )

  with st.expander("🎛️ Filtros y Configuración de Matriz", expanded=True):
    sc1, sc2, sc3 = st.columns(3)
    with sc1:
      col_filas = st.selectbox(
          "Filas",
          columnas_disponibles,
          index=(
              columnas_disponibles.index("Maquina")
              if "Maquina" in columnas_disponibles
              else 0
          ),
          label_visibility="collapsed",
      )
    with sc2:
      col_columnas = st.selectbox(
          "Columnas",
          columnas_disponibles,
          index=(
              columnas_disponibles.index("Fecha")
              if "Fecha" in columnas_disponibles
              else 0
          ),
          label_visibility="collapsed",
      )
    with sc3:
      opciones_valores = [
          "Horas_Decimales",
          "_Segundos_Totales",
          "Minutos_Muertos",
      ] + [
          c
          for c in columnas_disponibles
          if c not in ["Horas_Decimales", "_Segundos_Totales", "Minutos_Muertos"]
      ]
      col_valor = st.selectbox(
          "Valores", opciones_valores, index=0, label_visibility="collapsed"
      )

    # Preparar datos temporales seguros con columnas auxiliares garantizadas
    df_temp_filtro = df_all.copy()
    if not df_temp_filtro.empty and col_columnas in df_temp_filtro.columns:
      df_temp_filtro["_dt_temp"] = pd.to_datetime(
          df_temp_filtro[col_columnas], errors="coerce"
      )
      df_temp_filtro["_Anio"] = df_temp_filtro["_dt_temp"].dt.year.apply(
          lambda x: str(int(x)) if pd.notna(x) and x >= 2000 else "(Sin fecha)"
      )
      df_temp_filtro["_Mes"] = (
          df_temp_filtro["_dt_temp"]
          .dt.strftime("%B")
          .fillna("Mes no especificado")
      )
    else:
      df_temp_filtro["_Anio"] = "(Sin fecha)"
      df_temp_filtro["_Mes"] = "Mes no especificado"

    fc1, fc2, fc3, fc4 = st.columns(4)

    with fc1:
      maquinas_disponibles = (
          sorted(list(df_all[col_filas].dropna().astype(str).unique()))
          if not df_all.empty and col_filas in df_all.columns
          else []
      )
      maq_seleccionadas = st.multiselect(
          "Máquinas",
          options=maquinas_disponibles,
          default=[],
          placeholder="Todas las máquinas",
      )

    with fc2:
      anios_disp = (
          sorted(list(df_temp_filtro["_Anio"].dropna().astype(str).unique()))
          if not df_temp_filtro.empty
          else []
      )
      anio_elegido = st.selectbox(
          "Año", options=["(Todos los años)"] + anios_disp, index=0
      )

      meses_seleccionados = []
      dias_seleccionados = []
      if anio_elegido != "(Todos los años)":
        df_anio_filtrado = df_temp_filtro[
            df_temp_filtro["_Anio"] == anio_elegido
        ]
        meses_disp = sorted(
            list(df_anio_filtrado["_Mes"].dropna().astype(str).unique())
        )
        meses_seleccionados = st.multiselect(
            "Mes(es)", options=meses_disp, default=[], placeholder="Todos"
        )
        if meses_seleccionados:
          df_mes_filtrado = df_anio_filtrado[
              df_anio_filtrado["_Mes"].isin(meses_seleccionados)
          ]
          dias_disp = sorted(
              list(df_mes_filtrado[col_columnas].dropna().astype(str).unique())
          )
          dias_seleccionados = st.multiselect(
              "Días", options=dias_disp, default=[], placeholder="Todos"
          )

    with fc3:
      turno_opts = (
          sorted(list(df_all["Turno"].dropna().astype(str).unique()))
          if not df_all.empty and "Turno" in df_all.columns
          else []
      )
      f_turno = st.selectbox(
          "Turno", options=["(Todos)"] + turno_opts, index=0
      )

      reporta_opts = (
          sorted(list(df_all["Quien_Reporta"].dropna().astype(str).unique()))
          if not df_all.empty and "Quien_Reporta" in df_all.columns
          else []
      )
      rep_seleccionados = st.multiselect(
          "Quién Reporta",
          options=reporta_opts,
          default=[],
          placeholder="Todos",
      )

    with fc4:
      texto_busqueda = st.text_input(
          "Búsqueda rápida", "", placeholder="Diagnóstico / Solución..."
      )

  # Aplicar filtros al DataFrame de forma completamente segura (evitando KeyError)
  df_view = df_temp_filtro.copy() if not df_temp_filtro.empty else pd.DataFrame()
  if not df_view.empty:
    if maq_seleccionadas and col_filas in df_view.columns:
      df_view = df_view[
          df_view[col_filas].astype(str).isin(maq_seleccionadas)
      ]

    if dias_seleccionados and col_columnas in df_view.columns:
      df_view = df_view[
          df_view[col_columnas].astype(str).isin(dias_seleccionados)
      ]
    elif anio_elegido != "(Todos los años)":
      df_view = df_view[df_view["_Anio"] == anio_elegido]
      if meses_seleccionados:
        df_view = df_view[df_view["_Mes"].isin(meses_seleccionados)]

    if f_turno != "(Todos)" and "Turno" in df_view.columns:
      df_view = df_view[df_view["Turno"].astype(str) == f_turno]

    if rep_seleccionados and "Quien_Reporta" in df_view.columns:
      df_view = df_view[
          df_view["Quien_Reporta"].astype(str).isin(rep_seleccionados)
      ]

    if texto_busqueda:
      mask = (
          df_view.astype(str)
          .apply(lambda x: x.str.contains(texto_busqueda, case=False, na=False))
          .any(axis=1)
      )
      df_view = df_view[mask]

  st.markdown("---")
  st.subheader("📋 Matriz de Tiempo Reportado")

  tabla_numerica = pd.DataFrame()
  if (
      not df_view.empty
      and col_filas in df_view.columns
      and col_columnas in df_view.columns
      and col_valor in df_view.columns
  ):
    try:
      # 1. Base numérica exacta
      tabla_numerica = pd.pivot_table(
          df_view,
          index=col_filas,
          columns=col_columnas,
          values=col_valor,
          aggfunc="sum",
          fill_value=0,
      )
      tabla_numerica["Total General"] = tabla_numerica.sum(axis=1)
      total_columna_num = pd.DataFrame(tabla_numerica.sum(axis=0)).T
      total_columna_num.index = ["Total General"]
      tabla_numerica = pd.concat([tabla_numerica, total_columna_num])

      # 2. Convertimos los valores a formato [H]:mm:ss para la tabla visual
      def convertir_a_hms_formato_excel(val):
        if pd.isna(val) or val <= 0:
          return "00:00:00"
        segundos = val * 3600 if col_valor == "Horas_Decimales" else val
        horas = int(segundos // 3600)
        minutos = int((segundos % 3600) // 60)
        segs = int(segundos % 60)
        return f"{horas:02d}:{minutos:02d}:{segs:02d}"

      tabla_formateada = tabla_numerica.map(convertir_a_hms_formato_excel)
      st.dataframe(tabla_formateada, use_container_width=True)

    except Exception as ex:
      st.warning(f"No se pudo generar la tabla cruzada: {ex}")
      st.dataframe(df_view, use_container_width=True)
  else:
    st.info("No hay datos que coincidan con los filtros seleccionados.")

  st.markdown("---")
  st.subheader("📈 Gráfica Apilada"="from datetime import datetime
import io
import os
import pandas as pd
import plotly.graph_objects as go
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

# ENLACE CSV DE GOOGLE SHEETS
GOOGLE_SHEET_CSV_URL = "https://docs.google.com/spreadsheets/d/e/2PACX-1vSH5iUS_32swVnDY1r7_1WcUagclXiaERsSplqKazMPSPeOfAN214d6DR5e1wLjLr_YO5HYJgB43F9P/pub?gid=1350106078&single=true&output=csv"


# FUNCIÓN PARA CALCULAR SEGUNDOS, MINUTOS Y HORAS DECIMALES
def calcular_tiempo_falla(df):
  try:
    if "Hora_Inicial" in df.columns and "Hora_Final" in df.columns:
      t_ini = pd.to_datetime(
          df["Hora_Inicial"], errors="coerce", format="mixed"
      )
      t_fin = pd.to_datetime(df["Hora_Final"], errors="coerce", format="mixed")

      diferencia = t_fin - t_ini
      diferencia = diferencia.apply(
          lambda x: (
              x + pd.Timedelta(days=1)
              if pd.notna(x) and x.total_seconds() < 0
              else x
          )
      )

      df["_Segundos_Totales"] = diferencia.dt.total_seconds().fillna(0)
      df["Minutos_Muertos"] = df["_Segundos_Totales"] / 60
      df["Horas_Decimales"] = df["_Segundos_Totales"] / 3600
    else:
      df["_Segundos_Totales"] = 0
      df["Minutos_Muertos"] = 0
      df["Horas_Decimales"] = 0
  except Exception:
    df["_Segundos_Totales"] = 0
    df["Minutos_Muertos"] = 0
    df["Horas_Decimales"] = 0
  return df


# FUNCIÓN DE CONVERSIÓN Y LIMPIEZA
def cargar_y_limpiar_datos(fuente):
  try:
    if isinstance(fuente, str) and fuente.startswith("http"):
      df = pd.read_csv(fuente, encoding="utf-8")
    elif isinstance(fuente, str) and os.path.exists(fuente):
      df = pd.read_excel(fuente)
    elif hasattr(fuente, "name"):
      nombre = fuente.name.lower()
      if nombre.endswith(".csv"):
        df = pd.read_csv(fuente, encoding="latin-1")
      else:
        df = pd.read_excel(fuente)
    else:
      df = pd.DataFrame(fuente)

    if df.empty:
      return pd.DataFrame()

    df.columns = df.columns.astype(str).str.strip()

    mapa_columnas = {
        "maquina": "Maquina",
        "máquina": "Maquina",
        "equipos": "Maquina",
        "equipo": "Maquina",
        "fecha": "Fecha",
        "dia": "Fecha",
        "turno": "Turno",
        "quien reporta": "Quien_Reporta",
        "reporta": "Quien_Reporta",
        "técnico": "Quien_Reporta",
        "tecnico": "Quien_Reporta",
        "diagnostico": "Diagnostico",
        "diagnóstico": "Diagnostico",
        "falla": "Diagnostico",
        "descripcion": "Diagnostico",
        "descripción de falla": "Diagnostico",
        "solucion": "Solucion",
        "solución": "Solucion",
        "tiempo de falla": "Tiempo de Falla",
        "tiempo muerto": "Tiempo de Falla",
        "hora inicial de falla": "Hora_Inicial",
        "hora inici": "Hora_Inicial",
        "hora final de falla": "Hora_Final",
    }

    nuevo_mapeo = {}
    for col in df.columns:
      col_lower = col.lower()
      if col_lower in mapa_columnas:
        nuevo_mapeo[col] = mapa_columnas[col_lower]
    df = df.rename(columns=nuevo_mapeo)

    for col in df.columns:
      df[col] = df[col].astype(str).str.strip()
      df[col] = df[col].replace(
          ["nan", "None", "NAT", "NaT", "NaN", ""], "N/A"
      )

    columnas_requeridas = [
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
        "Tiempo de Falla",
    ]

    for col in columnas_requeridas:
      if col not in df.columns:
        if col == "Tiempo de Falla":
          df[col] = "00:00:00"
        else:
          df[col] = "N/A"

    df = calcular_tiempo_falla(df)
    return df
  except Exception as e:
    return pd.DataFrame()


# PERSISTENCIA AUTOMÁTICA CON GOOGLE SHEETS
if "bitacora_general" not in st.session_state:
  if GOOGLE_SHEET_CSV_URL.strip() != "":
    st.session_state["bitacora_general"] = cargar_y_limpiar_datos(
        GOOGLE_SHEET_CSV_URL
    )
    st.session_state["fuente_activa"] = "Google Sheets (Sincronizado)"
  else:
    st.session_state["bitacora_general"] = pd.DataFrame()
    st.session_state["fuente_activa"] = "Sin fuente configurada"

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

# 1. DISEÑADOR DE FORMATOS
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

# 2. PANEL DE TÉCNICO
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
            "Tiempo de Falla": "01:00:00",
        }
        df_nuevo = pd.DataFrame([nueva_fila])
        df_nuevo = calcular_tiempo_falla(df_nuevo)
        st.session_state["bitacora_general"] = pd.concat(
            [st.session_state["bitacora_general"], df_nuevo],
            ignore_index=True,
        )
        st.success("¡Reporte agregado con éxito a la sesión actual!")

# 3. PANEL DE ADMINISTRACIÓN
elif menu == "Panel de Administración":
  st.header("📊 Panel de Administración y Control")

  df_all = st.session_state["bitacora_general"]
  total_reg = len(df_all)

  # Barra superior compacta
  b1, b2, b3 = st.columns([2, 1, 1])
  with b1:
    st.caption(f"🟢 **Google Sheets:** {total_reg} registros sincronizados")
  with b2:
    if st.button("🔄 Sincronizar", use_container_width=True):
      if GOOGLE_SHEET_CSV_URL.strip() != "":
        st.session_state["bitacora_general"] = cargar_y_limpiar_datos(
            GOOGLE_SHEET_CSV_URL
        )
        st.success("¡Actualizado!")
        st.rerun()
  with b3:
    if not df_all.empty:
      output = io.BytesIO()
      with pd.ExcelWriter(output, engine="openpyxl") as writer:
        df_all.to_excel(writer, index=False, sheet_name="Reportes")
      st.download_button(
          "📥 Descargar Excel",
          data=output.getvalue(),
          file_name="Bitacora_Mantenimiento.xlsx",
          mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
          use_container_width=True,
      )

  # ============================================================================
  # PANEL DE FILTROS Y CONFIGURACIÓN (COMPACTO Y BLINDADO)
  # ============================================================================
  columnas_disponibles = (
      list(df_all.columns)
      if not df_all.empty
      else [
          "Semana",
          "Fecha",
          "Turno",
          "Maquina",
          "Quien_Reporta",
          "Descripción de Falla",
      ]
  )

  with st.expander("🎛️ Filtros y Configuración de Matriz", expanded=True):
    sc1, sc2, sc3 = st.columns(3)
    with sc1:
      col_filas = st.selectbox(
          "Filas",
          columnas_disponibles,
          index=(
              columnas_disponibles.index("Maquina")
              if "Maquina" in columnas_disponibles
              else 0
          ),
          label_visibility="collapsed",
      )
    with sc2:
      col_columnas = st.selectbox(
          "Columnas",
          columnas_disponibles,
          index=(
              columnas_disponibles.index("Fecha")
              if "Fecha" in columnas_disponibles
              else 0
          ),
          label_visibility="collapsed",
      )
    with sc3:
      opciones_valores = [
          "Horas_Decimales",
          "_Segundos_Totales",
          "Minutos_Muertos",
      ] + [
          c
          for c in columnas_disponibles
          if c not in ["Horas_Decimales", "_Segundos_Totales", "Minutos_Muertos"]
      ]
      col_valor = st.selectbox(
          "Valores", opciones_valores, index=0, label_visibility="collapsed"
      )

    # Preparar datos temporales seguros con columnas auxiliares garantizadas
    df_temp_filtro = df_all.copy()
    if not df_temp_filtro.empty and col_columnas in df_temp_filtro.columns:
      df_temp_filtro["_dt_temp"] = pd.to_datetime(
          df_temp_filtro[col_columnas], errors="coerce"
      )
      df_temp_filtro["_Anio"] = df_temp_filtro["_dt_temp"].dt.year.apply(
          lambda x: str(int(x)) if pd.notna(x) and x >= 2000 else "(Sin fecha)"
      )
      df_temp_filtro["_Mes"] = (
          df_temp_filtro["_dt_temp"]
          .dt.strftime("%B")
          .fillna("Mes no especificado")
      )
    else:
      df_temp_filtro["_Anio"] = "(Sin fecha)"
      df_temp_filtro["_Mes"] = "Mes no especificado"

    fc1, fc2, fc3, fc4 = st.columns(4)

    with fc1:
      maquinas_disponibles = (
          sorted(list(df_all[col_filas].dropna().astype(str).unique()))
          if not df_all.empty and col_filas in df_all.columns
          else []
      )
      maq_seleccionadas = st.multiselect(
          "Máquinas",
          options=maquinas_disponibles,
          default=[],
          placeholder="Todas las máquinas",
      )

    with fc2:
      anios_disp = (
          sorted(list(df_temp_filtro["_Anio"].dropna().astype(str).unique()))
          if not df_temp_filtro.empty
          else []
      )
      anio_elegido = st.selectbox(
          "Año", options=["(Todos los años)"] + anios_disp, index=0
      )

      meses_seleccionados = []
      dias_seleccionados = []
      if anio_elegido != "(Todos los años)":
        df_anio_filtrado = df_temp_filtro[
            df_temp_filtro["_Anio"] == anio_elegido
        ]
        meses_disp = sorted(
            list(df_anio_filtrado["_Mes"].dropna().astype(str).unique())
        )
        meses_seleccionados = st.multiselect(
            "Mes(es)", options=meses_disp, default=[], placeholder="Todos"
        )
        if meses_seleccionados:
          df_mes_filtrado = df_anio_filtrado[
              df_anio_filtrado["_Mes"].isin(meses_seleccionados)
          ]
          dias_disp = sorted(
              list(df_mes_filtrado[col_columnas].dropna().astype(str).unique())
          )
          dias_seleccionados = st.multiselect(
              "Días", options=dias_disp, default=[], placeholder="Todos"
          )

    with fc3:
      turno_opts = (
          sorted(list(df_all["Turno"].dropna().astype(str).unique()))
          if not df_all.empty and "Turno" in df_all.columns
          else []
      )
      f_turno = st.selectbox(
          "Turno", options=["(Todos)"] + turno_opts, index=0
      )

      reporta_opts = (
          sorted(list(df_all["Quien_Reporta"].dropna().astype(str).unique()))
          if not df_all.empty and "Quien_Reporta" in df_all.columns
          else []
      )
      rep_seleccionados = st.multiselect(
          "Quién Reporta",
          options=reporta_opts,
          default=[],
          placeholder="Todos",
      )

    with fc4:
      texto_busqueda = st.text_input(
          "Búsqueda rápida", "", placeholder="Diagnóstico / Solución..."
      )

  # Aplicar filtros al DataFrame de forma completamente segura (evitando KeyError)
  df_view = df_temp_filtro.copy() if not df_temp_filtro.empty else pd.DataFrame()
  if not df_view.empty:
    if maq_seleccionadas and col_filas in df_view.columns:
      df_view = df_view[
          df_view[col_filas].astype(str).isin(maq_seleccionadas)
      ]

    if dias_seleccionados and col_columnas in df_view.columns:
      df_view = df_view[
          df_view[col_columnas].astype(str).isin(dias_seleccionados)
      ]
    elif anio_elegido != "(Todos los años)":
      df_view = df_view[df_view["_Anio"] == anio_elegido]
      if meses_seleccionados:
        df_view = df_view[df_view["_Mes"].isin(meses_seleccionados)]

    if f_turno != "(Todos)" and "Turno" in df_view.columns:
      df_view = df_view[df_view["Turno"].astype(str) == f_turno]

    if rep_seleccionados and "Quien_Reporta" in df_view.columns:
      df_view = df_view[
          df_view["Quien_Reporta"].astype(str).isin(rep_seleccionados)
      ]

    if texto_busqueda:
      mask = (
          df_view.astype(str)
          .apply(lambda x: x.str.contains(texto_busqueda, case=False, na=False))
          .any(axis=1)
      )
      df_view = df_view[mask]

  st.markdown("---")
  st.subheader("📋 Matriz de Tiempo Muerto (Formato Estilo [H]:mm:ss)")

  tabla_numerica = pd.DataFrame()
  if (
      not df_view.empty
      and col_filas in df_view.columns
      and col_columnas in df_view.columns
      and col_valor in df_view.columns
  ):
    try:
      # 1. Base numérica exacta
      tabla_numerica = pd.pivot_table(
          df_view,
          index=col_filas,
          columns=col_columnas,
          values=col_valor,
          aggfunc="sum",
          fill_value=0,
      )
      tabla_numerica["Total General"] = tabla_numerica.sum(axis=1)
      total_columna_num = pd.DataFrame(tabla_numerica.sum(axis=0)).T
      total_columna_num.index = ["Total General"]
      tabla_numerica = pd.concat([tabla_numerica, total_columna_num])

      # 2. Convertimos los valores a formato [H]:mm:ss para la tabla visual
      def convertir_a_hms_formato_excel(val):
        if pd.isna(val) or val <= 0:
          return "00:00:00"
        segundos = val * 3600 if col_valor == "Horas_Decimales" else val
        horas = int(segundos // 3600)
        minutos = int((segundos % 3600) // 60)
        segs = int(segundos % 60)
        return f"{horas:02d}:{minutos:02d}:{segs:02d}"

      tabla_formateada = tabla_numerica.map(convertir_a_hms_formato_excel)
      st.dataframe(tabla_formateada, use_container_width=True)

    except Exception as ex:
      st.warning(f"No se pudo generar la tabla cruzada: {ex}")
      st.dataframe(df_view, use_container_width=True)
  else:
    st.info("No hay datos que coincidan con los filtros seleccionados.")

  st.markdown("---")
  st.subheader("📈 Gráfica Apilada de Tiempo Reportado")

  if not tabla_numerica.empty:
    # 3. Preparamos la gráfica de barras apiladas directamente desde la matriz
    df_grafica = tabla_numerica.drop(index=["Total General"], errors="ignore")
    if "Total General" in df_grafica.columns:
      df_grafica = df_grafica.drop(columns=["Total General"], errors="ignore")

    if col_valor != "Horas_Decimales":
      df_grafica = df_grafica / 3600

    df_grafica = df_grafica.apply(pd.to_numeric, errors="coerce").fillna(0)

    if not df_grafica.empty and df_grafica.sum().sum() > 0:
      fig = go.Figure()

      for fecha_col in df_grafica.columns:
        valores_y = df_grafica[fecha_col]

        textos_barra = []
        for val in valores_y:
          if val <= 0:
            textos_barra.append("")
          else:
            total_segs = int(val * 3600)
            h = total_segs // 3600
            m = (total_segs % 3600) // 60
            s = total_segs % 60
            textos_barra.append(f"{h:02d}:{m:02d}:{s:02d}")

        fig.add_trace(
            go.Bar(
                x=df_grafica.index.astype(str),
                y=valores_y,
                name=str(fecha_col),
                text=textos_barra,
                textposition="inside",
                insidetextanchor="middle",
                textfont=dict(color="black"),
            )
        )

      fig.update_layout(
          barmode="stack",
          xaxis_title=col_filas,
          yaxis_title="Horas Equivalentes",
          legend_title="Fecha",
          plot_bgcolor="rgba(0,0,0,0)",
          paper_bgcolor="rgba(0,0,0,0)",
      )

      st.plotly_chart(fig, use_container_width=True)
    else:
      st.info("Sin datos numéricos suficientes para graficar.")
  else:
    st.info("Sin datos para mostrar en la gráfica."))

  if not tabla_numerica.empty:
    # 3. Preparamos la gráfica de barras apiladas directamente desde la matriz
    df_grafica = tabla_numerica.drop(index=["Total General"], errors="ignore")
    if "Total General" in df_grafica.columns:
      df_grafica = df_grafica.drop(columns=["Total General"], errors="ignore")

    if col_valor != "Horas_Decimales":
      df_grafica = df_grafica / 3600

    df_grafica = df_grafica.apply(pd.to_numeric, errors="coerce").fillna(0)

    if not df_grafica.empty and df_grafica.sum().sum() > 0:
      fig = go.Figure()

      for fecha_col in df_grafica.columns:
        valores_y = df_grafica[fecha_col]

        textos_barra = []
        for val in valores_y:
          if val <= 0:
            textos_barra.append("")
          else:
            total_segs = int(val * 3600)
            h = total_segs // 3600
            m = (total_segs % 3600) // 60
            s = total_segs % 60
            textos_barra.append(f"{h:02d}:{m:02d}:{s:02d}")

        fig.add_trace(
            go.Bar(
                x=df_grafica.index.astype(str),
                y=valores_y,
                name=str(fecha_col),
                text=textos_barra,
                textposition="inside",
                insidetextanchor="middle",
                textfont=dict(color="black"),
            )
        )

      fig.update_layout(
          barmode="stack",
          xaxis_title=col_filas,
          yaxis_title="Horas Equivalentes",
          legend_title="Fecha",
          plot_bgcolor="rgba(0,0,0,0)",
          paper_bgcolor="rgba(0,0,0,0)",
      )

      st.plotly_chart(fig, use_container_width=True)
    else:
      st.info("Sin datos numéricos suficientes para graficar.")
  else:
    st.info("Sin datos para mostrar en la gráfica.")
