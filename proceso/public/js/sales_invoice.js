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
    frappe.run_serially([
      (_) => update_discount_on_items_label(frm),
      // (_) => set_fields(frm),
    ]);
    
  }

  function validate(frm) {
  }

  function update_discount_on_items_label(frm) {
    const fieldname = "discount_on_items";
    const property = "label";
    const value = `${__("Discount on Items")} %`;

    frm.set_df_property(fieldname, property, value);
  }

  function discount_on_items(frm) {
    //discount apply by percentage
    const { doc } = frm;

    if (is_empty(doc.discount_on_items)) {
      return "Skipping as the field is empty";
    }

    // otherwise... apply discount
    apply_discount_on_items(frm);
  }

  function discount_for_items(frm) {
    // discount apply by amount
    const { doc } = frm;

    if (is_empty(doc.discount_for_items)) {
      return "Skipping as the field is empty";
    }

    apply_discount_for_items(frm);
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
    ]);
  }

  function apply_discount_for_items(frm) {
    const { doc } = frm;
    const { discount_for_items: discount_amount } = doc;

    if (is_empty(discount_amount)) {
      frappe.throw("Ha ocurrido un error por culpa del desarrollador");
    }

    frappe.run_serially([
      (_) => frappe.dom.freeze("Espere..."),
      (_) => frappe.timeout(0.5),
      (_) => calculate_discount_for_items(frm),
      (_) => frappe.timeout(1.5),
      (_) => {
        if (frm.doc.ars) {
          frm.set_value("difference_amount_clone", frm.doc.net_total_clone);
        } else {
          frm.set_value("difference_amount", frm.doc.total);
        }
      },
      (_) => frappe.dom.unfreeze(),
    ]);
  }

  function calculate_discount_for_items(frm, cdt, cdn) {
    const { doc } = frm;
    let total_diference_amount = 0.0;

    for (const item of doc.items) {
      total_diference_amount += flt(item.difference_amount, 2);
    }
    
    const new_difference_amount = flt(total_diference_amount) - flt(doc.discount_for_items);
    const field_list = ["difference_amount_clone", "outstanding_amount_clone", "net_total_clone"];

    for (const field of field_list) {
      frm.set_value(field, new_difference_amount);
      refresh_field(field);
    }
  }

    function set_fields(frm) {
    const { doc } = frm;
    let total_amount_without_discount = 0.0;
    let total_amount_with_discount =0.0;

    for (const item of doc.items) {
      total_amount_without_discount += flt(item.difference_amount, 2);
      total_amount_with_discount += flt(item.total, 2);
    }

    const field_list = ["difference_amount_clone", "outstanding_amount_clone", "net_total_clone"];
    for (const field of field_list) {
      doc[field] = total_amount_with_discount;
      refresh_field(field);
    }
    doc.total = total_amount_without_discount;
    refresh_field("total");
  }


   function discount_item(frm, cdt, cdn) {
    calculate_percent(frm, cdt, cdn);
  }

  function discount_with_percent(frm, cdt, cdn){
    calculate_discount(frm, cdt, cdn);
  }

  function item_code(frm, cdt, cdn){
    calculate_difference_amount(frm, cdt, cdn);
    set_fields(frm);
  }

  function calculate_difference_amount(frm, cdt, cdn){
    const table_name = "items";
    const child = frappe.get_doc(cdt, cdn);
    child.difference_amount = child.claimed_amount - child.authorized_amount;
    refresh_field("difference_amount", cdn, table_name);
  }

  function calculate_percent(frm, cdt, cdn) {
    const table_name = "items";
    const child = frappe.get_doc(cdt, cdn);
    if (child.discount_item > child.difference_amount) {
      frappe.throw(`El descuento de la línea #${child.idx} 
                          no puede ser mayor que la diferencia`);
    } else {
      child.discount_with_percent = child.discount_item / child.difference_amount * 100;
      child.total = child.difference_amount - child.discount_item;
    }
    refresh_field( table_name);

    set_fields(frm);

  }


  function calculate_discount(frm, cdt, cdn) {
    const table_name = "items";
    const child = frappe.get_doc(cdt, cdn);
    if (child.discount_with_percent > 100) {
      frappe.throw(`El porciento de descuento de la línea #${child.idx} 
                          no puede ser mayor que 100`);
    } else if(child.discount_with_percent <= 100)  {
      child.discount_item = child.discount_with_percent / 100 * child.difference_amount;
      child.total = child.difference_amount - child.discount_item;
    }
    refresh_field(table_name);

    set_fields(frm);
  }

  

  frappe.ui.form.on("Sales Invoice", {
    refresh,
    validate,
    items_add,
    discount_on_items,
    discount_for_items,
  });

  frappe.ui.form.on("Sales Invoice Item", {
    discount_item,
    discount_with_percent,
    item_code,
  });
}
