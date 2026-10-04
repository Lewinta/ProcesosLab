# Copyright (c) 2024, Lewin Villar and Contributors
# For license information, please see license.txt

import frappe
from frappe import _
from frappe.utils import cint, cstr, get_url, getdate
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

RESULTS_ROLES = ("Portal Resultados", "System Manager")


def _check_results_access():
	"""El portal entra con token de un usuario con el rol "Portal Resultados".
	Mientras el WordPress viejo siga vivo se permite Guest; para cerrarlo:
	bench --site procesos.tzcode.net set-config resultados_allow_guest 0 (no requiere reinicio)."""
	if frappe.session.user == "Guest":
		if cint(frappe.conf.get("resultados_allow_guest", 1)):
			return
		raise frappe.PermissionError
	if not set(RESULTS_ROLES) & set(frappe.get_roles()):
		raise frappe.PermissionError


@frappe.whitelist(allow_guest=True)
def get_results(filters):
	_check_results_access()
	filters = frappe._dict(frappe.parse_json(filters) or {})
	conditions, values = get_conditions(filters)
	if not conditions:
		return []
	values["limit"] = 10000 if (filters.get("start_date") or filters.get("end_date")) else 500
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
			{conditions}
		ORDER BY fecha desc, paciente, docstatus
		LIMIT %(limit)s """.format(conditions=" AND ".join(conditions)), values, as_dict=True)

@frappe.whitelist(allow_guest=True)
def get_institutions(medico=None):
	_check_results_access()
	if not medico:
		return frappe.db.sql("""SELECT name
			FROM `tabInstitucion`
			WHERE pertenece_a_la_pagina = 1
			ORDER BY name"""
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
			ORDER BY name""", medico
		)


@frappe.whitelist()
def get_print_url(name, print_format="Resultados Timbrados"):
	doc = frappe.get_doc("Resultado", name)
	doc.check_permission("read")
	return "{url}/{doctype}/{name}?format={print_format}&key={key}".format(**{
		"url": get_url(),
		"doctype": "Resultado",
		"name": name,
		"print_format": print_format,
		"key": doc.get_signature()
	})

@frappe.whitelist()
def get_team(email):
	return frappe.db.get_value("Institucion", {
		"correo_electronico": email
	})


@frappe.whitelist(allow_guest=True)
def get_single_result(key):
	"""Validación del QR: la llave (56 caracteres) es key_code + código de autorización."""
	key = (key or "").strip()
	if len(key) != 56:
		return False
	return frappe.db.get_value("Resultado", {"key": key, "docstatus": 1}, "print_url") or False

@frappe.whitelist(allow_guest=True)
def download_result_pdf(key_code, format="Resultados Timbrados", no_letterhead=0):
	doctype = "Resultado"

	name = frappe.db.exists(doctype, {"key": key_code, "docstatus": 1}) if len(key_code or "") == 56 else None
	if not name:
		frappe.local.response["type"] = "redirect"
		frappe.local.response["location"] = "/404"
	else:
		html = frappe.get_print(doctype, name, format, no_letterhead=no_letterhead)
		frappe.local.response.filename = "{name}.pdf".format(name=name.replace(" ", "-").replace("/", "-"))
		frappe.local.response.filecontent = get_pdf(html)
		frappe.local.response.type = "download"

def get_conditions(filters):
	"""Condiciones parametrizadas. Devuelve ([], {}) si no hay ningún filtro."""
	conditions, values = [], {}

	if filters.get("start_date"):
		conditions.append("fecha >= %(start_date)s")
		values["start_date"] = getdate(filters.start_date)

	if filters.get("end_date"):
		conditions.append("fecha <= %(end_date)s")
		values["end_date"] = getdate(filters.end_date)

	if filters.get("paciente"):
		conditions.append("paciente LIKE %(paciente)s")
		values["paciente"] = "%{}%".format(cstr(filters.paciente).strip()[:80])

	if filters.get("paciente_id"):
		conditions.append("cedula_pasaporte = %(paciente_id)s")
		values["paciente_id"] = cstr(filters.paciente_id).strip()

	for field in ("medico", "sucursal", "institucion"):
		if filters.get(field):
			conditions.append("{0} = %({0})s".format(field))
			values[field] = cstr(filters.get(field)).strip()

	if "instituciones" in filters:
		lista = [cstr(i).strip() for i in (filters.instituciones or []) if cstr(i).strip()]
		conditions.append("institucion IN %(instituciones)s" if lista else "1 = 0")
		if lista:
			values["instituciones"] = tuple(lista)

	if cstr(filters.get("docstatus")) in ("0", "1"):
		conditions.append("docstatus = %(docstatus)s")
		values["docstatus"] = cint(filters.docstatus)

	return conditions, values

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
