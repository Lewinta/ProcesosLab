import frappe


def before_validate(doc, method=None):
    """Populate customer DOB from linked Patient when missing."""
    if doc.doctype != "Customer":
        return

    if doc.get("date_of_birth"):
        return

    if doc.get("customer_group") != "Patients":
        return

    patient = frappe.db.get_value(
        "Patient",
        {"customer": doc.name},
        ["name", "dob"],
        as_dict=True,
    )

    if not patient and doc.get("customer_name"):
        patient = frappe.db.get_value(
            "Patient",
            {"patient_name": doc.customer_name},
            ["name", "dob"],
            as_dict=True,
            order_by="modified desc",
        )

    if patient and patient.get("dob"):
        doc.date_of_birth = patient.get("dob")
