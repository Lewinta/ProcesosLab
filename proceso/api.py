# Copyright (c) 2024, Lewin Villar and Contributors
# For license information, please see license.txt

import frappe
from frappe import _
from frappe.utils import get_url
from frappe.utils.pdf import get_pdf

__all__ = (
	"get_results",
	"get_institutions",
	"get_print_url",
	"get_team",
	"get_single_result",
	"download_result_pdf",
	"setup_customer_birthdate_flow",
)


def _upsert_custom_field(doc):
	name = f"{doc['dt']}-{doc['fieldname']}"
	if frappe.db.exists("Custom Field", name):
		existing = frappe.get_doc("Custom Field", name)
		for key, value in doc.items():
			existing.set(key, value)
		existing.save(ignore_permissions=True)
		return existing.name

	custom_field = frappe.get_doc({"doctype": "Custom Field", **doc})
	custom_field.insert(ignore_permissions=True)
	return custom_field.name


def _upsert_client_script(dt, script):
	filters = {"dt": dt, "view": "Form", "enabled": 1}
	existing_name = frappe.db.get_value("Client Script", filters, "name")
	if existing_name:
		client_script = frappe.get_doc("Client Script", existing_name)
		client_script.script = script
		client_script.save(ignore_permissions=True)
		return client_script.name

	client_script = frappe.get_doc(
		{
			"doctype": "Client Script",
			"dt": dt,
			"view": "Form",
			"enabled": 1,
			"script": script,
		}
	)
	client_script.insert(ignore_permissions=True)
	return client_script.name


def setup_customer_birthdate_flow():
	"""Configure customer and quotation DOB flow without migrate."""
	_upsert_custom_field(
		{
			"dt": "Customer",
			"fieldname": "date_of_birth",
			"label": "Date of Birth",
			"fieldtype": "Date",
			"insert_after": "territory",
			"reqd": 1,
		}
	)

	_upsert_custom_field(
		{
			"dt": "Quotation",
			"fieldname": "customer_date_of_birth",
			"label": "Fecha de Nacimiento",
			"fieldtype": "Date",
			"insert_after": "party_name",
			"fetch_from": "party_name.date_of_birth",
			"fetch_if_empty": 1,
			"reqd": 1,
		}
	)

	script = """
frappe.ui.form.on('Quotation', {
	async party_name(frm) {
		if (!frm.doc.party_name) {
			frm.set_value('customer_date_of_birth', null);
			return;
		}

		const customerResponse = await frappe.db.get_value(
			'Customer',
			frm.doc.party_name,
			'date_of_birth'
		);
		let customerDob = customerResponse && customerResponse.message
			? customerResponse.message.date_of_birth
			: null;

		if (!customerDob) {
			const patientResponse = await frappe.db.get_value(
				'Patient',
				{ customer: frm.doc.party_name },
				['name', 'dob']
			);
			const patientData = patientResponse && patientResponse.message
				? patientResponse.message
				: null;

			if (patientData && patientData.dob) {
				customerDob = patientData.dob;
				await frappe.db.set_value(
					'Customer',
					frm.doc.party_name,
					'date_of_birth',
					customerDob
				);
				frappe.msgprint({
					title: __('Fecha de Nacimiento actualizada'),
					indicator: 'green',
					message: __('Se completó la fecha de nacimiento del cliente usando el Paciente relacionado.')
				});
			}
		}

		if (customerDob) {
			await frm.set_value('customer_date_of_birth', customerDob);
			return;
		}

		await frm.set_value('customer_date_of_birth', null);
		frappe.msgprint({
			title: __('Cliente sin fecha de nacimiento'),
			indicator: 'red',
			message: __('El cliente seleccionado no tiene fecha de nacimiento configurada. Por favor, configúrala en el Cliente para continuar.')
		});
	},

	validate(frm) {
		if (frm.doc.party_name && !frm.doc.customer_date_of_birth) {
			frappe.throw(__('Debes establecer la fecha de nacimiento del cliente antes de guardar la cotización.'));
		}
	}
});
""".strip()

	_upsert_client_script("Quotation", script)

	frappe.clear_cache(doctype="Customer")
	frappe.clear_cache(doctype="Quotation")
	frappe.db.commit()
	return "OK"

@frappe.whitelist(allow_guest=True)
def get_results(filters):
	filters = frappe.parse_json(filters)
	limit = 10000
	if not filters.get("start_date") and not filters.get("end_date"):
		limit = 500
	return frappe.db.sql("""
		SELECT
			name,
			docstatus,
			fecha,
			paciente,
			institucion,
			sucursal,
			print_url
		FROM
			`tabResultado`
		WHERE
			%(conditions)s
		ORDER BY fecha desc, paciente, docstatus
		LIMIT %(limit)s """ % {
			"conditions": get_conditions(filters),
			"limit": limit
		}, as_dict=True, debug=False)

@frappe.whitelist(allow_guest=True)
def get_institutions(medico):
	if not medico:
		return frappe.db.sql("""SELECT name
			FROM `tabInstitucion`
			WHERE pertenece_a_la_pagina = 1
			ORDER BY name""", debug=False
		)
	else:
		return frappe.db.sql("""
			SELECT
				distinct(`tabResultado`.institucion) as name
			FROM
				`tabResultado`
			JOIN
				`tabInstitucion`
			ON
				`tabResultado`.institucion = `tabInstitucion`.name
			WHERE
				`tabInstitucion`.pertenece_a_la_pagina = 1
			AND
				`tabResultado`.medico = %s
			ORDER BY name""", medico, debug=False
		)


@frappe.whitelist(allow_guest=True)
def get_print_url(name, print_format="Resultados Timbrados"):
	doc = frappe.get_doc("Resultado", name)
	return "{url}/{doctype}/{name}?format={print_format}&key={key}".format(**{
		"url": get_url(),
		"doctype": "Resultado",
		"name": name,
		"print_format": print_format,
		"key": doc.get_signature()
	})

@frappe.whitelist(allow_guest=True)
def get_team(email):
	return frappe.db.get_value("Institucion", {
		"correo_electronico": email
	})
	

@frappe.whitelist(allow_guest=True)
def get_single_result(key):
	name = frappe.db.exists("Resultado", {"key":key, "docstatus": 1})
	if not name:
		return False
	url = "https://app.laboratoriobetalab.com/api/method/consultas.consultas.api.download_result_pdf?key_code={}".format(key)
	return url

@frappe.whitelist(allow_guest=True)
def download_result_pdf(key_code, format="Resultados Timbrados", no_letterhead=0):
	doctype = "Resultado"
	
	name = frappe.db.exists(doctype, {"key": key_code})
	if not name:
		frappe.local.response["type"] = "redirect"
		frappe.local.response["location"] = "/custom_404.html?key_code={}".format(key_code[0:-6])
	else:	
		html = frappe.get_print(doctype, name, format, no_letterhead=no_letterhead)
		frappe.local.response.filename = "{name}.pdf".format(name=name.replace(" ", "-").replace("/", "-"))
		frappe.local.response.filecontent = get_pdf(html)
		frappe.local.response.type = "download"
	
def get_conditions(filters):
	conditions = []
	
	if filters.get("start_date"):
		conditions.append("fecha >= '{start_date}'")
	
	if filters.get("end_date"):
		conditions.append("fecha <= '{end_date}'")
	
	if filters.get("paciente"):
		conditions.append("paciente LIKE '%{paciente}%'")
	
	if filters.get("medico"):
		conditions.append("medico = '{medico}'")
	
	if filters.get("sucursal"):
		conditions.append("sucursal = '{sucursal}'")
	
	if filters.get("institucion"):
		conditions.append("institucion = '{institucion}'")
	
	if filters.get("docstatus"):
		conditions.append("docstatus = '{docstatus}'")

	return " And ".join(conditions).format(**filters)

def borrador(doctype, docname):
	doc = frappe.get_doc(doctype,docname)
	doc.docstatus = 0
	doc.db_update()
	frappe.db.commit()

def quitar_coprologico(docname):
	doc = frappe.get_doc("Resultado",docname)
	if doc:
		doc.test_coprologico = 0
		print("removed coprologico")
	doc.db_update()
	frappe.db.commit()

def get_rango_por_edad(indice_prueba, edad):
	if not frappe.db.exists("Indice Prueba", indice_prueba):
		return "not found"
	# ip = frappe.get_value("Indice Prueba", {"prueba": prueba}, "name")

	conditions = frappe.db.sql("""
		SELECT
			condicion,
			edad_anos,
			rango_de_referencia
		FROM 
			`tabRango por Edad`
		WHERE
			parent = %s
		""", indice_prueba, as_dict=True)

	for cond in conditions:
		# print(cond.condicion)
		if cond.condicion == "Menor":
			frappe.errprint("{} {} < {}".format(cond.condicion, cond.edad_anos, edad))
			if edad < cond.edad_anos :
				return cond.rango_de_referencia

		if cond.condicion == "Igual":
			frappe.errprint("{} {} == {}".format(cond.condicion, cond.edad_anos, edad))
			if edad == cond.edad_anos:
				return cond.rango_de_referencia

		if cond.condicion == "Mayor":
			frappe.errprint("{} {} > {}".format(cond.condicion, cond.edad_anos, edad))
			if edad > cond.edad_anos:
				return cond.rango_de_referencia
	
	return " - "
