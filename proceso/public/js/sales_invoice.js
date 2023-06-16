// Copyright (c) 2023, Yefri Tavarez and contributors
// For license information, please see license.txt
/* eslint-disable */

{
    const { log } = console;

    function is_empty(value) {
        // evaluate a number field and
        // will return true if value is falsy value 
        // excepting 0 value... which is falsy but still valid for the field
        return !value && value !== 0;
    }


    function test_is_empty() {
        if (
            is_empty(0) === false &&
            is_empty(4) === false &&
            is_empty(-9) === false &&
            is_empty(10) === false &&
            is_empty("") === true &&
            is_empty(null) === true &&
            is_empty(undefined) === true
        ) {
            log("test is_empty passed");
        } else {
            log("test is_empty failed");
        }
    }

    function discount_on_items(frm) {
        const { doc } = frm;

        if (is_empty(doc.discount_on_items)) {
            return "Skipping as the field is empty";;
        }

        // otherwise... apply discount
        apply_discount_on_items(frm);
    }

    function items_add(frm) {
        const { doc } = frm;

        if (is_empty(doc.discount_on_items)) {
            return "Skipping as the field is empty";
        }

        // otherwise... apply discount
        apply_discount_on_items(frm);
    }

    function apply_discount_on_items(frm) {
        const { doc } = frm;

        const { discount_on_items: value } = doc;

        if (is_empty(value)) {
            frappe.throw("Ha ocurrido un error por culpa de desarrollador");
        }

        for (const item of doc.items) {
            const { doctype, name } = item;
            const fieldname = "discount_percentage";

            frappe
                .model
                .set_value(doctype, name, fieldname, value)
                ;
        }

        validate_against_difference_amount(frm);
    }

    function validate_against_difference_amount(frm) {
        // will validate the total amount discounted
        // against the difference amount field
        // which cannot be greater than
        const { doc } = frm;

        let total_discount = 0.000;

        for (const item of doc.items) {
            // const { doctype, name } = item;
            total_discount += flt(item.discount_amount, 2);
        }

        if (total_discount > doc.difference_amount) {
            frappe.throw(
                `No es posible agregar un descuento mayor a la diferencia que pagaria el paciente.`
            );
        }

    }

    frappe.ui.form.on("Sales Invoice", {
        items_add,
        discount_on_items,
    });
}