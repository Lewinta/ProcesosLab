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

  function refresh(frm) {
    frappe.run_serially([(_) => update_discount_on_items_label(frm)]);
  }

  function validate(frm) {
    frappe.run_serially([(_) => validate_against_difference_amount(frm)]);
  }

  function update_discount_on_items_label(frm) {
    const fieldname = "discount_on_items";
    const property = "label";
    const value = `${__("Discount on Items")} %`;

    frm.set_df_property(fieldname, property, value);
  }

  function discount_on_items(frm) {
    const { doc } = frm;

    if (is_empty(doc.discount_on_items)) {
      return "Skipping as the field is empty";
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

    frappe.run_serially([
      (_) => frappe.dom.freeze("Espere..."),
      (_) => frappe.timeout(0.5),
      (_) => {
        for (const item of doc.items) {
          const { doctype, name } = item;
          const fieldname = "discount_with_percent";

          frappe.model.set_value(doctype, name, fieldname, value);
        }
      },
      (_) => frappe.timeout(1.5),
      (_) => frappe.dom.unfreeze(),
      (_) => validate_against_difference_amount(frm),
    ]);
  }

  function validate_against_difference_amount(frm) {
    // will validate the total amount discounted
    // against the difference amount field
    // which cannot be greater than
    frappe.validated = false;

    const { doc } = frm;
    let total_discount = 0.0;   
    for (const item of doc.items) {
      // const { doctype, name } = item;
     total_discount += flt(item.discount_amount, 2);
    
    }

    if (total_discount > doc.difference_amount) {
      frappe.throw(
        `No es posible agregar un descuento mayor a la diferencia que pagaria el paciente.`
      );
    } else {
      frappe.validated = true;
    }
    set_fields(frm);
  }

  function set_fields(frm) {
    const { doc } = frm;
    let total_amount_without_discount = 0.0;
    let total_amount_with_discount =0.0;

    for (const item of doc.items) {
      total_amount_without_discount += flt(item.difference_amount, 2);
      total_amount_with_discount += flt(item.total, 2);
    }
    const field_list = ["difference_amount_clone", "outstanding_amount", "net_total_clone"];

      for (const field of field_list) {
          doc[field] = total_amount_with_discount;
          refresh_field(field);
      }

      doc.total = total_amount_without_discount;
      refresh_field("total");
  }

  function discount(frm, cdt, cdn) {
    calculate_percent(frm, cdt, cdn);
  }

  function discount_with_percent(frm, cdt, cdn){
    calculate_discount(frm, cdt, cdn);
  }

  function item_code(frm, cdt, cdn){
    calculate_difference_amount(frm, cdt, cdn);
  }

  function calculate_difference_amount(frm, cdt, cdn){
    const table_name = "items";
    const child = frappe.get_doc(cdt, cdn);
    child.difference_amount = child.claimed_amount - child.authorized_amount;
    refresh_field(table_name);
  }

  function calculate_percent(frm, cdt, cdn) {
    const table_name = "items";
    const child = frappe.get_doc(cdt, cdn);
    if (child.discount > child.difference_amount) {
      frappe.throw(`El descuento de la línea #${child.idx} 
                          no puede ser mayor que la diferencia`);
    } else {
      // child.difference_amount -= child.discount;
      child.discount_with_percent = child.discount / child.difference_amount * 100;
      child.total = child.difference_amount - child.discount;
    }
    refresh_field(table_name);

    set_fields(frm);
  }


  function calculate_discount(frm, cdt, cdn) {
    const table_name = "items";
    const child = frappe.get_doc(cdt, cdn);
    if (child.discount_with_percent > 100) {
      frappe.throw(`El porciento de descuento de la línea #${child.idx} 
                          no puede ser mayor que 100`);
    } else {
      child.discount = child.discount_with_percent / 100 * child.difference_amount;
      child.total = child.difference_amount - child.discount;
    }
    refresh_field(table_name);

    set_fields(frm);
  }

  frappe.ui.form.on("Sales Order", {
    refresh,
    validate,
    items_add,
    discount_on_items,
  });

  frappe.ui.form.on("Sales Order Item", {
    discount,
    discount_with_percent,
    item_code,
  });
}
