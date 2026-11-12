from datetime import datetime
import io
import os
import pandas as pd
import plotly.graph_objects as go
import requests
import streamlit as st

st.set_page_config(
    page_title="Reporte de Fallas - Mantenimiento C.H",
    page_icon="🔧",
    layout="wide",
)

st.title("🔧 Sistema Integral de Reportes C.H/7G")
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

# URL DE TU GOOGLE APPS SCRIPT
APPS_SCRIPT_URL = "https://script.google.com/macros/s/AKfycbxyJKgLSeYOe3UOKBZ_4EWLZQzX4xMcK6sRHV_QokmjuVWxsmIBajGnlJ3kGpQm9NQq/exec"


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
        "Turno",
        "Maquina",
        "Diagnostico",
        "Accion_Realizada",
        "Portamolde",
        "Quien_Reporta",
        "Seccion_Maquina",
        "Campo_Trabajo",
        "Acompanamiento",
        "Requiere_Repuesto",
        "Detalle_Repuesto",
        "Hora_Inicial",
        "Hora_Final",
        "Observaciones",
    ]

    for col in columnas_requeridas:
      if col not in df.columns:
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

# 1. DISEÑADOR DE FORMATOS
if menu == "Diseñador de Formatos por Departamento":
  st.header("🛠️ Diseñador y Gestión de Formatos")
  st.info(
      "Módulo activo para la gestión de campos personalizados por"
      " departamento."
  )

# 2. PANEL DE TÉCNICO
elif menu == "Panel de Técnico (Reporte de Falla)":
  st.header("📝 Registro de Reporte de Fallas")

  with st.form("form_falla"):
    c1, c2 = st.columns(2)
    with c1:
      fecha = st.date_input("1. Fecha", value=datetime.today())
      turno = st.selectbox("2. Turno", ["Turno Diurno", "Turno Nocturno"])
      maquina = st.selectbox(
          "3. Maquina",
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
      diagnostico = st.text_area("4. Diagnostico")
      accion_realizada = st.text_area("5. Acciones Realizadas")
      portamolde = st.selectbox(
          "6. Portamolde",
          [
              "Portalmolde 1",
              "Portalmolde 2",
              "Portalmolde 3",
              "Portalmolde 4",
              "Portalmolde 5",
              "N. A",
          ],
      )
      quien_reporta = st.selectbox(
          "7. Quien Reporta",
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
    with c2:
      seccion = st.selectbox(
          "8. Sección de Maquina",
          [
              "Inyector",
              "Mesa",
              "Central Hidraulica",
              "Gabinete Electrico",
              "Bloque de Prensado",
              "N/A",
          ],
      )
      campo_t = st.selectbox(
          "9. Campo de Trabajo",
          [
              "Mantenimiento Preventivo",
              "Corte de Energia",
              "Electrico",
              "Mecanico",
              "Hidraulico",
              "Refrigeración",
              "Proceso",
              "Neumatico",
              "Problemas Con Vacio",
              "N/A",
          ],
      )
      acompanamiento = st.selectbox(
          "10. Acompañamiento",
          [
              "N/A",
              "Carlos Castellanos",
              "Axel Castellanos",
              "Manuel Hernandez",
              "Bayron Enamorado",
              "Arnold Matute",
          ],
      )
      requiere_repuesto = st.selectbox(
          "11. Requiere repuestos o Insumo", ["No", "Si"]
      )
      detalle_repuesto = st.text_input(
          "12. Si requiere repuesto especifique qué repuesto es"
      )
      h_ini = st.text_input("13. Hora inicial de Falla (Ej. 08:00 AM)")
      h_fin = st.text_input("14. Hora Final de Falla (Ej. 09:30 AM)")

    observaciones = st.text_area("15. Observaciones")

    enviar = st.form_submit_button("Enviar Reporte")
    if enviar:
      if not diagnostico:
        st.error("Por favor escriba el diagnóstico.")
      else:
        datos_envio = {
            "Fecha": str(fecha),
            "Turno": turno,
            "Maquina": maquina,
            "Diagnostico": diagnostico,
            "Accion_Realizada": accion_realizada,
            "Portamolde": portamolde,
            "Quien_Reporta": quien_reporta,
            "Seccion_Maquina": seccion,
            "Campo_Trabajo": campo_t,
            "Acompanamiento": acompanamiento,
            "Requiere_Repuesto": requiere_repuesto,
            "Detalle_Repuesto": detalle_repuesto,
            "Hora_Inicial": h_ini,
            "Hora_Final": h_fin,
            "Observaciones": observaciones,
        }

        try:
          response = requests.post(APPS_SCRIPT_URL, json=datos_envio)
          if response.status_code == 200:
            st.success(
                "¡Reporte enviado y guardado exitosamente en Google Sheets!"
            )
          else:
            st.warning("El reporte se procesó con advertencias.")
        except Exception as ex:
          st.error(f"Error al conectar con Google Sheets: {ex}")

# 3. PANEL DE ADMINISTRACIÓN
elif menu == "Panel de Administración":
  st.header("📊 Panel de Administración y Control")

  df_all = st.session_state["bitacora_general"]
  total_reg = len(df_all)

  b1, b2, b3 = st.columns([2, 1, 1])
  with b1:
    st.caption(f"🟢 **Google Sheets:** {total_reg} registros sincronizados")
  with b2:
    if st.button("🔄 Sincronizar", use_container_width=True):
      if GOOGLE_SHEET_CSV_URL.strip() != "":
        st.session_state["bitacora_general"] = cargar_y_limpiar_datos(
            GOOGLE_SHEET_CSV_URL
        )
        st.success("¡Actualizado desde Google Sheets!")
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

  st.markdown("---")

  if not df_all.empty:
    st.subheader("📋 Historial de Reportes")
    st.dataframe(df_all, use_container_width=True)
  else:
    st.warning("No hay registros disponibles para mostrar.")
