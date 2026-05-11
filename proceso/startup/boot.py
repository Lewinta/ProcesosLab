# Copyright (c) 2026, TzCode, S. R. L. and contributors
# For license information, please see license.txt

import frappe


def boot_session(bootinfo=None):

    if frappe.session.user == "Administrator":
        return 
    
    if not bootinfo:
        bootinfo = frappe._dict()

    if "Consultor de Sucursal" not in frappe.get_roles():
        return

    bootinfo.allowed_workspaces = 	all_pages = frappe.get_all(
        "Workspace",
        fields=["name", "category", "icon", "module"],
        filters={
            "name": ["in", ["Laboratorio"]]
        },
        ignore_permissions=True,
    )

    return bootinfo
