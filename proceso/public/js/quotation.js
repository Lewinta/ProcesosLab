// Copyright (c) 2026, Rainier J Polanco and contributors
//  For license information, please see license.txt

frappe.ui.form.on('Quotation', {
    party_name: async function(frm) {
        const { doc } = frm;

        if (doc.party_name){
            try {
                const r = await frappe.db.get_value("Patient", { customer: doc.party_name }, 'name');
                if (r && r.message) {
                    frm.set_value('patient', r.message.name);
                }
            } catch (err) {
                // fallo silencioso: log para debugging
                console.error('Patient lookup failed', err);
            }
        }
    }

});