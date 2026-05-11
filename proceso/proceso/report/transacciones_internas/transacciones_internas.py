# Copyright (c) 2026, Lewin Villar and contributors
# For license information, please see license.txt

import frappe
from frappe import qb
from frappe.query_builder import Criterion
def execute(filters=None):
	return get_columns(filters), get_data(filters)

def get_columns(filters):
	if filters.get("report_type") == "Purchases":
		# select name, posting_date, company, supplier, bill_no, net_total,total_taxes_and_charges, grand_total, outstanding_amount 
		return [
			{"fieldname": "name", "label": "Name", "fieldtype": "Link", "options": "Purchase Invoice", "width": 190},
			{"fieldname": "posting_date", "label": "Date", "fieldtype": "Date", "width": 100},
			{"fieldname": "company", "label": "Company", "fieldtype": "Data", "width": 120},
			{"fieldname": "supplier", "label": "Supplier", "fieldtype": "Link", "options": "Supplier", "width": 200},
			{"fieldname": "bill_no", "label": "NCF", "fieldtype": "Data", "width": 150},
			{"fieldname": "net_total", "label": "Net Total", "fieldtype": "Currency", "width": 120},
			{"fieldname": "total_taxes_and_charges", "label": "ITBIS", "fieldtype": "Currency", "width": 130},
			{"fieldname": "grand_total", "label": "Grand Total", "fieldtype": "Currency", "width": 120},
			{"fieldname": "outstanding_amount", "label": "Outstanding", "fieldtype": "Currency", "width": 150},

		]
	else:
		# select name, posting_date, company, customer, bill_no, net_total,total_taxes_and_charges, grand_total, outstanding_amount 
		return [
			{"fieldname": "name", "label": "Name", "fieldtype": "Link", "options": "Sales Invoice", "width": 150},
			{"fieldname": "posting_date", "label": "Posting Date", "fieldtype": "Date", "width": 100},
			{"fieldname": "company", "label": "Company", "fieldtype": "Data", "width": 200},
			{"fieldname": "customer", "label": "Customer", "fieldtype": "Link", "options": "Customer", "width": 200},
			{"fieldname": "ncf", "label": "NCF", "fieldtype": "Data", "width": 150},
			{"fieldname": "net_total", "label": "Net Total", "fieldtype": "Currency", "width": 120},
			{"fieldname": "total_taxes_and_charges", "label": "ITBIS", "fieldtype": "Currency", "width": 130},
			{"fieldname": "grand_total", "label": "Grand Total", "fieldtype": "Currency", "width": 120},
			{"fieldname": "outstanding_amount", "label": "Outstanding", "fieldtype": "Currency", "width": 120},

		]

def get_data(filters):
	SINV = qb.DocType("Sales Invoice")
	PINV = qb.DocType("Purchase Invoice")
	DOC = SINV if filters.get("report_type") == "Sales" else PINV
	
	conditions = [DOC.docstatus == 1]  
	
	if filters.get("company"):
		conditions.append(DOC.company == filters.get("company"))
	
	if filters.get("from_date"):
		conditions.append(DOC.posting_date >= filters.get("from_date"))
	
	if filters.get("to_date"):
		conditions.append(DOC.posting_date <= filters.get("to_date"))
	
	if filters.get("supplier") :
		conditions.append(DOC.supplier == filters.get("supplier"))
	
	if filters.get("customer") :
		conditions.append(DOC.customer == filters.get("customer"))
	
	return qb.from_(DOC).select(
		DOC.name,
		DOC.posting_date,
		DOC.company,
		DOC.supplier if filters.get("report_type") == "Purchases" else DOC.customer,
		DOC.bill_no if filters.get("report_type") == "Purchases" else DOC.ncf,
		DOC.net_total,
		DOC.total_taxes_and_charges,
		DOC.grand_total,
		DOC.outstanding_amount
	).where(Criterion.all(conditions)).run(as_dict=True, debug=True)
