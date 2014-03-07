# -*- coding: utf-8 -*-
from __future__ import unicode_literals
import frappe
from frappe.model.doc import addchild

#This part of the code generates the alphanumeric series which
#does not include 0,I, O (includes 1-9 and A-Z)
#==============================
def next_string(bean,s):
	if len(s) == 0:
		return '1'
	head = s[0:-1]
	tail = s[-1]
	if tail == 'Z':
		return next_string(bean, head) + '0'
	if tail == '9':
		return head+'A'
	if tail == 'H':
		return head+'J'
	if tail == 'N':
		return head+'P'
	return head + chr(ord(tail)+1)
	
	#Code to generate the letter based on Base Metal
	#====================
def fn_base_metal(bean, base_material):
	return {
		"HSS": 'H',
		"Carbide": 'C',
	}.get(base_material,"")	

	#Code to generate the letter based on Flutes
	#====================
def fn_flutes(bean,flutes):
	return {
		1:1,
		2:2,
		3:3,
		4:4,
		5:5,
		6:6,
		7:7,
		8:8,
		9:9,
		10:'A',
	}.get(flutes,"")

	#Code to generate the letter based on Special Treatment
	#====================		
def fn_special_treatment(bean,treatment):
	return {
		"TiAlN": '1',
		"TiN": '2',
		"ACX": '3',
		"CRY": '4',
		"ALDURA": '5',
		"Hard": 'H',
	}.get(treatment,"")

	#Code to generate the letter based on RM
	#====================
def fn_isrm(bean,is_rm):
	return {
		"Yes": 'R',
	}.get(is_rm,"")
			
	#Code to generate the letter based on BRAND
	#====================
def fn_brand(bean,brand):
	return {
		"Rohit": 'R',
		"Anubis": 'A',
		"Export": 'E',
		"Groz": 'G',
	}.get(brand,"")
	
	#Code to Check the numeric fields
	#====================		
def fn_float_check(bean,float):
	if not float:
		float = 0
	else:
		if float > 999:
			frappe.msgprint("Number entered should be less than 1000", 
				raise_exception=1)
		elif float < 0:
			frappe.msgprint("Number entered should be more than Zero", 
				raise_exception=1)

def fn_check_flutes (bean,z):
	if z == "":
		frappe.msgprint("Flutes Cannot less than 1", raise_exception=1)
	elif z <1:
		frappe.msgprint("Flutes Cannot less than 1", raise_exception=1)
	elif z>10:
		frappe.msgprint("Flutes cannot be more than 10", raise_exception=1)

def fn_d1_d2 (bean,d1,d2):
	if d1 < d2:
		if bean.doc.tool_type != "SQEM" and bean.doc.base_material != "HSS":
			frappe.msgprint("D or H/D should be greater than W or D1", raise_exception=1)
	elif d1 != d2:
		if bean.doc.tool_type == "Square":
			frappe.msgprint("H/D and W should be equal for Square Tools", raise_exception=1)

def fn_length(bean,l):
	if bean.doc.is_rm == "Yes" and bean.doc.base_material== "HSS":
		if l !=0:
			frappe.msgprint("Length of HSS RM should be ZERO", raise_exception=1)
	else:
		if l ==0:
			frappe.msgprint("Length cannot be ZERO", raise_exception=1)

def fn_a1(bean, a1):
	if a1 == "" :
		frappe.msgprint("Some mandatory field missing", raise_exception=1)

def fn_l1 (bean,L,L1):
	if L <= L1:
		frappe.msgprint("L1 should be less than L", raise_exception=1)

def fn_l1_l2(bean,L,L1,L2):
	if L <= (L1 + L2):
		frappe.msgprint("L1+L2 should be less than L", raise_exception=1)

def fn_ttbased_check(bean, tt):
		# Count of Tool Type==1 below
	if tt == "Square":
		fn_d1_d2(bean, bean.doc.height_dia, bean.doc.width)
		fn_length(bean, bean.doc.length)
		fn_a1(bean, bean.doc.a1)
		
		# Count of Tool Type==4 below
	elif tt=="Rectangular" or tt=="Mandrels" or tt=="Parting":
		fn_d1_d2(bean, bean.doc.height_dia, bean.doc.width)
		bean.fn_length(bean.doc.length)
		bean.fn_a1(bean.doc.a1)

		# Count of Tool Type==8 below
	elif tt=="Ball Nose" or tt=="Drill" or tt=="Reamer" or tt=="SQEM" :
		fn_d1_d2(bean, bean.doc.height_dia, bean.doc.d1)
		fn_a1(bean, bean.doc.a1)
		fn_length(bean, bean.doc.length)
		fn_length(bean, bean.doc.l1)
		fn_l1(bean, bean.doc.length, bean.doc.l1)
		fn_check_flutes(bean, bean.doc.no_of_flutes)
		
		# Count of Tool Type==9 below
	elif tt=="Punches" :
		fn_d1_d2(bean, bean.doc.height_dia, bean.doc.d1)
		fn_a1(bean, bean.doc.a1)
		fn_length(bean, bean.doc.length)
		fn_length(bean, bean.doc.l1)
		fn_l1(bean, bean.doc.length, bean.doc.l1)

		# Count of Tool Type==10 below
	elif tt=="Centre Drill Type A":
		fn_d1_d2(bean, bean.doc.height_dia, bean.doc.d1)
		fn_length(bean, bean.doc.length)
		fn_length(bean, bean.doc.l1)
		fn_a1(bean, bean.doc.a1)
		fn_l1(bean, bean.doc.length, bean.doc.l1)
		fn_check_flutes(bean, bean.doc.no_of_flutes)
		
		# Count of Tool Type==11 below
	elif tt=="Centre Drill Type B":
		fn_d1_d2(bean, bean.doc.height_dia, bean.doc.d1)
		fn_d1_d2(bean, bean.doc.d1, bean.doc.d2)
		fn_length(bean, bean.doc.length)
		fn_length(bean, bean.doc.l1)
		fn_length(bean, bean.doc.l2)
		fn_a1(bean, bean.doc.a1)
		fn_a1(bean, bean.doc.a2)
		fn_a1(bean, bean.doc.a3)
		fn_l1(bean, bean.doc.length, bean.doc.l1)
		fn_check_flutes(bean, bean.doc.no_of_flutes)
		
		# Count of Tool Type==12 below
	elif tt=="Centre Drill Type R":
		fn_d1_d2(bean, bean.doc.height_dia, bean.doc.d1)
		fn_d1_d2(bean, bean.doc.d1, bean.doc.d2)
		fn_length(bean, bean.doc.length)
		fn_a1(bean, bean.doc.a1)
		fn_a1(bean, bean.doc.a2)
		fn_a1(bean, bean.doc.a3)
		fn_a1(bean, bean.doc.r1)
		fn_l1(bean, bean.doc.length, bean.doc.l1)
		fn_check_flutes(bean, bean.doc.no_of_flutes)

		# Count of Tool Type==13 below
	elif tt=="Punch Step3":
		fn_d1_d2(bean, bean.doc.height_dia, bean.doc.d1)
		fn_length(bean, bean.doc.length)
		fn_a1(bean, bean.doc.a1)
		fn_a1(bean, bean.doc.a2)
		fn_l1(bean, bean.doc.length, bean.doc.l1)
		fn_l1_l2(bean, bean.doc.length, bean.doc.l1, bean.doc.l2)

		# Count of Tool Type==14 below
	elif tt=="Round":
		fn_length(bean, bean.doc.length)
		fn_a1(bean, bean.doc.a1)

	#This function converts inch size
def fn_inch_size(bean, s):
	if (s):
		t = '{0}{1}'.format(s, '"')
	else:
		t = '{0}'.format("")
	return(t)

def fn_mm_size(bean,s):
	if (s):
		t = '{0:.4g}'.format(s)
		tw = '{0:.4g}{1}'.format(s,"mm")
	else:
		t = '{0}'.format("")
		tw = '{0}'.format("")
	return (t, tw)

	#Code to generate the Size Description based on the Tool Type
def fn_size_desc(bean,tooltype):
	if bean.doc.inch_h==1:
		D = fn_inch_size(bean, bean.doc.height_dia_inch)
		Dweb = fn_inch_size(bean, bean.doc.height_dia_inch)
	else:
		D = fn_mm_size(bean, bean.doc.height_dia)[0]
		Dweb = fn_mm_size(bean, bean.doc.height_dia)[1]
		

	if bean.doc.inch_w==1:
		W = fn_inch_size(bean, bean.doc.width_inch)
		Wweb = fn_inch_size(bean, bean.doc.width_inch)
	else:
		W = fn_mm_size(bean, bean.doc.width)[0]
		Wweb = fn_mm_size(bean, bean.doc.width)[1]

	if bean.doc.inch_l==1:
		L = fn_inch_size(bean, bean.doc.length_inch)
	else:
		L = fn_mm_size(bean, bean.doc.length)[0]
	
	if bean.doc.inch_d1==1:
		D1 = fn_inch_size(bean, bean.doc.d1_inch)
	else:
		D1 = fn_mm_size(bean, bean.doc.d1)[0]

	if bean.doc.inch_l1==1:
		L1 = fn_inch_size(bean, bean.doc.l1_inch)
	else:
		L1 = fn_mm_size(bean, bean.doc.l1)[0]

	if bean.doc.inch_d2==1:
		D2 = fn_inch_size(bean, bean.doc.d2_inch)
	else:
		D2 = fn_mm_size(bean, bean.doc.d2)[0]

	if bean.doc.inch_l2==1:
		L2 = fn_inch_size(bean, bean.doc.l2_inch)
	else:
		L2 = fn_mm_size(bean, bean.doc.l2)[0]
	
	if not bean.doc.a1:
		A1 = '{0}'.format("")
	else:
		A1 = '{0}{1}{2}'.format(" ",bean.doc.a1,"\xb0")
		
	if not bean.doc.a2:
		A2 = '{0}'.format("")
	else:
		A2 = '{0}{1}{2}'.format(" ",bean.doc.a2,"\xb0")
		
	if not bean.doc.a3:
		A3 = '{0}'.format("")
	else: 
		A3 = '{0}{1}{2}'.format(" ",bean.doc.a3,"\xb0")
	
	R1 = fn_mm_size(bean, bean.doc.r1)[0]
	
	if tooltype == "Ball Nose" or tooltype == "SQEM" or tooltype == "Reamer":
		if D1 != D:
			SizeDesc = '{0}{1}{2}{3}{4}{5}{6}{7}{8}{9}{10}{11}'.format("\xd8",D1, "x", L1, 
				"x\xd8", D, "x", L, A1, A2,A3 ," ")
		else:
			SizeDesc = '{0}{1}{2}{3}{4}{5}{6}{7}{8}{9}'.format("\xd8",D1, "x", L1, 
				"x", L, A1, A2,A3 ," ")
	elif tooltype == "Drill":
		if D1 != D:
			SizeDesc = '{0}{1}{2}{3}{4}{5}{6}{7}{8}{9}{10}{11}{12}'.format("\xd8",D1, "x", L1, 
				"x\xd8", D, "x", L, " PA:", A1, A2,A3 ," ")
		else:
			SizeDesc = '{0}{1}{2}{3}{4}{5}{6}{7}{8}{9}{10}'.format("\xd8",D1, "x", L1,
				"x", L, " PA:", A1, A2,A3 ," ")
	
	elif tooltype == "Centre Drill Type A" or tooltype == "Centre Drill Type B" or tooltype == "Centre Drill Type R" :
		SizeDesc = '{0}{1}{2}{3}{4}{5}{6}{7}{8}'.format("\xd8",D1, " SH:\xd8", D, " PA:",A1, A2, A3, R1, " ")
	
	elif tooltype == "Square" or tooltype == "Rectangular" or tooltype == "Mandrels" or tooltype == "Parting" :
		if bean.doc.length >0:
			SizeDesc = '{0}{1}{2}{3}{4}{5}{6}'.format(D, "x", W, "x", L, A1, " ")
			SizeDweb = '{0}{1}{2}{3}{4}{5}{6}'.format(Dweb, "x", Wweb, "x", L, A1, " ")
		else:
			SizeDesc = '{0}{1}{2}{3}'.format(D, "x", W, " ")
	
	elif tooltype == "Round" :
		if bean.doc.length >0:
			SizeDesc = '{0}{1}{2}{3}{4}{5}'.format("\xd8", D, "x", L, A1, " ")
		else:
			SizeDesc = '{0}{1}{2}'.format("\xd8", D, " ")
		
	elif tooltype == "Punches" :
		SizeDesc = '{0}{1}{2}{3}{4}{5}{6}{7}{8}{9}'.format("\xd8", D, "x", L1,"  \xd8", D1, "x", L, A1, " ")
	
	elif tooltype == "Punch Step3" :
		SizeDesc = '{0}{1}{2}{3}{4}{5}{6}{7}{8}{9}{10}{11}{12}{13}{14}'.format("\xd8", D, "x", L1, " \xd8", D1, 
			"x", L2, " \xd8", D2, "x", L, A1, A2, " ")
			
	else:
		frappe.msgprint("Unable to generate Size Description")
	return (SizeDesc)

def fn_unique_float(bean,s):
	if (s):
		if s == 0:
			t = '{0:.4f}'.format(0.0000)
		else:
			t = '{0:.4f}'.format(s)
	else:
		t = '{0:.4f}'.format(0.0000)
	return (t)

	#Code to generate the CHECK DIGIT
	#====================
def fn_check_digit(bean,id_without_check):
 
	# allowable characters within identifier
	valid_chars = "0123456789ABCDEFGHJKLMNPQRSTUVYWXZ"
	  
	# remove leading or trailing whitespace, convert to uppercase
	id_without_checkdigit = id_without_check.strip().upper()
	 
	# this will be a running total
	sum = 0;
	  
	# loop through digits from right to left
	for n, char in enumerate(reversed(id_without_checkdigit)):
			 
			if not valid_chars.count(char):
					raise Exception('InvalidIDException')
			 
			# our "digit" is calculated using ASCII value - 48
			digit = ord(char) - 48
			  
			# weight will be the current digit's contribution to
			# the running total
			weight = None
			if (n % 2 == 0):
					 
					# for alternating digits starting with the rightmost, we
					# use our formula this is the same as multiplying x 2 and
					# adding digits together for values 0 to 9.  Using the
					# following formula allows us to gracefully calculate a
					# weight for non-numeric "digits" as well (from their
					# ASCII value - 48).
					weight = (2 * digit) - int((digit / 5)) * 9
			else:
					# even-positioned digits just contribute their ascii
					# value minus 48
					weight = digit
					 
			# keep a running total of weights
			sum += weight
	  
	# avoid sum less than 10 (if characters below "0" allowed,
	# this could happen)
	sum = abs(sum) + 10
	  
	# check digit is amount needed to reach next number
	# divisible by ten. Return an integer 
	return int((10 - (sum % 10)) % 10)

def fn_add_item_website_specifications(bean):
	web_specs = [d.label for d in bean.doclist.get({"parentfield": "item_website_specification"})]
	if "H" not in web_specs:
		ch = addchild(bean.doc, 'item_website_specification', 'Item Website Specification', bean.doclist)
		ch.label = "H"
		ch.description = bean.doc.height_dia

	#Validation based on various rules
	#====================
def validate(bean, method):
	if bean.doc.tool_type != "Others":
		Check = fn_float_check(bean, bean.doc.height_dia)
		Check = fn_float_check(bean, bean.doc.width)
		Check = fn_float_check(bean, bean.doc.length)
		Check = fn_float_check(bean, bean.doc.a1)
		Check = fn_float_check(bean, bean.doc.d1)
		Check = fn_float_check(bean, bean.doc.l1)
		Check = fn_float_check(bean, bean.doc.a2)
		Check = fn_float_check(bean, bean.doc.d2)
		Check = fn_float_check(bean, bean.doc.l2)
		Check = fn_float_check(bean, bean.doc.a3)
		Check = fn_float_check(bean, bean.doc.r1)
		
			#Check values based on the tool type
			#================================================================
		Check = fn_ttbased_check (bean, bean.doc.tool_type)
		
			#Check if the BRAND selected is in unison with RM
			#============================			
		if (bean.doc.is_rm):
			if bean.doc.is_rm != frappe.db.get_value ("Brand", bean.doc.brand, "is_rm"):
				frappe.msgprint("Brand Selected is NOT ALLOWED", raise_exception=1)

			#Check if the base material selected is in unison with the quality
			#============================
		if bean.doc.base_material != frappe.db.get_value("Quality", bean.doc.quality, "base_material"):
			frappe.msgprint("Base Material and Quality Combo is WRONG", raise_exception=1)

			#Check if the IS RM selected is in unison with the quality
			#============================			
		if (bean.doc.is_rm):
			if bean.doc.is_rm != frappe.db.get_value("Quality", bean.doc.quality, "is_rm"):
				frappe.msgprint("Is RM and Quality Combo is WRONG", raise_exception=1)

			#Check for HEIGHT should always be less than WIDTH
			#============================
		if bean.doc.width >0:
			if bean.doc.height_dia > bean.doc.width:
				frappe.msgprint("HEIGHT cannot be more than WIDTH", raise_exception=1)
		
			#Check Dia Field
		
			#Check No of Flutes
			#============================
		if (bean.doc.no_of_flutes) and bean.doc.no_of_flutes >10:
			frappe.msgprint("No of Flutes cannot be more than 10", raise_exception=1)


			#Check Overall Length and Other Lengths
			#============================
		if bean.doc.length == 0 and bean.doc.is_rm != "Yes":
			frappe.msgprint("Overall Length cannot be ZERO", raise_exception=1)
		
		if bean.doc.is_rm == "Yes":
			if bean.doc.a1 >0:
				frappe.msgprint("α1 Should be Zero in case of RM", raise_exception=1)
			if bean.doc.special_treatment != "None" and bean.doc.special_treatment != "Hard":
				frappe.msgprint("Special Treatment has to be NONE or HARD in case of RM", raise_exception=1)
			if bean.doc.length >0 and bean.doc.base_material != "Carbide" :
				frappe.msgprint ("Lenght has to be ZERO for HSS RM", raise_exception = 1)
				
		fn_add_item_website_specifications(bean)
		generate_item_code(bean)

def generate_item_code(bean, method=None):
	if bean.doc.tool_type != "Others":
		#Code to generate automatic item code & description
		#============================
		BM = fn_base_metal(bean, bean.doc.base_material)		
		BMDesc = bean.doc.base_material
		serial_no = frappe.db.get_value("Item Group", "Carbide Tools" , "serial_number")
		QLT = frappe.db.get_value("Quality", bean.doc.quality , "code")
		QLTDesc = " " + frappe.db.get_value("Quality", bean.doc.quality, "description") + " "
		QTLWebD = " " + frappe.db.get_value("Quality", bean.doc.quality, "website_description") + " "
		TT = frappe.db.get_value("Tool Type", bean.doc.tool_type, "code")
		TTDesc = frappe.db.get_value("Tool Type", bean.doc.tool_type, "description") + " "
		TTWebD = frappe.db.get_value("Tool Type", bean.doc.tool_type, "website_description") + " "
		Zn = fn_flutes(bean, bean.doc.no_of_flutes)
	
		if (bean.doc.no_of_flutes):
			ZnDesc = '{0}{1}'.format(" Z= ", bean.doc.no_of_flutes)
			ZnWebD = '{0}{1}'.format(" Flutes= ", bean.doc.no_of_flutes)
		else:
			ZnDesc = '{0}'.format("")
			ZnWebD = '{0}'.format("")

		
		SPL = fn_special_treatment(bean, bean.doc.special_treatment)
		if SPL == '4':
			if bean.doc.quality == "H-3X":
				SPLDesc = '{0}'.format(" EC500 ")
			else:
				SPLDesc = '{0}'.format(" Cryo ")
		elif SPL == '3' or SPL == '2' or SPL == '1' or SPL == '5' or SPL== 'H':
			SPLDesc = '{0}{1}{2}'.format(" ", bean.doc.special_treatment, " ")
		else:
			SPLDesc = '{0}'.format("")
		
		RM = fn_isrm(bean, bean.doc.is_rm)
		if bean.doc.is_rm =="Yes":
			RMDesc = "RM "
		else:
			RMDesc = ""
	 
		BRAND = frappe.db.get_value("Brand", bean.doc.brand, "code")
		if BRAND =="X":
			BRAND = ""
	
		BRANDDesc = '{0}{1}'.format(" ", frappe.db.get_value("Brand", bean.doc.brand, "item_desc"))
	
		if bean.doc.drill_type is None:
			DTDesc = '{0}'.format("")
		else:
			DTDesc = '{0}{1}'.format(bean.doc.drill_type, " ")
	
		SizeDesc =	fn_size_desc(bean, bean.doc.tool_type)
		SizeDweb =	fn_size_desc(bean, bean.doc.tool_type)
	
		desc_inter = '{0}{1}{2}{3}{4}{5}{6}{7}{8}'.format(RMDesc, BMDesc, BRANDDesc , QLTDesc, 
			SPLDesc, DTDesc, TTDesc, SizeDesc, ZnDesc)
		desc_web = '{0}{1}{2}{3}{4}{5}{6}{7}{8}'.format(RMDesc, BMDesc, BRANDDesc , QTLWebD, 
			SPLDesc, DTDesc, TTWebD, SizeDweb, ZnWebD)
		
		item_code_intermediate = '{0}{1}{2}{3}{4}{5}{6}{7}'.format(RM, BM, QLT, TT, Zn, SPL, 
			BRAND, serial_no)
	
		CD = fn_check_digit(bean, item_code_intermediate)
	
			#below field concat is going to be used to check the integrity of data so that no one makes 2 codes for 
			#1 item.
		Du = fn_unique_float(bean, bean.doc.height_dia)
		Wu = fn_unique_float(bean, bean.doc.width)
		Lu = fn_unique_float(bean, bean.doc.length)
		A1u = fn_unique_float(bean, bean.doc.a1)
		R1u = fn_unique_float(bean, bean.doc.R1)
		D1u = fn_unique_float(bean, bean.doc.d1)
		L1u = fn_unique_float(bean, bean.doc.l1)
		D2u = fn_unique_float(bean, bean.doc.d2)
		L2u = fn_unique_float(bean, bean.doc.l2)
		A2u = fn_unique_float(bean, bean.doc.a2)
		A3u = fn_unique_float(bean, bean.doc.a3)
	
		bean.doc.concat = '{0}{1}{2}{3}{4}{5}{6}{7}{8}{9}'.format(RM, BM, QLT, TT, Zn, SPL, BRAND, Du, Wu , Lu)
		bean.doc.concat1 = '{0}{1}{2}{3}{4}{5}{6}{7}'.format(A1u, D1u, L1u, A2u, D2u, L2u, R1u, A3u)
		bean.doc.concat2= ""
		bean.doc.item_name=bean.doc.item_code
			#update the image of the item
		bean.doc.dim_image_list = frappe.db.get_value("File Data", {"attached_to_doctype": "Tool Type", 
			"attached_to_name": bean.doc.tool_type}, "file_url")
		bean.doc.description = desc_inter
		bean.doc.web_long_description = desc_web
	
		# update incremented serial_no in item group
	
		# islocal check not required as this function will be called only in autoname
		if bean.doc.fields.get("__islocal"):
			bean.doc.item_code = '{0}{1}'.format(item_code_intermediate, CD)
			bean.doc.item_name = '{0}{1}'.format(item_code_intermediate, CD)
				#increment serial_no value and assign to item_code
			next_serial_no = next_string(bean, serial_no)
			frappe.db.set_value("Item Group", "Carbide Tools", "serial_number", next_serial_no)		#This part of the code generates the alphanumeric series which does not include 0,I, O (includes 1-9 and A-Z)

