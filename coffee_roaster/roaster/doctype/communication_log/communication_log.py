import frappe
from frappe.model.document import Document

class CommunicationLog(Document):
    def before_save(self):
        if not self.communication_date:
            self.communication_date = frappe.utils.today()
