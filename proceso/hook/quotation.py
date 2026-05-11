# Copyright (c) 2026, Rainier Polanco and contributors
# For license information, please see license.txt

import frappe

def before_print(doc, *args, **kwargs):
    # Frappe may pass extra arguments to print hooks (print_format, html, etc.).
    # Accept them with *args/**kwargs to avoid TypeError and use only doc.
    doc.patient_birthday = get_patient_birthday(doc)


# ...existing code...
def get_patient_birthday(doc):
    try:
        if not getattr(doc, "party_name", None):
            return None

        # Buscar DOB usando filtros; get_value no lanza excepción si no hay resultados
        dob = frappe.db.get_value("Patient", {"customer": doc.party_name}, "dob")
        return dob
    except Exception as e:
        # Loguear el error para debugging y devolver None
        frappe.log_error(message=str(e), title="Get patient birthday failed")
        return None
# ...existing
