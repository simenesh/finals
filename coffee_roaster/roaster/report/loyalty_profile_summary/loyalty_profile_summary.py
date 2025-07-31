import frappe

def execute(filters=None):
    columns = [
        {"label": "Label", "fieldname": "label", "fieldtype": "Data"},
        {"label": "Value", "fieldname": "value", "fieldtype": "Float"}
    ]
    data = frappe.db.sql("""
        SELECT
            COALESCE(program_name, 'Unassigned') AS label,
            AVG(loyalty_score) AS value
        FROM `tabLoyalty Profile`
        GROUP BY program_name
        ORDER BY value DESC
    """, as_dict=True)
    return columns, data

