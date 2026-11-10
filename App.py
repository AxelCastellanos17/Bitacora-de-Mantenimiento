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


# Función auxiliar para limpiar espacios fantasma en los textos y nombres
def limpiar_dataframe(df):
  if df.empty:
    return df
  for col in df.select_dtypes(include=["object"]).columns:
    df[col] = df[col].astype(str).str.strip()
  return df


# PERSISTENCIA AUTOMÁTICA: Carga los datos guardados al iniciar la app
if "bitacora_general" not in st.session_state:
  if os.path.exists(EXCEL_FILE):
    try:
      st.session_state["bitacora_general"] = limpiar_dataframe(
          pd.read_excel(EXCEL_FILE)
      )
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
        }
        df_nuevo = pd.DataFrame([nueva_fila])
        st.session_state["bitacora_general"] = pd.concat(
            [st.session_state["bitacora_general"], df_nuevo],
            ignore_index=True,
        )
        st.session_state["bitacora_general"] = limpiar_dataframe(
            st.session_state["bitacora_general"]
        )
        try:
          st.session_state["bitacora_general"].to_excel(EXCEL_FILE, index=False)
        except Exception as ex:
          st.warning(f"Guardado local con advertencia: {ex}")
        st.success("¡Reporte enviado y guardado con éxito!")

# 3. PANEL DE ADMINISTRACIÓN
elif menu == "Panel de Administración":
  st.header("📊 Panel de Administración y Control")

  col_d, col_a, col_b = st.columns(3)
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
        "📂 Abrir archivo (Excel, CSV o Texto)", type=["xlsx", "csv", "txt"]
    )
    if archivo_subido is not None:
      if "archivo_procesado" not in st.session_state or st.session_state[
          "archivo_procesado"
      ] != archivo_subido.name:
        try:
          nombre_archivo = archivo_subido.name.lower()
          if nombre_archivo.endswith(".csv"):
            df_temp = pd.read_csv(archivo_subido, encoding="latin-1")
          elif nombre_archivo.endswith(".txt"):
            df_temp = pd.read_csv(
                archivo_subido, sep=None, engine="python", encoding="latin-1"
            )
          else:
            df_temp = pd.read_excel(archivo_subido)

          st.session_state["bitacora_general"] = limpiar_dataframe(df_temp)
          st.session_state["bitacora_general"].to_excel(EXCEL_FILE, index=False)
          st.session_state["archivo_procesado"] = archivo_subido.name
          st.success(
              f"✅ Archivo abierto y guardado con éxito"
              f" ({len(st.session_state['bitacora_general'])} registros)"
          )
        except Exception as e:
          st.error(f"Error al abrir el archivo: {e}")

  with col_b:
    st.write("🗑️ **Gestión de Datos**")
    if st.button("🗑️ Borrar y Limpiar Todos los Datos"):
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
      if "archivo_procesado" in st.session_state:
        del st.session_state["archivo_procesado"]
      if os.path.exists(EXCEL_FILE):
        try:
          os.remove(EXCEL_FILE)
        except:
          pass
      st.success("¡Se han borrado los datos cargados correctamente!")
      st.rerun()

  # PEGAR DATOS DIRECTAMENTE
  st.markdown("---")
  st.subheader("📋 Pegar Datos Directamente (Copia y Pega desde Excel)")
  texto_pegado = st.text_area(
      "Selecciona tus celdas en Excel (Ctrl+C) y pégalas aquí (Ctrl+V):",
      height=120,
      placeholder="Pega aquí los datos copiados de Excel...",
  )
  if st.button("📥 Procesar y Agregar Datos Pegados"):
    if texto_pegado:
      try:
        df_pegado = pd.read_csv(
            io.StringIO(texto_pegado), sep="\t", encoding="latin-1"
        )
        if not df_pegado.empty:
          df_pegado = limpiar_dataframe(df_pegado)
          st.session_state["bitacora_general"] = pd.concat(
              [st.session_state["bitacora_general"], df_pegado],
              ignore_index=True,
              sort=False,
          )
          st.session_state["bitacora_general"] = limpiar_dataframe(
              st.session_state["bitacora_general"]
          )
          try:
            st.session_state["bitacora_general"].to_excel(
                EXCEL_FILE, index=False
            )
          except:
            pass
          st.success(
              f"✅ ¡Se agregaron {len(df_pegado)} registros nuevos y se guardaron"
              " permanentemente!"
          )
          st.rerun()
        else:
          st.warning("El texto pegado no contiene datos válidos.")
      except Exception as ex:
        st.error(f"Error al procesar los datos pegados: {ex}")
    else:
      st.warning("Pega los datos en el cuadro de texto antes de procesar.")

  # ============================================================================
  # PANEL DE FILTROS Y CONFIGURACIÓN DE MATRIZ CON FILTRO JERÁRQUICO (AÑO / MES[CHECK] / DÍA)
  # ============================================================================
  st.markdown("---")
  st.subheader("⚙️ Panel de Filtros y Configuración de Matriz")

  df_all = st.session_state["bitacora_general"]
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

  with st.expander(
      "🎛️ Configuración de Filas, Columnas y Filtros Internos", expanded=True
  ):
    c_f1, c_f2, c_f3 = st.columns(3)
    with c_f1:
      col_filas = st.selectbox(
          "Filas de la Tabla (Ej. Maquina):",
          columnas_disponibles,
          index=(
              columnas_disponibles.index("Maquina")
              if "Maquina" in columnas_disponibles
              else 0
          ),
      )
    with c_f2:
      col_columnas = st.selectbox(
          "Columnas de la Tabla (Ej. Fecha):",
          columnas_disponibles,
          index=(
              columnas_disponibles.index("Fecha")
              if "Fecha" in columnas_disponibles
              else 0
          ),
      )
    with c_f3:
      col_valor = st.selectbox(
          "Valores / Tiempo Muerto:",
          columnas_disponibles,
          index=(
              columnas_disponibles.index("Tiempo de Falla")
              if "Tiempo de Falla" in columnas_disponibles
              else 0
          ),
      )

    st.markdown("### 🔍 Filtros Interactivos Internos")

    # PREPARACIÓN DE DATOS TEMPORALES PARA EL FILTRO JERÁRQUICO
    df_temp_filtro = df_all.copy()
    if not df_temp_filtro.empty and col_columnas in df_temp_filtro.columns:
      df_temp_filtro["_dt_temp"] = pd.to_datetime(
          df_temp_filtro[col_columnas], errors="coerce"
      )
      if df_temp_filtro["_dt_temp"].notna().sum() > 0:
        # Extraer el año como entero limpio sin decimales
        df_temp_filtro["_Anio"] = (
            df_temp_filtro["_dt_temp"].dt.year.fillna(0).astype(int).astype(str)
        )
        df_temp_filtro["_Mes"] = df_temp_filtro["_dt_temp"].dt.strftime("%B")
      else:
        df_temp_filtro["_Anio"] = "General"
        df_temp_filtro["_Mes"] = "General"
    else:
      df_temp_filtro["_Anio"] = "General"
      df_temp_filtro["_Mes"] = "General"

    f_col1, f_col2, f_col3, f_col4 = st.columns(4)

    # 1. Filtro Multiselección de Máquinas
    with f_col1:
      if not df_all.empty and col_filas in df_all.columns:
        maquinas_disponibles = sorted(
            list(df_all[col_filas].dropna().astype(str).unique())
        )
        maq_seleccionadas = st.multiselect(
            f"Filtrar {col_filas}",
            options=maquinas_disponibles,
            default=maquinas_disponibles,
        )
      else:
        maq_seleccionadas = []

    # 2. SELECCIÓN JERÁRQUICA CORREGIDA: AÑO ➔ MESES (CON CHECK/MULTISELECT) ➔ DÍAS
    with f_col2:
      if not df_temp_filtro.empty:
        anios_disp = sorted(
            list(df_temp_filtro["_Anio"].dropna().astype(str).unique())
        )
        anio_elegido = st.selectbox("📅 Seleccionar Año", anios_disp)

        df_anio_filtrado = df_temp_filtro[
            df_temp_filtro["_Anio"] == anio_elegido
        ]
        meses_disp = sorted(
            list(df_anio_filtrado["_Mes"].dropna().astype(str).unique())
        )

        # Meses con multiselección (casillas de verificación)
        meses_seleccionados = st.multiselect(
            "📂 Seleccionar Mes(es)", options=meses_disp, default=meses_disp
        )

        df_mes_filtrado = df_anio_filtrado[
            df_anio_filtrado["_Mes"].isin(meses_seleccionados)
        ]
        dias_disp = sorted(
            list(df_mes_filtrado[col_columnas].dropna().astype(str).unique())
        )
        dias_seleccionados = st.multiselect(
            "📌 Seleccionar Días", options=dias_disp, default=dias_disp
        )
      else:
        dias_seleccionados = []

    # 3. Filtro por Turno
    with f_col3:
      turno_opts = (
          ["Todos"]
          + sorted(list(df_all["Turno"].dropna().astype(str).unique()))
          if not df_all.empty and "Turno" in df_all.columns
          else ["Todos"]
      )
      f_turno = st.selectbox("Filtrar por Turno", turno_opts)

    # 4. Filtro por Quién Reporta
    with f_col4:
      rep_opts = (
          ["Todos"]
          + sorted(list(df_all["Quien_Reporta"].dropna().astype(str).unique()))
          if not df_all.empty and "Quien_Reporta" in df_all.columns
          else ["Todos"]
      )
      f_rep = st.selectbox("Filtrar por Quién Reporta", rep_opts)

    texto_busqueda = st.text_input(
        "Buscar palabra clave (Diagnóstico / Solución):",
        "",
        placeholder="Escribe para buscar...",
    )

  # Aplicar todos los filtros al DataFrame final
  df_view = df_all.copy() if not df_all.empty else pd.DataFrame()
  if not df_view.empty:
    if maq_seleccionadas and col_filas in df_view.columns:
      df_view = df_view[
          df_view[col_filas].astype(str).isin(maq_seleccionadas)
      ]
    if dias_seleccionados and col_columnas in df_view.columns:
      df_view = df_view[
          df_view[col_columnas].astype(str).isin(dias_seleccionados)
      ]
    if f_turno != "Todos" and "Turno" in df_view.columns:
      df_view = df_view[df_view["Turno"].astype(str) == f_turno]
    if f_rep != "Todos" and "Quien_Reporta" in df_view.columns:
      df_view = df_view[df_view["Quien_Reporta"].astype(str) == f_rep]
    if texto_busqueda:
      mask = (
          df_view.astype(str)
          .apply(lambda x: x.str.contains(texto_busqueda, case=False, na=False))
          .any(axis=1)
      )
      df_view = df_view[mask]

  # 1. VISUALIZACIÓN DE LA TABLA CRUZADA (MATRIZ)
  st.markdown("---")
  st.subheader("📋 Total de Tiempo Muerto / Falla (Tabla Cruzada)")

  tabla_dinamica = pd.DataFrame()
  if (
      not df_view.empty
      and col_filas in df_view.columns
      and col_columnas in df_view.columns
  ):
    try:
      tabla_dinamica = pd.pivot_table(
          df_view,
          index=col_filas,
          columns=col_columnas,
          values=col_valor,
          aggfunc="count",
          fill_value=0,
      )
      # Agregar totales estilo Excel
      tabla_dinamica["Total General"] = tabla_dinamica.sum(axis=1)
      total_columna = pd.DataFrame(tabla_dinamica.sum(axis=0)).T
      total_columna.index = ["Total General"]
      tabla_dinamica = pd.concat([tabla_dinamica, total_columna])

      st.dataframe(tabla_dinamica, use_container_width=True)
    except Exception as ex:
      st.warning(f"No se pudo generar la tabla cruzada: {ex}")
      st.dataframe(df_view, use_container_width=True)
  else:
    st.info("Sube un archivo o pega datos para mostrar la tabla cruzada.")

  # 2. GRÁFICA DE BARRAS APILADAS CONTROLADA
  st.markdown("---")
  st.subheader("📈 Gráfica de Tiempo de Paros de Máquinas (Apilada)")

  if not tabla_dinamica.empty:
    df_grafica_barras = tabla_dinamica.drop(
        index=["Total General"], errors="ignore"
    )
    if "Total General" in df_grafica_barras.columns:
      df_grafica_barras = df_grafica_barras.drop(
          columns=["Total General"], errors="ignore"
      )

    st.bar_chart(df_grafica_barras)
  else:
    df_cero = pd.DataFrame({"Datos": ["Sin datos"], "Cantidad": [0]}).set_index(
        "Datos"
    )
    st.bar_chart(df_cero)
