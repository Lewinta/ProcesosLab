{
    function onload(frm) {
        frm.doc.disable_rounded_total = true;
    }

    frappe.ui.form.on("Purchase Invoice", {
        onload: onload,
    });

}