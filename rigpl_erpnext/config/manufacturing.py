from frappe import _

data = [
	{
		"label": _("Rohit Reports"),
		"icon": "icon-paper-clip",
		"items": [
			{
				"type": "report",
				"is_query_report": True,
				"name": "Items For Production",
				"doctype": "Production Order",
			},
		]
	}
]