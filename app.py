import streamlit as st
import json
import os
from datetime import datetime

# ── Configuración de página ──────────────────────────────────────────────────
st.set_page_config(
    page_title="Gestor de Tareas",
    page_icon="✅",
    layout="centered",
)

# ── Estilos ──────────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Syne:wght@400;700;800&family=DM+Sans:wght@400;500&display=swap');

html, body, [class*="css"] { font-family: 'DM Sans', sans-serif; }
h1, h2, h3 { font-family: 'Syne', sans-serif; }

.task-card {
    background: #f8f7f4;
    border-left: 4px solid #e8e4dc;
    border-radius: 8px;
    padding: 12px 16px;
    margin-bottom: 10px;
    transition: border-color 0.2s;
}
.task-card.done {
    border-left-color: #4ade80;
    opacity: 0.65;
}
.task-card.alta  { border-left-color: #f87171; }
.task-card.media { border-left-color: #fbbf24; }
.task-card.baja  { border-left-color: #60a5fa; }

.badge {
    display: inline-block;
    padding: 2px 8px;
    border-radius: 99px;
    font-size: 11px;
    font-weight: 600;
    letter-spacing: .4px;
}
.badge-alta  { background:#fee2e2; color:#b91c1c; }
.badge-media { background:#fef3c7; color:#92400e; }
.badge-baja  { background:#dbeafe; color:#1d4ed8; }

.stats-row {
    display: flex;
    gap: 16px;
    margin-bottom: 24px;
}
.stat-box {
    flex: 1;
    background: #1a1a2e;
    color: white;
    border-radius: 12px;
    padding: 14px 18px;
    text-align: center;
}
.stat-box .num { font-family:'Syne',sans-serif; font-size:28px; font-weight:800; }
.stat-box .lbl { font-size:12px; opacity:.7; margin-top:2px; }
</style>
""", unsafe_allow_html=True)

# ── Persistencia en archivo JSON ─────────────────────────────────────────────
DATA_FILE = "tareas.json"

def cargar_tareas():
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return []

def guardar_tareas(tareas):
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(tareas, f, ensure_ascii=False, indent=2)

# ── Estado de sesión ─────────────────────────────────────────────────────────
if "tareas" not in st.session_state:
    st.session_state.tareas = cargar_tareas()

# ── Encabezado ───────────────────────────────────────────────────────────────
st.markdown("# ✅ Gestor de Tareas")
st.markdown("---")

# ── Estadísticas ─────────────────────────────────────────────────────────────
tareas = st.session_state.tareas
total     = len(tareas)
pendientes = sum(1 for t in tareas if not t["hecho"])
completadas = total - pendientes

st.markdown(f"""
<div class="stats-row">
  <div class="stat-box"><div class="num">{total}</div><div class="lbl">Total</div></div>
  <div class="stat-box"><div class="num">{pendientes}</div><div class="lbl">Pendientes</div></div>
  <div class="stat-box"><div class="num">{completadas}</div><div class="lbl">Completadas</div></div>
</div>
""", unsafe_allow_html=True)

# ── Formulario nueva tarea ────────────────────────────────────────────────────
with st.expander("➕ Agregar nueva tarea", expanded=(total == 0)):
    with st.form("nueva_tarea", clear_on_submit=True):
        titulo = st.text_input("Título de la tarea", placeholder="Ej: Revisar el informe...")
        col1, col2 = st.columns(2)
        with col1:
            prioridad = st.selectbox("Prioridad", ["alta", "media", "baja"])
        with col2:
            categoria = st.text_input("Categoría (opcional)", placeholder="Trabajo, Personal…")
        descripcion = st.text_area("Descripción (opcional)", height=80)
        enviado = st.form_submit_button("Agregar tarea", use_container_width=True)

        if enviado:
            if titulo.strip():
                nueva = {
                    "id": datetime.now().strftime("%Y%m%d%H%M%S%f"),
                    "titulo": titulo.strip(),
                    "descripcion": descripcion.strip(),
                    "prioridad": prioridad,
                    "categoria": categoria.strip(),
                    "hecho": False,
                    "fecha": datetime.now().strftime("%d/%m/%Y %H:%M"),
                }
                st.session_state.tareas.insert(0, nueva)
                guardar_tareas(st.session_state.tareas)
                st.success("Tarea agregada ✓")
                st.rerun()
            else:
                st.warning("El título no puede estar vacío.")

st.markdown("---")

# ── Filtros ───────────────────────────────────────────────────────────────────
col_f1, col_f2 = st.columns([1, 1])
with col_f1:
    filtro_estado = st.selectbox(
        "Mostrar",
        ["Todas", "Pendientes", "Completadas"],
        label_visibility="collapsed",
    )
with col_f2:
    filtro_prioridad = st.selectbox(
        "Prioridad",
        ["Todas las prioridades", "alta", "media", "baja"],
        label_visibility="collapsed",
    )

# ── Lista de tareas ───────────────────────────────────────────────────────────
tareas_filtradas = list(st.session_state.tareas)

if filtro_estado == "Pendientes":
    tareas_filtradas = [t for t in tareas_filtradas if not t["hecho"]]
elif filtro_estado == "Completadas":
    tareas_filtradas = [t for t in tareas_filtradas if t["hecho"]]

if filtro_prioridad != "Todas las prioridades":
    tareas_filtradas = [t for t in tareas_filtradas if t["prioridad"] == filtro_prioridad]

if not tareas_filtradas:
    st.info("No hay tareas que mostrar." if total > 0 else "¡Agrega tu primera tarea arriba!")
else:
    for tarea in tareas_filtradas:
        estado_clase = "done" if tarea["hecho"] else tarea["prioridad"]
        badge_clase  = f"badge-{tarea['prioridad']}"
        cat_text     = f"· {tarea['categoria']}" if tarea["categoria"] else ""
        desc_text    = f"<p style='margin:4px 0 0;font-size:13px;color:#666'>{tarea['descripcion']}</p>" if tarea["descripcion"] else ""

        st.markdown(f"""
        <div class="task-card {estado_clase}">
          <div style="display:flex;align-items:center;gap:8px;flex-wrap:wrap">
            <strong style="font-family:'Syne',sans-serif">{tarea['titulo']}</strong>
            <span class="badge {badge_clase}">{tarea['prioridad'].upper()}</span>
            <span style="font-size:12px;color:#999">{cat_text} · {tarea['fecha']}</span>
          </div>
          {desc_text}
        </div>
        """, unsafe_allow_html=True)

        col_a, col_b, col_c = st.columns([2, 1, 1])
        with col_a:
            label_toggle = "↩ Marcar pendiente" if tarea["hecho"] else "✓ Completar"
            if st.button(label_toggle, key=f"toggle_{tarea['id']}"):
                for t in st.session_state.tareas:
                    if t["id"] == tarea["id"]:
                        t["hecho"] = not t["hecho"]
                        break
                guardar_tareas(st.session_state.tareas)
                st.rerun()
        with col_c:
            if st.button("🗑 Eliminar", key=f"del_{tarea['id']}"):
                st.session_state.tareas = [
                    t for t in st.session_state.tareas if t["id"] != tarea["id"]
                ]
                guardar_tareas(st.session_state.tareas)
                st.rerun()

# ── Pie ───────────────────────────────────────────────────────────────────────
if completadas > 0:
    st.markdown("---")
    if st.button("🧹 Limpiar completadas"):
        st.session_state.tareas = [t for t in st.session_state.tareas if not t["hecho"]]
        guardar_tareas(st.session_state.tareas)
        st.rerun()