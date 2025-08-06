import frappe
from frappe.model.document import Document

class CombinedCoffeeReport(Document):
    @frappe.whitelist()
    def get_combined_data(self, roast_batch):
        # Fetch Extrinsic Assessment
        extrinsic = frappe.get_all(
            "Extrinsic Assessment",
            filters={"roast_batch": roast_batch},
            fields=["*"]
        )
        
        # Fetch Descriptive Assessment
        descriptive = frappe.get_all(
            "Descriptive Assessment",
            filters={"roast_batch": roast_batch},
            fields=["*"]
        )
        
        if not extrinsic or not descriptive:
            frappe.throw("No assessments found for this Roast Batch!")
        
        return {
            "extrinsic": extrinsic[0],  # Take the first match
            "descriptive": descriptive[0]
        }
