import frappe


def validate(doc, method):
    validate_discount(doc)
    validate_against_difference_amount(doc, method)
    validate_discount_for_items(doc, method)


def validate_discount(doc):
    for item in doc.items:
        item.difference_amount = item.claimed_amount - item.authorized_amount
        tolerance = 1e-3  # Puedes ajustar la tolerancia según tus necesidades
        if item.discount_item > item.difference_amount + tolerance:
            frappe.throw(f'''El descuento de la línea {item.idx} 
            no puede ser mayor que la diferencia''')

def validate_against_difference_amount(doc, method):
    total_discount = 0
    total_difference_amout = 0

    for item in doc.items:
        total_discount += item.discount_item
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
        