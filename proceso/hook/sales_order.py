import frappe


def validate(doc, method):
    validate_discount(doc)
    set_fields(doc, method)


def validate_discount(doc):
    for item in doc.items:
        item.difference_amount = item.claimed_amount - item.authorized_amount
        if item.discount > item.difference_amount:
            frappe.throw("Los descuentos no pueden ser mayor que la diferencia")
            
def set_fields(doc, method):
     total_amount_without_discount = 0.0
     total_amount_with_discount = 0.0
     
     for item in doc.items:
         total_amount_without_discount += round(float(item.difference_amount),2)
         total_amount_with_discount += round(float(item.total),2)
         
     doc.difference_amount = total_amount_with_discount
     doc.outstanding_amount = total_amount_with_discount
     doc.net_total = total_amount_with_discount
     doc.total = total_amount_without_discount