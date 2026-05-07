import streamlit as st
import pandas as pd
import numpy as np

# Configuración de la página
st.set_page_config(page_title="Calculadora Financiera", page_icon="💰")

st.title("💰 Calculadora de Préstamos")
st.write("Calcula tu cuota mensual y mira cómo se comportan los intereses.")

# Layout de dos columnas para los controles
col1, col2 = st.columns(2)

with col1:
    monto = st.number_input("Monto del préstamo ($)", min_value=1000, value=10000, step=500)
    tasa_anual = st.slider("Tasa de interés anual (%)", min_value=1.0, max_value=50.0, value=10.0)

with col2:
    plazo_años = st.number_input("Plazo en años", min_value=1, max_value=30, value=5)

# Cálculos financieros
tasa_mensual = (tasa_anual / 100) / 12
num_pagos = plazo_años * 12
cuota_mensual = (monto * tasa_mensual) / (1 - (1 + tasa_mensual)**-num_pagos)
total_pagado = cuota_mensual * num_pagos
total_intereses = total_pagado - monto

# Mostrar resultados principales
st.divider()
c1, c2, c3 = st.columns(3)
c1.metric("Cuota Mensual", f"${cuota_mensual:,.2f}")
c2.metric("Total a Pagar", f"${total_pagado:,.2f}")
c3.metric("Intereses Totales", f"${total_intereses:,.2f}")

# Gráfico de Proyección
st.subheader("Evolución del Saldo")
fechas = pd.date_range(start=pd.Timestamp.now(), periods=num_pagos, freq='M')
saldos = []
saldo_actual = monto

for _ in range(num_pagos):
    interes_mes = saldo_actual * tasa_mensual
    principal_mes = cuota_mensual - interes_mes
    saldo_actual -= principal_mes
    saldos.append(max(0, saldo_actual))

df_proyeccion = pd.DataFrame({"Mes": fechas, "Saldo Pendiente": saldos})
st.area_chart(df_proyeccion.set_index("Mes"))

st.info("💡 Consejo: Aumentar el pago mensual reduce drásticamente los intereses totales.")