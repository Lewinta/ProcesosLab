# Copyright (c) 2023, Yefri Tavarez and contributors
# For license information, please see license.txt

import frappe

from frappe.utils.background_jobs import enqueue


def after_insert(doc, method):
    enqueue(
        method="proceso.hook.price_list.remove_from_selling_settings",
        queue="long",
        enqueue_after_commit=True,
        price_list=doc.name,
    )


def remove_from_selling_settings(price_list):
    settings = frappe.get_doc("Selling Settings")

    if price_list == settings.selling_price_list:
        settings.selling_price_list = None

        # the user might not have access to this doctype
        settings.flags.ignore_permissions = True
        settings.flags.ignore_mandatory = True
        settings.save()
