# Copyright (c) 2024, Yefri Tavarez and Contributors
# For license information, please see license.txt

import frappe

def get_permission_query_conditions(user=None):
    if not user:
        user = frappe.session.user

    # if user == "Administrator":
    #     return ""


    return """
        `tabResultado`.data_source = "User Input"
    """
