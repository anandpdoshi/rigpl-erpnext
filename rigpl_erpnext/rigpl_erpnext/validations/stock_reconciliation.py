# -*- coding: utf-8 -*-
from __future__ import unicode_literals
import frappe
from frappe import msgprint

def validate(doc,method):
	#Get Stock Valuation from Item Table
	for d in doc.items:
		query = """SELECT valuation_rate, is_purchase_item FROM `tabItem` WHERE name = '%s' """ % d.item_code
		vr = frappe.db.sql(query, as_list=1)
		if vr[0][0] != 0 or vr[0][0]:
			if d.warehouse == "REJ-DEL20A - RIGPL":
				d.valuation_rate = 1
			elif d.warehouse == "Dead Stock - RIGPL":
				d.valuation_rate = (vr[0][0]/4)
			elif d.valuation_rate == 1 or d.valuation_rate == 0:
				pass
			else:
				d.valuation_rate = vr[0][0]
		else:
			d.valuation_rate = 1	