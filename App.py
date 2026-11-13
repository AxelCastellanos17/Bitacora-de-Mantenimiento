if tipo_actividad == "Falla":
      st.subheader("📋 Formulario de Reporte de Falla")
      c3, c4 = st.columns(2)
      with c3:
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
        seccion = st.selectbox(
            "Sección de Máquina",
            [
                "Inyector",
                "Mesa",
                "Central Hidraulica",
                "Gabinete Electrico",
                "Bloque de Prensado",
                "N/A",
            ],
        )
      with c4:
        campo_t = st.selectbox(
            "Campo de Trabajo",
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
        h_ini = st.text_input("Hora Inicial de Falla (Ej. 08:00 AM)")
        h_fin = st.text_input("Hora Final de Falla (Ej. 09:30 AM)")

      # ESTRUCTURA DE MUÑECAS RUSAS (JERARQUÍA DE FALLAS EXCLUSIVA)
      st.markdown("---")
      st.write("🔧 **Diagnóstico y Selección en Cascada:**")

      arbol_fallas = {
          "Problema Electrico": [
              "Corto circuito",
              "Relee dañado",
              "Falso En señal",
              "MicroSwitchs Dañado",
              "Sensor Dañado",
          ],
          "Problema Hidraulico": [
              "Fuga de Aceite",
              "Electrovalvula dañada",
              "Sellos dañado",
              "Bomba dañada",
          ],
          "Problema Mecanico": [
              "Guia de compuerta dañada",
              "Cuña de eje dañada",
          ],
          "Problema con la Refrigeracion": [
              "Chiller con problemas",
              "Fuga de agua",
              "Valvula dañada",
          ],
          "Proceso": [
              "Burbuja de aire en bota",
              "Rayado",
              "Bota incompleta",
          ],
          "Problema Neumatico": [
              "N/A",
          ],
      }

      cat_principal = st.selectbox(
          "Selecciona el Área Principal",
          list(arbol_fallas.keys()),
          key="cat_principal_rusia",
      )

      sub_opciones = arbol_fallas.get(cat_principal, ["N/A"])
      sub_detalle = st.selectbox(
          f"Selecciona el detalle para: {cat_principal}",
          sub_opciones,
          key="sub_detalle_rusia",
      )

      diagnostico = f"{cat_principal} -> {sub_detalle}"

      solucion = st.text_area("Acciones Realizadas / Solución")
      repuesto = st.selectbox(
          "Requiere Repuestos o Insumo", ["No", "Si", "Fusible 6A", "Tornillo M10"]
      )
      observaciones = st.text_area("Observaciones")
