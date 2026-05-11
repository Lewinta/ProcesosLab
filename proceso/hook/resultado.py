# Copyright (c) 2026, Rainier Polanco and contributors
# For license information, please see license.txt

import frappe

def before_print(doc, method):
    doc.patient_birthday = get_patient_birthday(doc)


def get_patient_birthday(doc):
    filters = { 
        "customer": doc.customer 
    }
    
    doctype = "Patient"

    patient = frappe.get_doc(doctype, filters)

    return patient.date_of_birth
