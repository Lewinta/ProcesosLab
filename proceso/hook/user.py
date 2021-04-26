import frappe

def validate(doc, event):
    if not doc.username:
        make_username(doc)
    
    doc.update({
        "first_name": doc.first_name.capitalize(),
        "last_name": doc.last_name.capitalize(),
        "full_name": "{} {}".format(doc.first_name.capitalize(), doc.last_name.capitalize()),
    })
   
def make_username(doc):
    doc.username = '';

    if doc.first_name:
        doc.username = doc.first_name.capitalize()

    if doc.last_name and doc.username:
        doc.username = "{}_{}".format(doc.username, doc.last_name.capitalize())
    else:
        doc.username = doc.last_name.capitalize()