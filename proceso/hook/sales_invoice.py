import frappe


def validate(doc, method):
    validate_discount(doc)


def validate_discount(doc):
    for item in doc.items:
        item.difference_amount = item.claimed_amount - item.authorized_amount
        if item.discount_item > item.difference_amount:
            frappe.throw("Los descuentos no pueden ser mayor que la diferencia")
            