from datetime import date
from app.domain.patient import Patient
from app.domain.exceptions import PossibleDuplicate, NotFound, ValidationError
from app.repositories.patient_repo import SqlitePatientRepo
from app.services.validation import required_text, normalize_phone, parse_birth_date
from app.db import get_db


def register_patient(form):
    repo = SqlitePatientRepo(get_db())
    name = required_text(form.get("full_name"), "Full name", 120)
    dob = parse_birth_date(form.get("date_of_birth"))
    gender = required_text(form.get("gender"), "Gender", 30)
    if gender not in {"Female", "Male", "Other", "Prefer not to say"}:
        raise ValidationError(["Select a valid gender option."])
    phone = normalize_phone(form.get("phone"))
    address = (form.get("address") or "").strip()
    if len(address) > 300:
        raise ValidationError(["Address must be 300 characters or fewer."])
    if repo.find_duplicate(phone, dob):
        raise PossibleDuplicate("A patient with this phone number and date of birth already exists. Check the existing record before registering again.")
    return repo.add(Patient(None, name, dob, gender, phone, address))


def update_patient(patient_id, form):
    repo = SqlitePatientRepo(get_db())
    patient = repo.get(patient_id)
    if patient is None or not patient.active:
        raise NotFound("Patient not found.")
    patient.full_name = required_text(form.get("full_name"), "Full name", 120)
    patient.gender = required_text(form.get("gender"), "Gender", 30)
    if patient.gender not in {"Female", "Male", "Other", "Prefer not to say"}:
        raise ValidationError(["Select a valid gender option."])
    patient.phone = normalize_phone(form.get("phone"))
    patient.address = (form.get("address") or "").strip()
    if len(patient.address) > 300:
        raise ValidationError(["Address must be 300 characters or fewer."])
    return repo.update(patient)
