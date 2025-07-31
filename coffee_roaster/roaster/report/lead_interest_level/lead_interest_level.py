import frappe

def execute(filters=None):
    columns = [
        {"label": "Label", "fieldname": "label", "fieldtype": "Data"},
        {"label": "Value", "fieldname": "value", "fieldtype": "Int"}
    ]
    data = frappe.db.sql("""
        SELECT
            COALESCE(interest_level, 'Unknown') AS label,
            COUNT(name) AS value
        FROM `tabLead`
        GROUP BY interest_level
        ORDER BY value DESC
    """, as_dict=True)
    return columns, data

