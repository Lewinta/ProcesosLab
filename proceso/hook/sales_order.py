#  Copyright (c) 2023, Rainier J Polanco and contributors
#  For license information, please see license.txt

import frappe
from frappe.utils import flt


def validate(doc, method):
    validate_unique_items(doc, method)


def validate_unique_items(doc, method):
    items = set()
    for item in doc.items:
        items.add(item.item_code)
    if len(items) != len(doc.items):
        frappe.throw('No puedes tener dos items iguales en la factura')
