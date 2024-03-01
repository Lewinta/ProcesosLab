// Copyright (c) 2024, Yefri Tavarez and contributors
// For license information, please see license.txt
/* eslint-disable */

{
	function refresh(frm) {
		add_intro_section(frm);
	}

	function add_intro_section(frm) {
		const { doc } = frm;

		if (doc.data_source === "Legacy System") {
			frm.set_intro();
			frm.set_intro("🥱 Este es un Resultado archivado de solo lectura que vino de otro sistema antigüo.", "yellow");

			frm.disable_form();
		}
	}

	frappe.ui.form.on("Resultado", {
		refresh,
	});
}