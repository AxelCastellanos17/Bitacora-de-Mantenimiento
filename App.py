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

# PERSISTENCIA AUTOMÁTICA: Carga los datos guardados al iniciar la app
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
        # Guarda automáticamente en disco para que no se pierda al actualizar
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
      try:
        nombre_archivo = archivo_subido.name.lower()
        if nombre_archivo.endswith(".csv"):
          st.session_state["bitacora_general"] = pd.read_csv(
              archivo_subido, encoding="latin-1"
          )
        elif nombre_archivo.endswith(".txt"):
          st.session_state["bitacora_general"] = pd.read_csv(
              archivo_subido, sep=None, engine="python", encoding="latin-1"
          )
        else:
          st.session_state["bitacora_general"] = pd.read_excel(archivo_subido)

        # Guarda automáticamente el archivo cargado para persistencia
        st.session_state["bitacora_general"].to_excel(EXCEL_FILE, index=False)

        st.success(
            f"✅ Archivo abierto y guardado con éxito"
            f" ({len(st.session_state['bitacora_general'])} registros)"
        )
        st.rerun()
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
          st.session_state["bitacora_general"] = pd.concat(
              [st.session_state["bitacora_general"], df_pegado],
              ignore_index=True,
              sort=False,
          )
          # Guarda automáticamente en disco tras pegar
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

  # FILTROS Y GRÁFICA PERSONALIZABLES (ESTILO TABLA DINÁMICA)
  st.markdown("---")
  st.subheader("🔍 Filtros de Búsqueda y Gráfica Dinámica")

  df_all = st.session_state["bitacora_general"]

  with st.expander(
      "⚙️ Configurar orden y campos de filtro (Estilo Tabla Dinámica)",
      expanded=True,
  ):
    c_f1, c_f2, c_f3 = st.columns(3)
    with c_f1:
      f_principal = st.selectbox(
          "Filtro Principal (Filas)",
          [
              "Maquina",
              "Quien_Reporta",
              "Turno",
              "Departamento",
              "Campo_Trabajo",
          ],
      )
    with c_f2:
      f_secundario = st.selectbox(
          "Filtro Secundario",
          [
              "Turno",
              "Quien_Reporta",
              "Maquina",
              "Departamento",
              "Campo_Trabajo",
          ],
      )
    with c_f3:
      metrica_grafica = st.selectbox(
          "Agrupar Gráfica por:",
          [
              "Maquina",
              "Quien_Reporta",
              "Turno",
              "Campo_Trabajo",
              "Departamento",
          ],
      )

  f1, f2, f3 = st.columns(3)
  with f1:
    deptos = (
        ["Todos"] + list(df_all["Departamento"].dropna().unique())
        if not df_all.empty and "Departamento" in df_all.columns
        else ["Todos"]
    )
    f_dep = st.selectbox("Filtrar por Departamento", deptos)
  with f2:
    maqs = (
        ["Todas"] + list(df_all["Maquina"].dropna().unique())
        if not df_all.empty and "Maquina" in df_all.columns
        else ["Todas"]
    )
    f_maq = st.selectbox("Filtrar por Máquina", maqs)
  with f3:
    tecnicos = (
        ["Todos"] + list(df_all["Quien_Reporta"].dropna().unique())
        if not df_all.empty and "Quien_Reporta" in df_all.columns
        else ["Todos"]
    )
    f_tec = st.selectbox("Filtrar por Quién Reporta", tecnicos)

  f4, f5, f6 = st.columns(3)
  with f4:
    turnos_opts = (
        ["Todos"] + list(df_all["Turno"].dropna().unique())
        if not df_all.empty and "Turno" in df_all.columns
        else ["Todos"]
    )
    f_turno = st.selectbox("Filtrar por Turno", turnos_opts)
  with f5:
    campos_opts = (
        ["Todos"] + list(df_all["Campo_Trabajo"].dropna().unique())
        if not df_all.empty and "Campo_Trabajo" in df_all.columns
        else ["Todos"]
    )
    f_campo = st.selectbox("Filtrar por Campo de Trabajo", campos_opts)
  with f6:
    f_diag = st.text_input("Buscar en Diagnóstico", "")

  # Aplicar filtros en cascada
  df_view = df_all.copy() if not df_all.empty else pd.DataFrame()
  if not df_view.empty:
    if f_dep != "Todos" and "Departamento" in df_view.columns:
      df_view = df_view[df_view["Departamento"] == f_dep]
    if f_maq != "Todas" and "Maquina" in df_view.columns:
      df_view = df_view[df_view["Maquina"] == f_maq]
    if f_tec != "Todos" and "Quien_Reporta" in df_view.columns:
      df_view = df_view[df_view["Quien_Reporta"] == f_tec]
    if f_turno != "Todos" and "Turno" in df_view.columns:
      df_view = df_view[df_view["Turno"] == f_turno]
    if f_campo != "Todos" and "Campo_Trabajo" in df_view.columns:
      df_view = df_view[df_view["Campo_Trabajo"] == f_campo]
    if f_diag and "Diagnostico" in df_view.columns:
      df_view = df_view[
          df_view["Diagnostico"].str.contains(f_diag, case=False, na=False)
      ]

  st.markdown("---")
  st.metric("Registros Encontrados (Filtrados)", len(df_view))
  st.dataframe(df_view, use_container_width=True)

  st.markdown("---")
  st.subheader("📈 Gráfica Interactiva (Dinámica)")
  if not df_view.empty and metrica_grafica in df_view.columns:
    st.bar_chart(df_view[metrica_grafica].value_counts())
  else:
    df_cero = pd.DataFrame({"Datos": ["Sin datos"], "Cantidad": [0]}).set_index(
        "Datos"
    )
    st.bar_chart(df_cero)
