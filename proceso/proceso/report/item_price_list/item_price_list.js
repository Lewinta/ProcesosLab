// Copyright (c) 2025, Lewin Villar and contributors
// For license information, please see license.txt
/* eslint-disable */

frappe.query_reports["Item Price List"] = {
	"filters": [
		{
			"fieldname": "item_code",
			"label": __("Item Code"),
			"fieldtype": "Link",
			"options": "Item",
		},
		{
			"fieldname": "price_list",
			"label": __("Price List"),
			"fieldtype": "Link",
			"options": "Price List",
		}
	],
	
	"onload": function(report) {
		// Personalizar el título del reporte
		report.page.set_title(__("Lista de Precios de Artículos"));
	},
	
	"after_datatable_render": function(datatable_obj) {
		// Agregar estilos CSS personalizados
		$('<style>')
		.prop('type', 'text/css')
		.html(`
			.dt-scrollable table thead th {
				background-color: #343a40 !important;
				color: white !important;
				font-weight: bold !important;
			}
			.dt-scrollable table tbody tr:nth-child(even) {
				background-color: #f8f9fa !important;
			}
			.dt-scrollable table tbody tr:hover {
				background-color: #e9ecef !important;
			}
			.item-code {
				font-family: monospace;
				font-weight: bold;
			}
			.price {
				text-align: right;
				font-weight: bold;
				color: #28a745;
			}
		`)
		.appendTo('head');
	},
	
	"get_print_html": function(filters) {
		// Usar nuestro HTML personalizado para impresión
		return frappe.call({
			method: "proceso.proceso.report.item_price_list.item_price_list.get_report_html",
			args: {
				filters: filters
			},
			callback: function(r) {
				if (r.message) {
					// Abrir en nueva ventana para imprimir
					var printWindow = window.open('', '_blank');
					printWindow.document.write(r.message);
					printWindow.document.close();
					printWindow.print();
				}
			}
		});
	}
};
