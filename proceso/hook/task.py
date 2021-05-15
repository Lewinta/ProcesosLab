import frappe

def validate(doc, method):
    update_task_color(doc)

def update_task_color(doc):
    if doc.is_group:
        filters = {"parent_task": doc.name}
        for name, in frappe.get_list("Task", filters, as_list=True):
            child = frappe.get_doc("Task", name)
            child.color = doc.color
    else:
        if not doc.parent_task:
            return 
        doc.color = frappe.get_value(
            "Task",
            doc.parent_task,
            "color"
        )