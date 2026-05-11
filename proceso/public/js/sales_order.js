const manage_discount_fields = function (frm) {
    let has_role = frappe.user.has_role('Discount manager') || frappe.user.has_role('Discount manager');
    console.log(`tiene el rol??: ${has_role}`);

    // Hide or Show Parent fields
    let parent_fields = [
        'apply_discount_on',
        'base_discount_amount',
        'additional_discount_percentage',
        'discount_on_items'
    ];

    parent_fields.forEach(f => {
        frm.set_df_property(f, 'hidden', has_role ? 0 : 1);
    });

    // Make Child fields Read Only
    let child_fields = [
        'discount_percent',
        'discount'
    ];

    child_fields.forEach(f => {
        // We set it as read only
        frm.fields_dict['items'].grid.update_docfield_property(f, 'read_only', has_role ? 0 : 1);
    });
};

frappe.ui.form.on('Sales Order', {
    refresh: function (frm) {
        manage_discount_fields(frm);
    }
});
