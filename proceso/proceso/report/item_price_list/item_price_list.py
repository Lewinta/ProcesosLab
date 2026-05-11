# Copyright (c) 2025, Rainier J Polanco and contributors
# For license information, please see license.txt

import frappe

# Reporte para mostrar la lista de precios de los artículos y sus articulos asociados, esto se podraa filtrar por lista de precios y articulo

def execute(filters=None):
	columns = get_columns(filters)
	data = get_data(filters)
	
	# Agregar información del reporte para impresión
	report_summary = [
		{
			"label": "Total de registros",
			"value": len(data),
			"indicator": "Blue"
		}
	]
	
	return columns, data, None, None, report_summary

def get_columns(filters):
	columns = [
		{
			"label": "Item Code",
			"fieldname": "item_code", 
			"fieldtype": "Link",
			"options": "Item",
			"width": 200
		},
		{
			"label": "Item Name",
			"fieldname": "item_name",
			"fieldtype": "Data", 
			"width": 200
		},
		{
			"label": "Price List",
			"fieldname": "price_list",
			"fieldtype": "Link",
			"options": "Price List",
			"width": 200
		},
		{
			"label": "Price",
			"fieldname": "price_list_rate",
			"fieldtype": "Currency",
			"width": 100
		}
	]
	return columns

def get_data(filters):
	# Obtener valores de filtros
	price_list = filters.get("price_list") or ""
	item_code = filters.get("item_code") or ""
	
	# Construir condiciones WHERE dinámicamente
	conditions = []
	where_clause = ""
	
	if price_list:
		conditions.append("ip.price_list = '{price_list}'".format(price_list=price_list))
	
	if item_code:
		conditions.append("ip.item_code = '{item_code}'".format(item_code=item_code))

	if conditions:
		where_clause = "WHERE " + " AND ".join(conditions)

	# Construir cláusula WHERE

	query = """
		SELECT
			ip.item_code,
			i.item_name,
			ip.price_list,
			ip.price_list_rate
		FROM
			`tabItem Price` ip
		INNER JOIN
			`tabItem` i
		ON
			ip.item_code = i.item_code
		{where_clause}

	""".format(
		where_clause=where_clause
	)

	data = frappe.db.sql(query, as_dict=True)
	return data

@frappe.whitelist()
def get_report_html(filters=None):
	"""Generar HTML personalizado para impresión"""
	columns, data, _, _, _ = execute(filters)
	
	# Crear HTML personalizado
	html = f"""
	<style>
		.custom-report {{
			font-family: Arial, sans-serif;
			max-width: 100%;
			margin: 0 auto;
		}}
		.report-header {{
			text-align: center;
			margin-bottom: 30px;
			border-bottom: 2px solid #007bff;
			padding-bottom: 20px;
		}}
		.report-title {{
			font-size: 24px;
			font-weight: bold;
			color: #333;
			margin: 10px 0;
		}}
		.filters-info {{
			background-color: #f8f9fa;
			padding: 10px;
			border-radius: 5px;
			margin-bottom: 20px;
		}}
		.data-table {{
			width: 100%;
			border-collapse: collapse;
			margin-bottom: 20px;
		}}
		.data-table th {{
			background-color: #343a40;
			color: white;
			padding: 12px 8px;
			text-align: left;
			border: 1px solid #454d55;
		}}
		.data-table td {{
			padding: 10px 8px;
			border: 1px solid #dee2e6;
		}}
		.data-table tr:nth-child(even) {{
			background-color: #f8f9fa;
		}}
		.item-code {{ font-family: monospace; font-weight: bold; }}
		.price {{ text-align: right; font-weight: bold; color: #28a745; }}
	</style>
	
	<div class="custom-report">
		<div class="report-header">
			<img src="/files/logo-procesolab.jpeg" style="width: 130px; margin-bottom: 15px;">
			<div class="report-title">Lista de Precios de Artículos</div>
			<div>Generado el {frappe.format_datetime(frappe.utils.now())}</div>
		</div>
		
		{get_filters_html(filters)}
		
		<table class="data-table">
			<thead>
				<tr>
					<th>Código de Artículo</th>
					<th>Nombre del Artículo</th>
					<th>Lista de Precios</th>
					<th>Precio</th>
				</tr>
			</thead>
			<tbody>
				{get_table_rows_html(data)}
			</tbody>
		</table>
		
		<div style="margin-top: 20px; font-size: 12px; color: #666;">
			<strong>Total de registros:</strong> {len(data)}<br>
			<strong>Generado por:</strong> Proceso Lab
		</div>
	</div>
	"""
	
	return html

def get_filters_html(filters):
	"""Generar HTML para los filtros aplicados"""
	if not filters or not any(filters.values()):
		return ""
		
	filter_html = '<div class="filters-info"><strong>Filtros aplicados:</strong><br>'
	
	if filters.get("price_list"):
		filter_html += f"Lista de Precios: {filters.get('price_list')}<br>"
	
	if filters.get("item_code"):
		filter_html += f"Código de Artículo: {filters.get('item_code')}<br>"
		
	filter_html += '</div>'
	return filter_html

def get_table_rows_html(data):
	"""Generar HTML para las filas de la tabla"""
	rows_html = ""
	for row in data:
		price_formatted = frappe.format_value(row.get('price_list_rate', 0), {"fieldtype": "Currency"})
		rows_html += f"""
		<tr>
			<td><span class="item-code">{row.get('item_code', '')}</span></td>
			<td>{row.get('item_name', '')}</td>
			<td>{row.get('price_list', '')}</td>
			<td class="price">{price_formatted}</td>
		</tr>
		"""
	return rows_html

