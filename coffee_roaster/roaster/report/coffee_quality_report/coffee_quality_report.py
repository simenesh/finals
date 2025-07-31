# File: coffee_quality_report.py
import frappe
from frappe.utils import flt

def execute(filters=None):
    columns = get_columns()
    data = get_data()
    return columns, data

def get_columns():
    return [
        {"label": "Batch", "fieldname": "roast_batch", "fieldtype": "Link", "options": "Roast Batch", "width": 120},
        {"label": "Sample", "fieldname": "sample_id", "fieldtype": "Data", "width": 100},
        {"label": "Physical Score", "fieldname": "physical_score", "fieldtype": "Float", "width": 110},
        {"label": "Descriptive Score", "fieldname": "descriptive_score", "fieldtype": "Float", "width": 130},
        {"label": "Extrinsic Score", "fieldname": "extrinsic_score", "fieldtype": "Float", "width": 120},
        {"label": "Affective Score", "fieldname": "affective_score", "fieldtype": "Float", "width": 120},
        {"label": "Average", "fieldname": "average_score", "fieldtype": "Float", "width": 100},
    ]

def get_data():
    assessments = frappe.db.sql("""
        SELECT 
            pa.roast_batch,
            pa.sample_id,
            pa.total_score AS physical_score,
            FROM `tabPhysical Assessment` pa
           """, as_dict=True)

    for row in assessments:
        scores = [flt(row.get(k)) for k in ("physical_score", "descriptive_score", "extrinsic_score", "affective_score") if row.get(k) is not None]
        row["average_score"] = round(sum(scores) / len(scores), 2) if scores else None

    return assessments

