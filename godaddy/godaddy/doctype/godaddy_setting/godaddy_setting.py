# -*- coding: utf-8 -*-
# Copyright (c) 2020, Firsterp and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe import _, msgprint
from frappe.model.document import Document
from godaddypy import Client, Account

class GodaddySetting(Document):
	def validate(self):
		# frappe.msgprint(self.get_a_records())
		domains= self.get_a_records()
		my_acct =  Account(api_key=self.key, api_secret=self.secret)
		for domain in domains:
			self.create_domain_records(domain,my_acct)
		self.create_subdomain(self.domain,my_acct)

	def get_a_records(self):
		my_acct = Account(api_key=self.key, api_secret=self.secret)
		return Client(my_acct).get_domains()
	
	def create_domain_records(self,domain,my_acct):
		client = Client(my_acct)
		if frappe.db.exists("Godaddy A Records",domain):
			try:
				data = client.get_records(domain, record_type='A')
				# frappe.msgprint(json.dumps(client.get_records(domain, record_type='A')))
				domain_doc = frappe.get_doc("Godaddy A Records",domain)
				domain_doc.records = str(data)
				domain_doc.save()
				frappe.msgprint(_("""{0} updated""").format(domain))
			except:
				frappe.msgprint(_("""{0} not updated""").format(domain))
		else:
			a_record = frappe.new_doc("Godaddy A Records")
			a_record.domain = domain
			try:
				a_record.records = str(client.get_records(domain, record_type='A'))
			except:
				frappe.msgprint(_("""{0} not created""").format(domain))
			a_record.insert()
			frappe.msgprint(_("""{0} created""").format(a_record.name))

	def create_subdomain(self,domain,my_acct):
		client = Client(my_acct)
		records = client.get_records(domain, record_type='A')
		for record in records:
			if not record['name'] == '@':
				if not frappe.db.exists("Godaddy Subdomains",record['name']):
					sub_domain_doc = frappe.new_doc("Godaddy Subdomains")
					sub_domain_doc.subdomain = record['name']
					sub_domain_doc.domain = domain
					sub_domain_doc.insert()
					frappe.msgprint(_("""{0} created""").format(sub_domain_doc.name))

@frappe.whitelist()
def get_godaddy_essentials():
	secret = frappe.db.get_single_value("Godaddy Setting","secret")
	key = frappe.db.get_single_value("Godaddy Setting","key")
	domain = frappe.db.get_single_value("Godaddy Setting","domain")
	ip  = frappe.db.get_single_value("Godaddy Setting","ip_address")
	my_acct = Account(api_key=key, api_secret=secret)
	client = Client(my_acct)
	return {
		"secret":secret,
		"key":key,
		"domain":domain,
		"ip":ip,
		"my_acct":my_acct,
		"client":client
	}

@frappe.whitelist()
def add_a_record(subdomain):
	godaddy = get_godaddy_essentials()
	if not godaddy['domain']:
		frappe.throw(_("Please set domain in Godaddy Setting"))
	if not godaddy['ip']:
		frappe.throw(_("Please set ip_address in Godaddy Setting"))
	# {'data':'1.2.3.4','name':'test','ttl':3600, 'type':'A'}
	record = {
		'data':godaddy['ip'],
		'name':subdomain,
		'ttl':3600,
		'type':'A'
	}
	try:
		godaddy['client'].add_record(godaddy['domain'],record)
	except Exception as e :
		return e

@frappe.whitelist()
def delete_a_record(subdomain):
	godaddy = get_godaddy_essentials()
	if not godaddy['domain']:
		frappe.throw(_("Please set domain in Godaddy Setting"))
	if not godaddy['ip']:
		frappe.throw(_("Please set ip_address in Godaddy Setting"))
	try:
		godaddy['client'].delete_records(godaddy['domain'],name=subdomain)
	except Exception as e :
		return e