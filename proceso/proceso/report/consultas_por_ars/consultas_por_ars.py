# Copyright (c) 2023, Yefri Tavarez and contributors
# For license information, please see license.txt

import frappe


def execute(filters=None):
	report = TestReport(filters)
	return report.run()


class TestReport():
	def __init__(self, filters):
		self.auto_set_filters(filters)
		self.initialize_class()

	def initialize_class(self):
		self.columns = list()
		self.data = list()

	def auto_set_filters(self, filters):
		self.report_filters = filters

		for fieldname in filters.keys():
			value = filters[fieldname]
			setattr(self, fieldname, value)

	def run(self):
		self.setup_columns()
		self.setup_data()

		return self.columns, self.data

	def setup_columns(self):
		columns = list()

		columns.append({
			"label": "Name",
			"fieldname": "name",
			"fieldtype": "Link",
			"options": "Sales Invoice",
			"width": "200",
		})

		columns.append({
			"label": "Compañia",
			"fieldname": "company",
			"fieldtype": "Link",
			"options": "Company",
			"width": "120",
		})

		columns.append({
			"label": "Fecha",
			"fieldname": "posting_date",
			"fieldtype": "Date",
			"width": "100",
		})

		columns.append({
			"label": "ARS",
			"fieldname": "ars_name",
			"fieldtype": "Data",
			"width": "220",
		})

		# columns.append({
		# 	"label": "Cobertura",
		# 	"fieldname": "insurance_coverage",
		# 	"fieldtype": "Percent",
		# 	"width": "80",
		# })

		columns.append({
			"label": "Customer",
			"fieldname": "customer_name",
			"fieldtype": "Data",
			"width": "260",
		})

		columns.append({
			"label": "Paciente",
			"fieldname": "patient",
			"fieldtype": "Link",
			"options": "Patient",
			"width": "260",
		})

		columns.append({
			"label": "NSS",
			"fieldname": "nss",
			"fieldtype": "Data",
			"width": "140",
		})

		columns.append({
			"label": "Monto Reclamado",
			"fieldname": "claimed_amount",
			"fieldtype": "Currency",
		})

		columns.append({
			"label": "Monto Autorizado",
			"fieldname": "authorized_amount",
			"fieldtype": "Currency",
		})

		columns.append({
			"label": "Diferencia",
			"fieldname": "difference_amount",
			"fieldtype": "Currency",
		})

		self.columns = columns

	def setup_data(self):
		query = self.get_query()

		for row in frappe.db.sql(query, self.report_filters, as_dict=True):
			self.post_process_row(row)
			self.data.append(row)

	def post_process_row(self, row):
		pass

	def get_query(self):
		return frappe.render_template("""
			Select
				Distinct(invoice.name) As name,
				invoice.company,
				invoice.posting_date,
				invoice.ars_name,
				invoice.insurance_coverage,
				invoice.customer_name,
				invoice.patient,
				invoice.nss,
				invoice.claimed_amount,
				invoice.authorized_amount,
				invoice.difference_amount
			From
				`tabSales Invoice` As invoice
			Inner Join
				`tabSales Invoice Item` As item
				On item.parent = invoice.name
				And item.parenttype = "Sales Invoice"
				And item.parentfield = "items"
			Where
				invoice.docstatus = 1
				And item.is_covered = 1

				{% if company %}
					And invoice.company = %(company)s
				{% endif %}

				{% if from_date %}
					And invoice.posting_date >= %(from_date)s
				{% endif %}

				{% if to_date %}
					And invoice.posting_date <= %(to_date)s
				{% endif %}

				{% if customer %}
					And invoice.ars = %(customer)s
				{% endif %}

		""", self.report_filters)

	company: str = None
	from_date: str = None
	to_date: str = None
	customer: str = None
	columns: list = None
	data: list = None
	report_filters: dict = None
