const manage_discount_fields_si = function (frm) {
    let has_role = frappe.user.has_role('Discount manager') || frappe.user.has_role('Discount manager');

    // Hide or Show Parent fields
    let parent_fields = [
        'discount_for_items',
        'discount_on_items'
    ];

    parent_fields.forEach(f => {
        frm.set_df_property(f, 'hidden', has_role ? 0 : 1);
    });

    // Make Child fields Read Only
    let child_fields = [
        'item_discount',
        'discount_percent'
    ];

    child_fields.forEach(f => {
        // We set it as read only
        frm.fields_dict['items'].grid.update_docfield_property(f, 'read_only', has_role ? 0 : 1);
    });
};

frappe.ui.form.on('Sales Invoice', {
    refresh: function (frm) {
        manage_discount_fields_si(frm);
    }
});
