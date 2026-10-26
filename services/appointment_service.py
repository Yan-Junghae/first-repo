from datetime import datetime
from app.db import get_db
from app.domain.appointment import Appointment, AppointmentStatus
from app.domain.exceptions import NotFound, ValidationError, SlotUnavailable, InvalidStatusChange
from app.repositories.patient_repo import SqlitePatientRepo
from app.repositories.user_repo import SqliteUserRepo
from app.repositories.appointment_repo import SqliteAppointmentRepo
from app.domain.user import Role
from app.services.validation import parse_appointment_time


def schedule_appointment(form):
    conn = get_db()
    try:
        patient_id = int(form.get("patient_id", ""))
        doctor_id = int(form.get("doctor_id", ""))
    except (TypeError, ValueError):
        raise ValidationError(["Select a valid patient and doctor."])
    patient = SqlitePatientRepo(conn).get(patient_id)
    doctor = SqliteUserRepo(conn).get(doctor_id)
    if patient is None or not patient.active:
        raise NotFound("Active patient not found.")
    if doctor is None or not doctor.active or doctor.role != Role.DOCTOR:
        raise ValidationError(["Select an active doctor account."])
    start = parse_appointment_time(form.get("start_time"))
    repo = SqliteAppointmentRepo(conn)
    if repo.doctor_has_conflict(doctor_id, start):
        raise SlotUnavailable("The doctor has an appointment in that 30-minute slot.")
    return repo.add(Appointment(None, patient_id, doctor_id, start))


def change_appointment_status(appointment_id, new_status):
    repo = SqliteAppointmentRepo(get_db())
    appointment = repo.get(appointment_id)
    if appointment is None:
        raise NotFound("Appointment not found.")
    if not appointment.can_become(new_status):
        raise InvalidStatusChange(f"Cannot change an appointment from {appointment.status.value} to {new_status.value}.")
    repo.update_status(appointment_id, new_status)
