# -*- coding: utf-8 -*-
from __future__ import unicode_literals
import frappe, erpnext
import math
import datetime
from frappe import msgprint
from frappe.model.mapper import get_mapped_doc
from frappe.utils import money_in_words, flt
from erpnext.accounts.general_ledger import make_gl_entries, delete_gl_entries
from erpnext.accounts.utils import get_fiscal_years, validate_fiscal_year, get_account_currency
from erpnext.hr.doctype.payroll_entry.payroll_entry import get_month_details, get_start_end_dates
from erpnext.hr.doctype.employee.employee import get_holiday_list_for_employee
from erpnext.hr.doctype.salary_slip.salary_slip import SalarySlip
from erpnext.accounts.utils import get_fiscal_year

def post_gl_entry(doc):
	comp_doc = frappe.get_doc("Company", doc.company)
	gl_map = []
	fiscal_year = get_fy(doc)
	ec_ded = 0
	
	for earn in doc.earnings:
		earn_doc = frappe.get_doc("Salary Component", earn.salary_component)
		if earn.amount != 0 and earn.expense_claim is None and earn_doc.only_for_deductions != 1:
			#Condition for Earning Posting which is actually paid and not just for calculation
			gl_dict = frappe._dict({
				'company': doc.company,
				'posting_date' : doc.posting_date,
				'fiscal_year': fiscal_year,
				'voucher_type': 'Salary Slip',
				'voucher_no': doc.name,
				'account': earn_doc.account,
				'cost_center': comp_doc.cost_center,
				'debit': flt(earn.amount),
				'debit_in_account_currency': flt(earn.amount),
				'against': comp_doc.default_payroll_payable_account
			})
			gl_map.append(gl_dict)
		elif earn.expense_claim and earn.amount > 0:
			ec_gl_map = []
			ec_ded += earn.amount
			#Check if the expense claim is already posted if not then post the expense claim
			#separately
			ec_posted = frappe.db.sql("""SELECT name FROM `tabGL Entry` WHERE docstatus =1 AND
				voucher_type = 'Expense Claim' AND voucher_no = '%s'
				"""%(earn.expense_claim), as_list=1)
			if not ec_posted:
				
				#Post the Expense Claim Separately.	
				ec_doc = frappe.get_doc("Expense Claim", earn.expense_claim)
				for exp in ec_doc.expenses:
					ecfy = get_fy(ec_doc)
					ec_gl_dict = frappe._dict({
						'company': ec_doc.company,
						'posting_date' : ec_doc.posting_date,
						'fiscal_year': ecfy,
						'voucher_type': 'Expense Claim',
						'voucher_no': ec_doc.name,
						'account': exp.default_account,
						'cost_center': comp_doc.cost_center,
						'debit': flt(exp.sanctioned_amount),
						'debit_in_account_currency': flt(exp.sanctioned_amount),
						'against': ec_doc.employee
					})
					ec_gl_map.append(ec_gl_dict)
				ec_gl_dict = frappe._dict({
					'company': ec_doc.company,
					'posting_date' : ec_doc.posting_date,
					'fiscal_year': ecfy,
					'voucher_type': 'Expense Claim',
					'voucher_no': ec_doc.name,
					'account': (ec_doc.payable_account or comp_doc.default_payroll_payable_account),
					'cost_center': (ec_doc.cost_center or comp_doc.cost_center),
					'party_type': 'Employee',
					'party': ec_doc.employee,
					'credit': flt(ec_doc.total_sanctioned_amount),
					'credit_in_account_currency': flt(ec_doc.total_sanctioned_amount)
				})
				ec_gl_map.append(ec_gl_dict)
				make_gl_entries(ec_gl_map, cancel=0, adv_adj=0)
				frappe.msgprint(("Posted Expense Claim # {0}").format(earn.expense_claim))
				
	for ded in doc.deductions:
		ded_doc = frappe.get_doc("Salary Component", ded.salary_component)
		if flt(ded.amount) > 0 and ded.employee_loan is None:
			gl_dict = frappe._dict({
				'company': doc.company,
				'posting_date' : doc.posting_date,
				'fiscal_year': fiscal_year,
				'voucher_type': 'Salary Slip',
				'voucher_no': doc.name,
				'account': ded_doc.account,
				'credit': flt(ded.amount),
				'credit_in_account_currency': flt(ded.amount),
				'against': comp_doc.default_payroll_payable_account
			})
			gl_map.append(gl_dict)
		elif flt(ded.amount) > 0 and ded.employee_loan is not None:
			gl_dict = frappe._dict({
				'company': doc.company,
				'posting_date' : doc.posting_date,
				'fiscal_year': fiscal_year,
				'voucher_type': 'Salary Slip',
				'voucher_no': doc.name,
				'account': ded_doc.account,
				'credit': flt(ded.amount),
				'credit_in_account_currency': flt(ded.amount),
				'party_type': 'Employee',
				'party': doc.employee,
				'against': ded.employee_loan
			})
			gl_map.append(gl_dict)
	if gl_map:	
		gl_dict = frappe._dict({
			'company': doc.company,
			'posting_date' : doc.posting_date,
			'fiscal_year': fiscal_year,
			'voucher_type': 'Salary Slip',
			'voucher_no': doc.name,
			'account': comp_doc.default_payroll_payable_account,
			'credit': flt(doc.rounded_total - ec_ded),
			'credit_in_account_currency': flt(doc.rounded_total - ec_ded),
			'party_type': 'Employee',
			'party': doc.employee,
			'against': comp_doc.default_payroll_payable_account
		})
		gl_map.append(gl_dict)
		gl_dict = frappe._dict({
			'company': doc.company,
			'posting_date' : doc.posting_date,
			'fiscal_year': fiscal_year,
			'voucher_type': 'Salary Slip',
			'voucher_no': doc.name,
			'account': comp_doc.round_off_account,
			'cost_center': comp_doc.round_off_cost_center,
			'debit': flt(doc.rounded_total - doc.net_pay),
			'debit_in_account_currency': flt(doc.rounded_total - doc.net_pay),
			'against': comp_doc.default_payroll_payable_account
		})
		gl_map.append(gl_dict)
			
	for cont in doc.contributions:
		if cont.amount > 0:
			cont_doc = frappe.get_doc("Salary Component", cont.salary_component)
			gl_dict = frappe._dict({
				'company': doc.company,
				'posting_date' : doc.posting_date,
				'fiscal_year': fiscal_year,
				'voucher_type': 'Salary Slip',
				'voucher_no': doc.name,
				'account': cont_doc.account,
				'cost_center': comp_doc.cost_center,
				'debit': flt(cont.amount),
				'debit_in_account_currency': flt(cont.amount),
				'against': cont_doc.liability_account
			})
			gl_map.append(gl_dict)
			gl_dict = frappe._dict({
				'company': doc.company,
				'posting_date' : doc.posting_date,
				'fiscal_year': fiscal_year,
				'voucher_type': 'Salary Slip',
				'voucher_no': doc.name,
				'account': cont_doc.liability_account,
				'credit': flt(cont.amount),
				'credit_in_account_currency': flt(cont.amount),
				'against': cont_doc.account
			})
			gl_map.append(gl_dict)
	make_gl_entries(gl_map, cancel=0, adv_adj=0)
		
def get_fy(document):
	fiscal_years = get_fiscal_years(document.posting_date, company=document.company)
	if len(fiscal_years) > 1:
		frappe.throw(_("Multiple fiscal years exist for the date {0}. \
			Please set company in Fiscal Year").format(formatdate(document.posting_date)))
	else:
		fiscal_year = fiscal_years[0][0]
	return fiscal_year

def on_submit(doc,method):
	if doc.net_pay < 0:
		frappe.throw(("Negative Net Pay Not Allowed for {0}").format(doc.name))
		
	#Update the expense claim amount cleared so that no new JV can be made
	for i in doc.earnings:
		if i.expense_claim:
			ec = frappe.get_doc("Expense Claim", i.expense_claim)
			frappe.db.set_value("Expense Claim", i.expense_claim, "total_amount_reimbursed", \
				i.amount)
			frappe.db.set_value("Expense Claim", i.expense_claim, "status", "Paid")

	#post the salary slip to GL entry table
	post_gl_entry(doc)	
			
def on_cancel(doc,method):
	#Update the expense claim amount cleared so that no new JV can be made
	for i in doc.earnings:
		if i.expense_claim:
			ec = frappe.get_doc("Expense Claim", i.expense_claim)
			frappe.db.set_value("Expense Claim", i.expense_claim, "total_amount_reimbursed", 0)
			frappe.db.set_value("Expense Claim", i.expense_claim, "status", "Unpaid")
	delete_gl_entries(None, 'Salary Slip', doc.name)
	
def validate(doc,method):
	get_edc(doc)
	update_fields(doc)
	msd, med = get_month_dates(doc)
	get_loan_deduction(doc, msd, med)
	get_expense_claim(doc, med)
	calculate_net_salary(doc, msd, med)
	table = ['earnings', 'deductions', 'contributions']
	recalculate_formula(doc, table)
	validate_ec_posting(doc)

def update_fields(doc):
	sstr = frappe.get_doc("Salary Structure", doc.salary_structure)
	doc.letter_head = sstr.letter_head
	doc.deparment = frappe.get_value("Employee", doc.employee, "department")

def validate_ec_posting(doc):
	comp_doc = frappe.get_doc("Company", doc.company)
	for e in doc.earnings:
		if e.expense_claim:
			#Check if the expense claim is properly posted in  Expenses Payable
			posted = frappe.db.sql("""SELECT name FROM `tabGL Entry` 
					WHERE voucher_type = 'Expense Claim' AND voucher_no = '%s'
					AND docstatus = 1""" %(e.expense_claim), as_list=1)
			if posted:
				for ec_claim in posted:
					#Check Credit Entry's account should be Expenses Payable
					debit = frappe.db.sql("""SELECT name, credit, account
						FROM `tabGL Entry` WHERE name = '%s'"""%(ec_claim[0]), as_list=1)
						
					if debit[0][1] > 0:
						if debit[0][2] != comp_doc.default_payroll_payable_account:
							frappe.throw(("Expense Claim {0} in Salary Slip {1} is not posted \
							correctly").format(e.expense_claim, doc.name))
	
def recalculate_formula(doc, table):
	data = SalarySlip.get_data_for_eval(doc)
	salary_structure_doc = frappe.get_doc("Salary Structure", doc.salary_structure)
	for table_name in table:
		for comp in salary_structure_doc.get(table_name):
			amount = SalarySlip.eval_condition_and_formula(doc, comp, data)
	
def calculate_net_salary(doc, msd, med):
	gross_pay = 0
	net_pay = 0
	tot_ded = 0
	tot_cont = 0
	tot_books = 0
	emp = frappe.get_doc("Employee", doc.employee)
	tdim, twd = get_total_days(doc, emp, msd, med)
	holidays = get_holidays(doc, msd, med, emp)
	lwp, plw = get_leaves(doc, msd, med, emp)
	doc.leave_without_pay = lwp
	doc.posting_date = med
	wd = twd - holidays #total working days
	doc.total_days_in_month = tdim
	att = frappe.db.sql("""SELECT sum(overtime), count(name) FROM `tabAttendance` 
		WHERE employee = '%s' AND attendance_date >= '%s' AND attendance_date <= '%s' 
		AND status = 'Present' AND docstatus=1""" \
		%(doc.employee, msd, med),as_list=1)

	half_day = frappe.db.sql("""SELECT count(name) FROM `tabAttendance` 
		WHERE employee = '%s' AND attendance_date >= '%s' AND attendance_date <= '%s' 
		AND status = 'Half Day' AND docstatus=1""" \
		%(doc.employee, msd, med),as_list=1)
	
	t_hd = flt(half_day[0][0])
	t_ot = flt(att[0][0])
	doc.total_overtime = t_ot
	tpres = flt(att[0][1])

	ual = twd - tpres - lwp - holidays - plw - (t_hd/2)
	
	if ual < 0:
		frappe.throw(("Unauthorized Leave cannot be Negative for Employee {0}").\
			format(doc.employee_name))
	
	paydays = tpres + (t_hd/2) + plw + math.ceil((tpres+(t_hd/2))/wd * holidays)
	pd_ded = flt(doc.payment_days_for_deductions)
	doc.payment_days = paydays
	
	if doc.change_deductions == 0:
		doc.payment_days_for_deductions = doc.payment_days
		
	if doc.payment_days_for_deductions == doc.payment_days:
		doc.change_deductions = 0
	
	doc.unauthorized_leaves = ual 
	
	ot_ded = round(8*ual,1)
	if ot_ded > t_ot:
		ot_ded = (int(t_ot/8))*8
	doc.overtime_deducted = ot_ded
	d_ual = int(ot_ded/8)

	#Calculate Earnings
	chk_ot = 0 #Check if there is an Overtime Rate
	for d in doc.earnings:
		if d.salary_component == "Overtime Rate":
			chk_ot = 1
	
	for d in doc.earnings:
		earn = frappe.get_doc("Salary Component", d.salary_component)
		if earn.depends_on_lwp == 1:
			d.depends_on_lwp = 1
		else:
			d.depends_on_lwp = 0

		if earn.based_on_earning:
			for d2 in doc.earnings:
				#Calculate Overtime Value
				if earn.earning == d2.salary_component:
					d.default_amount = flt(d2.amount) * t_ot
					d.amount = flt(d2.amount) * (t_ot - ot_ded)
		else:
			if d.depends_on_lwp == 1 and earn.books == 0:
				if chk_ot == 1:
					d.amount = round(flt(d.default_amount) * (paydays+d_ual)/tdim,0)
				else:
					d.amount = round(flt(d.default_amount) * (paydays)/tdim,0)
			elif d.depends_on_lwp == 1 and earn.books == 1:
				d.amount = round(flt(d.default_amount) * flt(doc.payment_days_for_deductions)/ tdim,0)
			elif earn.manual == 1:
				d.default_amount = d.amount
			else:
				d.amount = d.default_amount
		if earn.books == 1:
			tot_books += flt(d.amount)
		
		if earn.only_for_deductions != 1:
			gross_pay += flt(d.amount)

	if gross_pay < 0:
		frappe.throw(("Gross Pay Cannot be Less than Zero for Employee: {0}").format(emp.employee_name))
	
	#Calculate Deductions
	for d in doc.deductions:
		if d.salary_component != 'Loan Deduction':
			sal_comp_doc = frappe.get_doc("Salary Component", d.salary_component)
			if sal_comp_doc.depends_on_lwp == 1:
				if sal_comp_doc.round_up == 1:
					d.amount = int(flt(d.default_amount) * flt(doc.payment_days_for_deductions)/tdim)+1
				else:
					d.amount = round(flt(d.default_amount) * flt(doc.payment_days_for_deductions)/tdim,0)
		tot_ded += flt(d.amount)
	
	#Calculate Contributions
	for c in doc.contributions:
		c.amount = round((flt(c.default_amount) * flt(doc.payment_days_for_deductions)/tdim),0)
		tot_cont += c.amount

	doc.gross_pay = gross_pay
	doc.total_deduction = tot_ded
	doc.net_pay = doc.gross_pay - doc.total_deduction
	doc.rounded_cash = myround(flt(doc.net_pay) - flt(doc.actual_bank_salary))
	doc.rounded_total = flt(doc.actual_bank_salary) + flt(doc.rounded_cash)
	doc.net_pay_books = tot_books - doc.total_deduction
		
	company_currency = erpnext.get_company_currency(doc.company)
	doc.total_in_words = money_in_words(doc.rounded_total, company_currency)
	doc.total_ctc = doc.gross_pay + tot_cont
	
def get_leaves(doc, start_date, end_date, emp):
	#Find out the number of leaves applied by the employee only working days
	lwp = 0 #Leaves without pay
	plw = 0 #paid leaves
	diff = (end_date - start_date).days + 1
	for day in range(0, diff):
		date = start_date + datetime.timedelta(days=day)
		auth_leaves = frappe.db.sql("""SELECT la.name FROM `tabLeave Application` la
			WHERE la.status = 'Approved' AND la.docstatus = 1 AND la.employee = '%s'
			AND la.from_date <= '%s' AND la.to_date >= '%s'""" % (doc.employee, date, date), as_list=1)
		if auth_leaves:
			auth_leaves = auth_leaves[0][0]
			lap = frappe.get_doc("Leave Application", auth_leaves)
			ltype = frappe.get_doc("Leave Type", lap.leave_type)
			hol = get_holidays(doc, date, date, emp)
			if hol:
				pass
			else:
				if ltype.is_lwp == 1:
					lwp += 1
				else:
					plw += 1
	lwp = flt(lwp)
	plw = flt(plw)
	return lwp,plw
	
def get_holidays(doc, start_date, end_date,emp):
	if emp.relieving_date is None:
		relieving_date = datetime.date(2099, 12, 31)
	else:
		relieving_date = emp.relieving_date
	
	if emp.date_of_joining > start_date:
		start_date = emp.date_of_joining
	
	if relieving_date < end_date:
		end_date = relieving_date
	
	holiday_list = get_holiday_list_for_employee(doc.employee)
	holidays = frappe.db.sql("""SELECT count(name) FROM `tabHoliday` WHERE parent = '%s' AND 
		holiday_date >= '%s' AND holiday_date <= '%s'""" %(holiday_list, \
			start_date, end_date), as_list=1)
	
	holidays = flt(holidays[0][0]) #no of holidays in a month from the holiday list
	return holidays

def get_total_days(doc, emp, msd, med):
	tdim = (med - msd).days + 1 #total days
	if emp.relieving_date is None:
		relieving_date = datetime.date(2099, 12, 31)
	else:
		relieving_date = emp.relieving_date

	if emp.date_of_joining >= msd:
		twd = (med - emp.date_of_joining).days + 1 #Joining DATE IS THE First WORKING DAY
	elif relieving_date <= med:
		twd = (emp.relieving_date - msd).days + 1 #RELIEVING DATE IS THE LAST WORKING DAY
	else:
		twd = tdim #total days in a month
	doc.working_days = twd
	return tdim, twd

def get_expense_claim(doc, med):
	#Get total Expense Claims Due for an Employee
	query = """SELECT ec.name, ec.employee, ec.total_sanctioned_amount, ec.total_amount_reimbursed
		FROM `tabExpense Claim` ec
		WHERE ec.docstatus = 1 AND ec.approval_status = 'Approved' AND
			ec.total_amount_reimbursed < ec.total_sanctioned_amount AND
			ec.posting_date <= '%s' AND ec.pay_with_salary = 1 AND
			ec.employee = '%s'""" %(med, doc.employee)
	
	
	ec_list = frappe.db.sql(query, as_list=1)
	for i in ec_list:
		existing_ec = []
		for e in doc.earnings:
			existing_ec.append(e.expense_claim)
		
		if i[0] not in existing_ec:
			#Add earning claim for each EC separately:
			doc.append("earnings", {
				"idx": len(doc.earnings)+1, "depends_on_lwp": 0, "default_amount": (i[2]-i[3]), \
				"expense_claim": i[0], "salary_component": "Expense Claim", "amount": (i[2]- i[3])
			})

def get_loan_deduction(doc, msd, med):
	existing_loan = []
	for d in doc.deductions:
		existing_loan.append(d.employee_loan)
	#get total loan due for employee
	query = """SELECT el.name, eld.name, eld.emi, el.deduction_type, eld.loan_amount
		FROM 
			`tabEmployee Advance` el, `tabEmployee Loan Detail` eld
		WHERE
			eld.parent = el.name AND
			el.docstatus = 1 AND el.posting_date <= '%s' AND
			eld.employee = '%s'""" %(med, doc.employee)
		
	loan_list = frappe.db.sql(query, as_list=1)
	for i in loan_list:
		emi = i[2]
		total_loan = i[4]
		if i[0] not in existing_loan:
			#Check if the loan has already been deducted
			query = """SELECT SUM(ssd.amount) 
				FROM `tabSalary Detail` ssd, `tabSalary Slip` ss
				WHERE ss.docstatus = 1 AND
					ssd.parent = ss.name AND
					ssd.employee_loan = '%s' and ss.employee = '%s'""" %(i[0], doc.employee)
			deducted_amount = frappe.db.sql(query, as_list=1)

			if flt(total_loan) > flt(deducted_amount[0][0]):
				#Add deduction for each loan separately
				#Check if EMI is less than balance
				balance = flt(total_loan) - flt(deducted_amount[0][0])
				if balance > emi:
					doc.append("deductions", {
						"idx": len(doc.deductions)+1, "depends_on_lwp": 0, "default_amount": balance, \
						"employee_loan": i[0], "salary_component": i[3], "amount": emi
					})
				else:
					doc.append("deductions", {
						"idx": len(doc.deductions)+1, "d_depends_on_lwp": 0, "default_amount": balance, \
						"employee_loan": i[0], "salary_component": i[3], "amount": balance
					})
	for d in doc.deductions:
		if d.employee_loan:
			total_given = frappe.db.sql("""SELECT eld.loan_amount 
				FROM `tabEmployee Advance` el, `tabEmployee Loan Detail` eld
				WHERE eld.parent = el.name AND eld.employee = '%s' 
				AND el.name = '%s'"""%(doc.employee, d.employee_loan), as_list=1)
			
			deducted = frappe.db.sql("""SELECT SUM(ssd.amount) 
				FROM `tabSalary Detail` ssd, `tabSalary Slip` ss
				WHERE ss.docstatus = 1 AND ssd.parent = ss.name 
				AND ssd.employee_loan = '%s' and ss.employee = '%s'"""%(d.employee_loan, doc.employee), as_list=1)
			balance = flt(total_given[0][0]) - flt(deducted[0][0])
			if balance < d.amount:
				frappe.throw(("Max deduction allowed {0} for Loan Deduction {1} \
				check row # {2} in Deduction Table").format(balance, d.employee_loan, d.idx))

def get_month_dates(doc):
	date_details = get_start_end_dates(doc.payroll_frequency, doc.start_date or doc.posting_date)
	doc.end_date = date_details.end_date
	med = date_details.end_date
	doc.start_date = date_details.start_date
	msd = date_details.start_date
	return msd, med

def get_edc(doc):
	#Earning Table should be replaced if there is any change in the Earning Composition except manual
	#Change can be of 3 types in the earning table
	#1. If a user removes a type of earning
	#2. If a user adds a type of earning
	#3. If a user deletes and adds a type of another earning
	#Function to get the Earnings, Deductions and Contributions (E,D,C)
	doj = frappe.get_value("Employee", doc.employee, "date_of_joining")
	if doj > datetime.datetime.strptime(doc.start_date, '%Y-%m-%d').date():
		date_for_sstra = doj
	else:
		date_for_sstra = doc.start_date

	appl_sstr = frappe.db.sql("""SELECT sstra.salary_structure FROM `tabSalary Structure Assignment` sstra
		WHERE sstra.employee = '%s' 
		AND sstra.from_date <= '%s'
		ORDER BY sstra.from_date DESC LIMIT 1"""%(doc.employee, date_for_sstra), as_list=1)
	if appl_sstr:
		doc.salary_structure = appl_sstr[0][0]
	else:
		frappe.throw("No Salary Structure Found for Employee {}".format(doc.employee))
	sstr = frappe.get_doc("Salary Structure", doc.salary_structure)
	existing_ded = []
	manual_earn = []
	
	earn_dict = {}
	for comp in doc.earnings:
		earn_doc = frappe.get_doc("Salary Component", comp.salary_component)
		if earn_doc.manual == 1:
			earn_dict['salary_component'] = comp.salary_component
			earn_dict['idx'] = comp.idx
			earn_dict['default_amount'] = comp.amount
			earn_dict['amount'] = comp.amount
			manual_earn.append(earn_dict.copy())
	#Only Loan Deduction is Not Overwritten so that Loan Deduction can be Changed Later by user
	dict = {}
	for comp in doc.deductions:
		if comp.salary_component == 'Loan Deduction':
			dict['salary_component'] = comp.salary_component
			dict['idx'] = comp.idx
			dict['default_amount'] = comp.default_amount
			dict['amount'] = comp.amount
			dict['employee_loan'] = comp.employee_loan
			existing_ded.append(dict.copy())
			
	table_list = ["earnings", "deductions", "contributions"]
	doc.earnings = []
	doc.deductions = []
	doc.contributions = []
	get_from_sal_struct(doc, sstr, table_list)
	
	#Add Changed Manual Earning Amount to the Table
	if manual_earn:
		for i in range(len(manual_earn)):
			for comp in doc.earnings:
				if comp.salary_component == earn_dict['salary_component']:
					comp.default_amount = manual_earn[i]['amount']
					comp.amount = manual_earn[i]['amount']
					
	#Add changed loan amount to the table
	if existing_ded:
		for i in range(len(existing_ded)):
			doc.append("deductions", {
				"salary_component": dict['salary_component'],
				"default_amount": existing_ded[i]['default_amount'],
				"amount": existing_ded[i]['amount'],
				"idx": existing_ded[i]['idx'],
				"employee_loan": existing_ded[i]['employee_loan']
			})

def get_from_sal_struct(doc, salary_structure_doc, table_list):
	data = SalarySlip.get_data_for_eval(doc)

	for table_name in table_list:
		for comp in salary_structure_doc.get(table_name):
			amount = SalarySlip.eval_condition_and_formula(doc, comp, data)
			doc.append(table_name, {
				"salary_component": comp.salary_component,
				"default_amount": amount,
				"amount": amount,
				"idx": comp.idx,
				"depends_on_lwp": comp.depends_on_lwp
			})
			
def myround(x, base=5):
    return int(base * round(float(x)/base))
