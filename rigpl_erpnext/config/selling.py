from frappe import _

data = [
	{
		"label": _("Rohit Reports"),
		"icon": "icon-paper-clip",
		"items": [
			{
				"type": "report",
				"is_query_report": True,
				"name": "Customers with SO",
				"doctype": "Campaign",
			},
			{
				"type": "report",
				"is_query_report": True,
				"name": "Sales Partner SO Analysis",
				"doctype": "Sales Order",
			},
			{
				"type": "report",
				"is_query_report": True,
				"name": "Trial Tracking",
				"doctype": "Sales Order",
			},
		]
	}
]