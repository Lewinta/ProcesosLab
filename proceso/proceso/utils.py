import frappe
from datetime import datetime
from frappe.utils import nowdate, add_days

shift = frappe.get_doc("Shift Type", "JORNADA REG 8-5")
dt = shift.process_attendance_after
while dt <= datetime.fromisoformat("2022-04-23 00:00:00").date():
	shift.process_attendance_after = dt
	shift.last_sync_of_checkin = f"{dt} 20:00:00"
	shift.process_auto_attendance()
	print(f"Processing {dt}")
	dt = add_days(dt, 1)
	shift.save()