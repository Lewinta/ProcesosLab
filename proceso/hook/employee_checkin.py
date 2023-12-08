import frappe

def after_insert(doc, method):
    doc.log_type = get_next_log(doc)
    doc.db_update()

def get_next_log(doc):
    dt = str(doc.time)[0:10]
    last = frappe.db.sql("""
        SELECT 
            MAX(time), 
            `log_type`
        FROM 
            `tabEmployee Checkin`
        WHERE
           `employee` = %s
        AND
            CAST(`time` as DATE) = %s
    """, (doc.employee, dt), as_dict=True)[0]
    
    if (not last.log_type or last.log_type == "OUT"):
        return "IN"
    else:
        return "OUT"