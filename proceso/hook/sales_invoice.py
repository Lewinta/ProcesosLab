import frappe
from frappe.utils import flt

DISCOUNT_MANAGER_ROLE = "Discount Manager"


def user_has_discount_permission():
    return DISCOUNT_MANAGER_ROLE in frappe.get_roles()


def validate(doc, method):
    return 
    validate_discount(doc)
    validate_against_difference_amount(doc, method)
    validate_discount_for_items(doc, method)


def validate_discount(doc):
    has_any_discount = (
        any(
            flt(getattr(item, "discount_item", 0)) or flt(getattr(item, "discount_with_percent", 0))
            for item in doc.items
        )
        or flt(getattr(doc, "discount_for_items", 0))
    )
    if has_any_discount and not user_has_discount_permission():
        frappe.throw("Solo usuarios con el rol 'Discount Manager' pueden aplicar descuentos.")

    for item in doc.items:
        item.difference_amount = item.claimed_amount - item.authorized_amount
        tolerance = 1e-3  # Puedes ajustar la tolerancia según tus necesidades
        discount_val = getattr(item, "discount_item", 0) or getattr(item, "discount", 0)
        if discount_val > item.difference_amount + tolerance:
            frappe.throw(f'''El descuento de la línea {item.idx} 
            no puede ser mayor que la diferencia''')

def validate_against_difference_amount(doc, method):
    total_discount = 0
    total_difference_amout = 0

    for item in doc.items:
        total_discount += getattr(item, "discount_item", 0) or getattr(item, "discount", 0)
        total_difference_amout += item.difference_amount
    
    if total_discount > total_difference_amout:
        frappe.throw(f'''El descuento total {total_discount} 
         no puede ser mayor que la diferencia total {total_difference_amout}''')
        
def validate_discount_for_items(doc, method):
    total_difference_amout = 0
    for item in doc.items:
        total_difference_amout += item.difference_amount
    if doc.discount_for_items > total_difference_amout:
        frappe.throw(f'''El descuento dado {doc.discount_for_items}
        no puede ser mayor que la diferencia total {total_difference_amout} ''')
        