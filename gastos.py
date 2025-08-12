import streamlit as st
import pandas as pd

st.set_page_config(page_title="💳 Control de Gastos Roomies", page_icon="💳", layout="centered")

if "gastos" not in st.session_state:
    st.session_state.gastos = []
if "personas" not in st.session_state:
    st.session_state.personas = []

st.title("💳 Control de Gastos entre Roomies")

if not st.session_state.personas:
    st.subheader("👥 Registro de participantes")
    num_personas = st.number_input("¿Cuántas personas participan?", min_value=2, step=1)

    nombres = []
    if num_personas:
        for i in range(num_personas):
            nombre = st.text_input(f"Nombre de persona {i+1}", value=f"Persona {i+1}")
            nombres.append(nombre)

        if st.button("Confirmar personas"):
            # Guardamos sólo nombres no vacíos para evitar errores
            personas_limpias = [n.strip() for n in nombres if n.strip() != ""]
            if len(personas_limpias) >= 2:
                st.session_state.personas = personas_limpias
                st.success("✅ Personas registradas. Ahora puedes ingresar gastos.")
            else:
                st.error("⚠️ Debes ingresar al menos dos nombres válidos.")
else:
    st.subheader("➕ Agregar gasto")
    monto = st.number_input("Monto de la compra", min_value=0.0, step=0.01)
    tipo_gasto = st.selectbox("Tipo de gasto", ["Compartido", "Personal"])

    if tipo_gasto == "Compartido":
        divididos = st.multiselect("¿Entre quiénes se divide?", st.session_state.personas, default=st.session_state.personas)
    else:
        divididos = [st.selectbox("¿Para quién es el gasto?", st.session_state.personas)]

    quien_pago = st.selectbox("¿Quién pagó con su tarjeta?", st.session_state.personas)

    if st.button("Agregar gasto"):
        if monto > 0 and len(divididos) > 0:
            st.session_state.gastos.append({
                "Monto": monto,
                "Tipo": tipo_gasto,
                "Dividido entre": divididos,
                "Pagó": quien_pago
            })
            st.success("✅ Gasto agregado correctamente")
        else:
            st.error("⚠️ Ingresa un monto válido y selecciona al menos una persona.")

    if st.session_state.gastos:
        st.subheader("📜 Lista de gastos")
        df_gastos = pd.DataFrame(st.session_state.gastos)
        st.dataframe(df_gastos)

    if st.button("📊 Mostrar resumen"):
        df = pd.DataFrame(st.session_state.gastos)

        pagos_tarjeta = {p: 0 for p in st.session_state.personas}
        pagos_reales = {p: 0 for p in st.session_state.personas}

        for _, row in df.iterrows():
            pagos_tarjeta[row["Pagó"]] += row["Monto"]
            parte = row["Monto"] / len(row["Dividido entre"])
            for p in row["Dividido entre"]:
                pagos_reales[p] += parte

        resumen = []
        for p in st.session_state.personas:
            diferencia = pagos_tarjeta[p] - pagos_reales[p]
            resumen.append([p, pagos_tarjeta[p], pagos_reales[p], diferencia])

        df_resumen = pd.DataFrame(resumen, columns=["Persona", "Pagó tarjeta", "Pago real", "Diferencia"])
        st.subheader("📊 Resumen de gastos")
        st.dataframe(df_resumen)

        deudores = df_resumen[df_resumen["Diferencia"] < 0]
        acreedores = df_resumen[df_resumen["Diferencia"] > 0]

        st.subheader("💰 Deudas entre personas")
        if not deudores.empty and not acreedores.empty:
            for _, d in deudores.iterrows():
                for _, a in acreedores.iterrows():
                    monto = min(abs(d["Diferencia"]), a["Diferencia"])
                    if monto > 0:
                        st.write(f"**{d['Persona']}** le debe **${monto:.2f}** a **{a['Persona']}**")

        st.subheader("📈 Porcentaje de contribución al gasto real")
        total_gasto = sum(pagos_reales.values())
        for p in st.session_state.personas:
            st.write(f"{p}: {pagos_reales[p] / total_gasto * 100:.2f}% del gasto total")
