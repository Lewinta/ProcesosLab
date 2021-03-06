# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from . import __version__ as app_version

app_name = "proceso"
app_title = "Proceso"
app_publisher = "Lewin Villar"
app_description = "A customization app for Proceso"
app_icon = "octicon octicon-file-directory"
app_color = "grey"
app_email = "lewinvillar@tzcode.tech"
app_license = "MIT"

# Includes in <head>
# ------------------

# include js, css files in header of desk.html
# app_include_css = "/assets/proceso/css/proceso.css"
# app_include_js = "/assets/proceso/js/proceso.js"

# include js, css files in header of web template
# web_include_css = "/assets/proceso/css/proceso.css"
# web_include_js = "/assets/proceso/js/proceso.js"

# include custom scss in every website theme (without file extension ".scss")
# website_theme_scss = "proceso/public/scss/website"

# include js, css files in header of web form
# webform_include_js = {"doctype": "public/js/doctype.js"}
# webform_include_css = {"doctype": "public/css/doctype.css"}

# include js in page
# page_js = {"page" : "public/js/file.js"}

# include js in doctype views
doctype_js = {
	"User" : "public/js/user.js",
	"Task" : "public/js/task.js",
}
# doctype_list_js = {"doctype" : "public/js/doctype_list.js"}
# doctype_tree_js = {"doctype" : "public/js/doctype_tree.js"}
# doctype_calendar_js = {"doctype" : "public/js/doctype_calendar.js"}

# Home Pages
# ----------

# application home page (will override Website Settings)
# home_page = "login"

# website user home page (by Role)
# role_home_page = {
#	"Role": "home_page"
# }

app_logo_url = "/assets/proceso/images/blue_logo.svg"

website_context = {
    "favicon": 	"/assets/proceso/images/favicon.ico",
	"splash_image": "/assets/proceso/images/blue_logo.svg"
}
# Generators
# ----------

# automatically create page for each record of this doctype
# website_generators = ["Web Page"]

# Installation
# ------------

# before_install = "proceso.install.before_install"
# after_install = "proceso.install.after_install"

# Desk Notifications
# ------------------
# See frappe.core.notifications.get_notification_config

# notification_config = "proceso.notifications.get_notification_config"

# Permissions
# -----------
# Permissions evaluated in scripted ways

# permission_query_conditions = {
# 	"Event": "frappe.desk.doctype.event.event.get_permission_query_conditions",
# }
#
# has_permission = {
# 	"Event": "frappe.desk.doctype.event.event.has_permission",
# }

# DocType Class
# ---------------
# Override standard doctype classes

# override_doctype_class = {
# 	"ToDo": "custom_app.overrides.CustomToDo"
# }

# Document Events
# ---------------
# Hook on document methods and events

doc_events = {
	"User": {
		"validate": "proceso.hook.user.validate",
	},
	"Task": {
		"validate": "proceso.hook.task.validate",
	}
}

# Scheduled Tasks
# ---------------

# scheduler_events = {
# 	"all": [
# 		"proceso.tasks.all"
# 	],
# 	"daily": [
# 		"proceso.tasks.daily"
# 	],
# 	"hourly": [
# 		"proceso.tasks.hourly"
# 	],
# 	"weekly": [
# 		"proceso.tasks.weekly"
# 	]
# 	"monthly": [
# 		"proceso.tasks.monthly"
# 	]
# }

# Testing
# -------

# before_tests = "proceso.install.before_tests"

# Overriding Methods
# ------------------------------
#
# override_whitelisted_methods = {
# 	"frappe.desk.doctype.event.event.get_events": "proceso.event.get_events"
# }
#
# each overriding function accepts a `data` argument;
# generated from the base implementation of the doctype dashboard,
# along with any modifications made in other Frappe apps
# override_doctype_dashboards = {
# 	"Task": "proceso.task.get_dashboard_data"
# }

# exempt linked doctypes from being automatically cancelled
#
# auto_cancel_exempted_doctypes = ["Auto Repeat"]


# User Data Protection
# --------------------

user_data_fields = [
	{
		"doctype": "{doctype_1}",
		"filter_by": "{filter_by}",
		"redact_fields": ["{field_1}", "{field_2}"],
		"partial": 1,
	},
	{
		"doctype": "{doctype_2}",
		"filter_by": "{filter_by}",
		"partial": 1,
	},
	{
		"doctype": "{doctype_3}",
		"strict": False,
	},
	{
		"doctype": "{doctype_4}"
	}
]

