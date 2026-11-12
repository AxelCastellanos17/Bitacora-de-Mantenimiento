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
          response = requests.post(
              "https://script.google.com/macros/s/AKfycbxyJKgLSeYOe3UOKBZ_4EWLZQzX4xMcK6sRHV_QokmjuVWxsmIBajGnlJ3kGpQm9NQq/exec",
              json=datos_envio,
          )
          if response.status_code == 200:
            st.success(
                "¡Reporte enviado y guardado exitosamente en Google Sheets!"
            )
          else:
            st.warning("El reporte se procesó con advertencias.")
        except Exception as ex:
          st.error(f"Error al conectar con Google Sheets: {ex}")
