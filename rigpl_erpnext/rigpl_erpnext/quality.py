# -*- coding: utf-8 -*-
from __future__ import unicode_literals
import frappe
from frappe import msgprint, _

def fn_base_metal(bean,base_material):
	return {
		"HSS": 'H',
		"Carbide": 'C',
	}.get(base_material,"")

def fn_is_rm(bean,is_rm):
	return {
		"Yes": 'R',
	}.get(is_rm,"")

def autoname(bean, method=None):
	RM = fn_is_rm(bean, bean.doc.is_rm)
	BM = fn_base_metal(bean, bean.doc.base_material)
	QLT = bean.doc.material
	name_inter = '{0}{1}{2}{3}'.format(RM, BM, "-", QLT)
	bean.doc.name = name_inter