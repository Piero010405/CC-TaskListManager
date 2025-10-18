import streamlit as st
from pymongo import MongoClient
from datetime import datetime
from bson import ObjectId

# ============================
# CONFIGURACIÓN DE LA APP
# ============================
st.set_page_config(page_title="Mi Tablero de Actividades 🐕", layout="wide")

# Conexión a MongoDB usando secretos
MONGODB_URI = st.secrets["app"]["MONGODB_URI"]
client = MongoClient(MONGODB_URI)
db = client["daily_tasks_db"]
tasks_collection = db["tasks"]

# ============================
# FUNCIONES CRUD
# ============================
def get_tasks():
    return list(tasks_collection.find().sort("created_at", -1))

def add_task(title, description, status, priority):
    new_task = {
        "title": title,
        "description": description,
        "status": status,
        "priority": priority,
        "created_at": datetime.now()
    }
    tasks_collection.insert_one(new_task)

def delete_task(task_id):
    tasks_collection.delete_one({"_id": ObjectId(task_id)})

def update_task_status(task_id, new_status):
    tasks_collection.update_one({"_id": ObjectId(task_id)}, {"$set": {"status": new_status}})

# ============================
# INTERFAZ STREAMLIT
# ============================
st.title("🗓️ Mi Tablero de Actividades")
st.markdown("Organiza tus tareas diarias para poder seguir en vida 💡")

# Sidebar para agregar tareas
st.sidebar.header("➕ Agregar nueva tarea")
with st.sidebar.form("add_task_form"):
    title = st.text_input("Título de la tarea")
    description = st.text_area("Descripción")
    priority = st.selectbox("Prioridad", ["Alta", "Media", "Baja"])
    status = st.selectbox("Estado inicial", ["Pendiente", "En progreso", "Completada"])
    submit = st.form_submit_button("Guardar tarea")

if submit and title:
    add_task(title, description, status, priority)
    st.sidebar.success("✅ Tarea agregada exitosamente")

# ============================
# TABLERO DE TAREAS (Kanban)
# ============================
tasks = get_tasks()
statuses = ["Pendiente", "En progreso", "Completada"]
cols = st.columns(3)

for idx, status in enumerate(statuses):
    with cols[idx]:
        st.subheader(f"{status} ({len([t for t in tasks if t['status']==status])})")
        for task in [t for t in tasks if t["status"] == status]:
            with st.expander(f"📌 {task['title']}"):
                st.markdown(f"**Descripción:** {task['description']}")
                st.markdown(f"**Prioridad:** {task['priority']}")
                st.markdown(f"**Creada:** {task['created_at'].strftime('%d/%m/%Y %H:%M')}")
                new_status = st.selectbox(
                    "Actualizar estado:",
                    statuses,
                    index=statuses.index(task["status"]),
                    key=str(task["_id"])
                )
                if new_status != task["status"]:
                    update_task_status(task["_id"], new_status)
                    st.success("Estado actualizado ✅")
                    st.experimental_rerun()

                if st.button("🗑️ Eliminar", key=f"del-{task['_id']}"):
                    delete_task(task["_id"])
                    st.warning("Tarea eliminada 🗑️")
                    st.experimental_rerun()
