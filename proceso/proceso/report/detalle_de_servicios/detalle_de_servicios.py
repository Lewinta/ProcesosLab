# Copyright (c) 2026, Lewin Villar and contributors
# For license information, please see license.txt

# Copyright (c) 2026
# For license information, please see license.txt

import frappe
from frappe import qb
from frappe.query_builder import functions as fn


def execute(filters=None):
    filters = filters or {}

    columns = get_columns()
    data = get_data(filters)

    return columns, data


def get_columns():
    return [
        {
            "label": "Item Code",
            "fieldname": "item_code",
            "fieldtype": "Data",
            "width": 150,
        },
        {
            "label": "Item Name",
            "fieldname": "item_name",
            "fieldtype": "Data",
            "width": 300,
        },
        {
            "label": "Qty",
            "fieldname": "qty",
            "fieldtype": "Float",
            "width": 120,
        },
        {
            "label": "Amount",
            "fieldname": "amount",
            "fieldtype": "Currency",
            "width": 150,
        },
    ]


def get_data(filters):
    source = filters.get("source")

    if source == "Sales Order":
        return get_from_sales_order(filters)
    else:
        # Default to Sales Invoice
        return get_from_sales_invoice(filters)


def get_from_sales_invoice(filters):
    SI = qb.DocType("Sales Invoice")
    SII = qb.DocType("Sales Invoice Item")

    query = (
        qb.from_(SII)
        .join(SI)
        .on(SII.parent == SI.name)
        .select(
            SII.item_code,
            SII.item_name,
            fn.Sum(SII.qty).as_("qty"),
            fn.Sum(SII.qty * SII.rate).as_("amount"),
        )
        .where(
            (SI.docstatus == 1)
            & (SI.company == filters.company)
            & (SI.posting_date.between(filters.from_date, filters.to_date))
        )
        .groupby(SII.item_code)
    )

    if filters.get("branch"):
        query = query.where(SI.sucursal == filters.branch)

    return query.run(as_dict=True)


def get_from_sales_order(filters):
    SO = qb.DocType("Sales Order")
    SOI = qb.DocType("Sales Order Item")

    query = (
        qb.from_(SOI)
        .join(SO)
        .on(SOI.parent == SO.name)
        .select(
            SOI.item_code,
            SOI.item_name,
            fn.Sum(SOI.qty).as_("qty"),
            fn.Sum(SOI.qty * SOI.rate).as_("amount"),
        )
        .where(
            (SO.docstatus == 1)
            & (SO.company == filters.company)
            & (SO.transaction_date.between(filters.from_date, filters.to_date))
        )
        .groupby(SOI.item_code)
    )

    if filters.get("branch"):
        query = query.where(SO.sucursal == filters.branch)

    return query.run(as_dict=True)