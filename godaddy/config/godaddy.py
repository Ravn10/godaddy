from frappe import _

def get_data():
	return [{
		"label": _("Setting"),
				"items":[
                    {
                        "type":"doctype",
                        "name":"Godaddy Setting",
                        "description":_("Godaddy Setting")
                        }
                ]
    },
    {
		"label": _("Documents"),
				"items":[
                    {
                        "type":"doctype",
                        "name":"Godaddy A Records",
                        "description":_("Godaddy A Records")
                        },
                    {
                    "type":"doctype",
                    "name":"Godaddy Subdomains",
                    "description":_("Godaddy Subdomains")
                    }
                ]
    },
    ]