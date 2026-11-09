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
  # FILTROS Y GRÁFICA DINÁMICA USANDO LAS COLUMNAS REALES DE TU ARCHIVO
  # ============================================================================
  st.markdown("---")
  st.subheader("🔍 Filtros de Búsqueda y Gráfica Dinámica")

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
      "⚙️ Configurar campos de la Gráfica y Filtros (Estilo Tabla Dinámica)",
      expanded=True,
  ):
    c_f1, c_f2, c_f3 = st.columns(3)
    with c_f1:
      col_grafica = st.selectbox(
          "Agrupar Gráfica por (Primer Fila / Columna):",
          columnas_disponibles,
          index=(
              columnas_disponibles.index("Maquina")
              if "Maquina" in columnas_disponibles
              else 0
          ),
      )
    with c_f2:
      filtro_op1 = st.selectbox(
          "Filtro Dinámico 1:",
          ["(Ninguno)"] + columnas_disponibles,
          index=(
              columnas_disponibles.index("Turno") + 1
              if "Turno" in columnas_disponibles
              else 0
          ),
      )
    with c_f3:
      filtro_op2 = st.selectbox(
          "Filtro Dinámico 2:",
          ["(Ninguno)"] + columnas_disponibles,
          index=(
              columnas_disponibles.index("Quien_Reporta") + 1
              if "Quien_Reporta" in columnas_disponibles
              else 0
          ),
      )

  f1, f2, f3 = st.columns(3)
  with f1:
    val_col1 = "Todos"
    if filtro_op1 != "(Ninguno)" and filtro_op1 in df_all.columns:
      opts1 = ["Todos"] + list(df_all[filtro_op1].dropna().unique())
      val_col1 = st.selectbox(f"Filtrar por {filtro_op1}", opts1)
    else:
      st.info("Filtro 1 inactivo")

  with f2:
    val_col2 = "Todos"
    if filtro_op2 != "(Ninguno)" and filtro_op2 in df_all.columns:
      opts2 = ["Todos"] + list(df_all[filtro_op2].dropna().unique())
      val_col2 = st.selectbox(f"Filtrar por {filtro_op2}", opts2)
    else:
      st.info("Filtro 2 inactivo")

  with f3:
    texto_busqueda = st.text_input(
        "Buscar texto en cualquier columna",
        "",
        placeholder="Escribe para buscar...",
    )

  df_view = df_all.copy() if not df_all.empty else pd.DataFrame()
  if not df_view.empty:
    if (
        filtro_op1 != "(Ninguno)"
        and val_col1 != "Todos"
        and filtro_op1 in df_view.columns
    ):
      df_view = df_view[df_view[filtro_op1] == val_col1]
    if (
        filtro_op2 != "(Ninguno)"
        and val_col2 != "Todos"
        and filtro_op2 in df_view.columns
    ):
      df_view = df_view[df_view[filtro_op2] == val_col2]
    if texto_busqueda:
      mask = df_view.astype(str).apply(
          lambda x: x.str.contains(texto_busqueda, case=False, na=False)
      ).any(axis=1)
      df_view = df_view[mask]

  st.markdown("---")
  st.metric("Registros Encontrados (Filtrados)", len(df_view))
  st.dataframe(df_view, use_container_width=True)

  st.markdown("---")
  st.subheader(f"📈 Gráfica Interactiva agrupada por: {col_grafica}")
  if not df_view.empty and col_grafica in df_view.columns:
    st.bar_chart(df_view[col_grafica].value_counts())
  else:
    df_cero = pd.DataFrame({"Datos": ["Sin datos"], "Cantidad": [0]}).set_index(
        "Datos"
    )
    st.bar_chart(df_cero)
