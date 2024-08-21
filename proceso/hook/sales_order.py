#  Copyright (c) 2023, Rainier J Polanco and contributors
#  For license information, please see license.txt

import frappe
from frappe.utils import flt


def validate(doc, method):
    validate_discount(doc)
    calculate_totals(doc)
    validate_unique_items(doc, method)


def validate_discount(doc):
    for item in doc.items:
        item.difference_amount = round(item.claimed_amount - item.authorized_amount, 2)
        
        if item.discount > item.difference_amount:
            frappe.msgprint(f"El descuento: {item.discount} Es mayor que la diferencia: {item.difference_amount}")
            
            
def calculate_totals(doc):
    total_amount_without_discount = 0.0
    total_amount_with_discount = 0.0
     
    for item in doc.items:
        total_amount_without_discount += flt(item.difference_amount, 2)
        total_amount_with_discount += flt(item.total, 2)
         
    doc.difference_amount = total_amount_with_discount
    doc.outstanding_amount = total_amount_with_discount
    doc.net_total = total_amount_with_discount
    doc.total = total_amount_without_discount
    
def validate_unique_items(doc, method):
    items = set()
    for item in doc.items:
        items.add(item.item_code)
    if len(items) != len(doc.items):
        frappe.throw('No puedes tener dos items iguales en la factura')
