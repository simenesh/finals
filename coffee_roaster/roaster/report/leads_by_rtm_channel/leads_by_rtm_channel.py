import frappe

def execute(filters=None):
    columns = [
        {"label": "Label", "fieldname": "label", "fieldtype": "Data"},
        {"label": "Value", "fieldname": "value", "fieldtype": "Int"}
    ]
    data = frappe.db.sql("""
        SELECT
            COALESCE(preferred_rtm_channel, 'Unknown') AS label,
            COUNT(name) AS value
        FROM `tabLead`
        GROUP BY preferred_rtm_channel
        ORDER BY value DESC
    """, as_dict=True)
    return columns, data

