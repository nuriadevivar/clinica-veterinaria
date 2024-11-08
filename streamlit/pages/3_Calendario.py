import streamlit as st

from streamlit_calendar import calendar

import requests


st.title("Calendario de citas veterinarias 📆")


def send(data, method="POST"):
    try:
        if method == "POST":
            response = requests.post(backend, json=data)
        elif method == "PUT":
            response = requests.put(backend, json=data)
        elif method == "DELETE":
            response = requests.delete(backend, json=data)
        if response.status_code == 200:
            return '200'
        else:
            return str(response.status_code)
    except Exception as e:
        #mostrar errores
        return str(e)
    
@st.dialog("Registrar nueva cita")
def popup ():
    st.write(f'Fecha de la cita:')
    with st.form("form_nueva_cita"):
        nombre_animal = st.text_input("Nombre animal: ")
        nombre_dueño = st.text_input("Nombre dueño: ")
        tratamiento = st.text_input("Tipo de cita:")
        submitted = st.form_submit_button("Registrar cita")

    if submitted:
        data = {
            "nombre_animal": nombre_animal,
            "nombre_dueño": nombre_dueño,
            "tratamiento": tratamiento,
            "fecha_inicio": st.session_state["time_inicial"],
        }
        envio = send(data)
        if envio == '200':
            st.success("Registrado con éxito, puede cerrar!")
        else:
            st.error("No se registro, status_code: {}".format(envio))


mode = st.selectbox(
    "Calendar Mode:",
    (
        "daygrid",
        "timegrid",
        "timeline",
        "resource-daygrid", #consultas
        "resource-timegrid",
        "resource-timeline", #asignar y visualizar citas en diferentes lugares
        "list",
        "multimonth",
    ),
)
#eventos registrados
events = [
    {
        "title": "Consulta Perrito",
        "color": "#FF6C6C",
        "start": "2024-11-03",
        "end": "2023-11-05",
        "resourceId": "a",
    },
    
]
#recursos del calendario (consultas)
calendar_resources = [
    {"id": "a", "building": "Clinica 1", "title": "Consulta A"},
    {"id": "c", "building": "Clinica 1", "title": "Consulta B"},
]


backend = "http://fastapi:8000/citas"  # Esta URL meterla en un parámetro de configuración


fecha = ''


calendar_options = {
    #"true"
    "editable": True,
    "navLinks": True,
    "resources": calendar_resources,
    "selectable": True,
}
calendar_options = {
            **calendar_options,
            "initialDate": "2024-11-01",
            "initialView": "resourceTimeGridDay",
            "resourceGroupField": "building",
            "slotMinTime": "8:00:00", #hora de comienzo de citas
            "slotMaxTime": "18:00:00", #hora de fin de citas
        }

state = calendar(
    events=st.session_state.get("events", events),
    options=calendar_options,
    custom_css="""
    .fc-event-past {
        opacity: 0.8;
    }
    .fc-event-time {
        font-style: italic;
    }
    .fc-event-title {
        font-weight: 700;
    }
    .fc-toolbar-title {
        font-size: 2rem;
    }
    """,
    key='timegrid',
)

name = ''
#Actualizar eventos
if state.get("eventsSet") is not None:
    st.session_state["events"] = state["eventsSet"]
    #st.session_state["fecha"] = state["date"]

#Registrar nueva cita
if state.get('select') is not None:
    st.session_state["time_inicial"] = state["select"]["start"]
    st.session_state["time_final"] = state["select"]["end"]
    popup()

#Modificar citas
if state.get('eventChange') is not None:
    data = state.get('eventChange').get('event')
    ## aquí haríamos un requests.post()
    modified_data = {
        "id": data["id"],
        "start": data["start"],
        "end": data["end"]
    }
    envio = send(modified_data, method="PUT")
    if envio == '200':
        st.success('cita modificada con éxito')
    else:
        st.error(f"No se pudo modificar la cita, status_code: {envio}")


#Cancelar citas
if state.get('eventClick') is not None:
    data = state['eventClick']['event']
    if st.button(f"Cancelar cita {data['title']}"):
        envio = send({"id": data["id"]}, method="DELETE")
        if envio == "200":
            st.success("Cita cancelada.")
            #actualizar estado de eventos
            st.session_state["events"] = [event for event in st.session_state["events"] if event["id"] != data["id"]]
        else:
            st.error(f"No se pudo modificar la cita, status_code: {envio}")

if st.session_state.get("fecha") is not None:
    st.write('fecha')
    #st.write(st.session_state["fecha"])
   # with st.popover("Open popover"):
   #     st.markdown("Hello World 👋")
   #     name = st.text_input("What's your name?")