// Copyright (c) 2023, Yefri Tavarez and contributors
// For license information, please see license.txt
/* eslint-disable */

frappe.query_reports["Consultas por ARS"] = {
	"filters": [
		{
			"label": "Compania",
			"fieldname": "company",
			"fieldtype": "Link",
			"options": "Company",
			"default": frappe.defaults.get_default("company"),
			"reqd": 1,
		},
		{
			"label": "From Date",
			"fieldname": "from_date",
			"fieldtype": "Date",
		},
		{
			"label": "To Date",
			"fieldname": "to_date",
			"fieldtype": "Date",
		},
		{
			"label": "ARS",
			"fieldname": "customer",
			"fieldtype": "Link",
			"options": "Customer",
			"get_query": {
				"customer_group": "ARS"
			}
		},
	]
};
