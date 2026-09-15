import streamlit as st
import numpy as np
import scipy.stats as stats
import matplotlib.pyplot as plt

# --- CONFIGURACIÓN DE LA PÁGINA ---
st.set_page_config(page_title="Simulación - Equipo 11", layout="wide")
st.title("🏭 Prototipo de Validación Estadística - PrecisPiezas Ltda.")
st.caption("Asignatura: Simulación | Grupo: AA | Software Optimizado con Filtros y Gráficos Avanzados")

# --- MENÚ LATERAL (INPUTS CON BOTÓN DE REINICIO) ---
st.sidebar.header("📋 Parámetros de la Prueba")

# Control de estado para el botón de limpieza rápida
if "input_datos" not in st.session_state:
    st.session_state.input_datos = "0.69, 0.00, 0.55, 0.85, 0.14, 0.71, 0.26, 0.57, 0.12, 0.42, 0.98, 0.12, 0.83, 0.14"

# Botón de reinicio rápido
if st.sidebar.button("🧹 Limpiar / Reiniciar Caja de Texto"):
    st.session_state.input_datos = ""
    st.rerun()

# 1. Ingreso de datos conectado al botón
datos_string = st.sidebar.text_area(
    "Pegue los números pseudoaleatorios (ri) separados por comas o espacios:",
    value=st.session_state.input_datos,
    key="texto_ri",
    height=150
)
st.session_state.input_datos = datos_string

# 2. Selección de la prueba
tipo_prueba = st.sidebar.selectbox("Seleccione la prueba estadística:", ["Prueba de los Promedios", "Prueba de las Frecuencias"])

# 3. Nivel de significancia alfa
alfa_porcentaje = st.sidebar.selectbox("Nivel de significancia (α) %:", [1, 5, 10], index=1)
alfa = alfa_porcentaje / 100.0

# 4. Parámetro K para frecuencias
k_intervalos = st.sidebar.number_input("Número de intervalos (K) - Solo para Frecuencias:", min_value=2, max_value=20, value=4)

# --- PROCESAMIENTO Y BLINDAJE DE DATOS (Anti-Errores en Vivo) ---
try:
    # Limpieza eliminando comas, puntos y comas o tabulaciones accidentales
    limpio = datos_string.replace(",", " ").replace(";", " ").replace("\t", " ").split()
    ri = [float(x.strip()) for x in limpio if x.strip() != ""]
    n = len(ri)
except ValueError:
    st.error("❌ **Error Crítico de Entrada:** Se detectaron letras o caracteres especiales no válidos. Ingrese únicamente números decimales.")
    st.stop()

if n == 0:
    st.warning("⚠️ El sistema está listo. Por favor, ingrese o pegue una secuencia de números en la barra lateral para comenzar.")
    st.stop()

# Validación de rango uniforme teórico [0.0, 1.0]
fuera_de_rango = [x for x in ri if x < 0.0 or x > 1.0]
if fuera_de_rango:
    st.error(f"⚠️ **Error Operativo:** Se detectaron {len(fuera_de_rango)} números fuera del rango permitido [0.0 , 1.0]. Ejemplo(s): {fuera_de_rango[:3]}. Corrija la lista para continuar.")
    st.stop()

# --- VISTA PRINCIPAL EN DOS COLUMNAS ---
col1, col2 = st.columns(2)

with col1:
    st.subheader("📊 Resultados Estadísticos")
    st.write(f"**Cantidad de datos válidos procesados (n):** {n}")

    if tipo_prueba == "Prueba de los Promedios":
        promedio = np.mean(ri)
        z_calculado = abs((promedio - 0.5) * np.sqrt(n)) / np.sqrt(1/12)
        z_critico = stats.norm.ppf(1 - alfa/2)
        
        st.write(f"**Promedio muestral (X̄):** `{promedio:.4f}`")
        st.write(f"**Estadístico Calculado (Z₀):** `{z_calculado:.4f}`")
        st.write(f"**Valor Crítico de Tabla (Z_critico):** `{z_critico:.4f}`")
        
        se_acepta_h0 = z_calculado < z_critico

    else:
        fe = n / k_intervalos
        limites = np.linspace(0.0, 1.0, k_intervalos + 1)
        fo, _ = np.histogram(ri, bins=limites)
        
        chi_calculado = sum([(o - fe)**2 / fe for o in fo])
        chi_critico = stats.chi2.ppf(1 - alfa, k_intervalos - 1)
        
        st.write(f"**Frecuencia Esperada Teórica (FE):** `{fe:.2f}` por intervalo")
        st.write(f"**Estadístico Calculado (χ²₀):** `{chi_calculado:.4f}`")
        st.write(f"**Valor Crítico de Tabla (χ²_critico):** `{chi_critico:.4f}`")
        
        se_acepta_h0 = chi_calculado < chi_critico

    st.markdown("---")
    if se_acepta_h0:
        st.success("✅ **DECISIÓN: SE ACEPTA H₀**")
        st.info(
            f"**Interpretación Industrial (PrecisPiezas Ltda.):**\n\n"
            f"La secuencia de números suministrada se comporta de manera uniforme. "
            f"**Es matemáticamente válida** para integrarse en nuestro simulador de planta. "
            f"Nos permitirá modelar con total precisión la aparición de piezas defectuosas que entran a reproceso, "
            f"evitando errores de planificación o sobrecostos en la fábrica."
        )
    else:
        st.error("❌ **DECISIÓN: SE RECHAZA H₀ (SE ACEPTA H₁)**")
        st.warning(
            f"**Interpretación Industrial (PrecisPiezas Ltda.):**\n\n"
            f"La secuencia tiene un comportamiento sesgado y NO es uniforme. "
            f"**NO se debe usar en el simulador**. Si la usamos, calcularemos erróneamente "
            f"las fallas en las piezas mecánicas de precisión, destruyendo la confiabilidad de la simulación "
            f"y provocando pérdidas económicas en la planeación real."
        )

with col2:
    st.subheader("📈 Histograma de Frecuencias Requerido")
    
    fig, ax = plt.subplots(figsize=(6, 4.5))
    bins_grafico = np.linspace(0.0, 1.0, k_intervalos + 1)
    
    # --- MEJORAS VISUALES EN HISTOGRAMA ---
    conteos, barras, _ = ax.hist(ri, bins=bins_grafico, color='#1E88E5', edgecolor='black', alpha=0.8, rwidth=0.85)
    
    # Colocar etiquetas numéricas de conteo encima de cada barra
    for conteo, barra in zip(conteos, barras):
        if conteo > 0:
            ax.text(barra + (1/k_intervalos)/2, conteo + 0.1, str(int(conteo)), ha='center', va='bottom', fontsize=9, fontweight='bold', color='#0D47A1')

    # Línea horizontal punteada de Frecuencia Esperada (Solo se muestra en la prueba de frecuencias)
    if tipo_prueba == "Prueba de las Frecuencias":
        fe_linea = n / k_intervalos
        ax.axhline(fe_linea, color='#D32F2F', linestyle='--', linewidth=2, label=f'Frecuencia Esperada ({fe_linea:.2f})')
        ax.legend(loc='upper right')

    ax.set_xlim(0.0, 1.0)
    ax.set_ylim(0, max(conteos) + 1 if len(conteos) > 0 else 5)
    ax.set_title("Distribución de Frecuencias en el Rango [0.0 - 1.0]", fontweight='bold')
    ax.set_xlabel("Límites de los Intervalos")
    ax.set_ylabel("Frecuencia Absoluta (Cantidad)")
    ax.grid(axis='y', linestyle=':', alpha=0.6)
    
    st.pyplot(fig)