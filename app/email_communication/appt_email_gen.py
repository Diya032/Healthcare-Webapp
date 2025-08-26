from datetime import datetime
from app.email_communication.acs_email import appointment_email_template

def generate_appointment_email(
    patient_name: str,
    doctor_name: str,
    doctor_specialty: str,
    slot_datetime: datetime,
    clinic_name: str = "Healthcare Clinic",
    location: str = "Main Clinic, 123 Health St",
    contact_number: str = "+91-9876543210",
    appointment_link: str = "#"
) -> str:
    """Generate appointment confirmation email HTML from plain values."""
    html_content = appointment_email_template.format(
        patient_name=patient_name,
        doctor_name=doctor_name,
        doctor_specialty=doctor_specialty,
        appointment_date=slot_datetime.strftime("%A, %d %B %Y"),
        appointment_time=slot_datetime.strftime("%I:%M %p"),
        location=location,
        appointment_link=appointment_link,
        contact_number=contact_number,
        clinic_name=clinic_name,
        current_year=datetime.utcnow().year
    )
    return html_content
