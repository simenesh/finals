# Script Report ‒ Roast Batch Profitability
# ----------------------------------------
# Safe against missing filters (NoneType) and blank date range.

import frappe
from frappe.utils import flt

def execute(filters=None):
    # Always work with a dict-like object, even when report runs with no filters
    filters = frappe._dict(filters or {})

    # Extract filter values safely
    company = filters.get("company")
    date_from, date_to = (filters.get("roast_date_range") or [None, None])

    columns = [
        {"label": "Batch",       "fieldname": "batch",      "fieldtype": "Link",    "options": "Roast Batch", "width": 140},
        {"label": "Date",        "fieldname": "date",       "fieldtype": "Date",                               "width": 90},
        {"label": "Cost / Kg",   "fieldname": "cost_kg",    "fieldtype": "Currency",                           "width": 110},
        {"label": "Sell / Kg",   "fieldname": "sell_kg",    "fieldtype": "Currency",                           "width": 110},
        {"label": "Margin / Kg", "fieldname": "margin",     "fieldtype": "Currency",                           "width": 110},
        {"label": "Margin %",    "fieldname": "margin_pct", "fieldtype": "Percent",                            "width": 90},
    ]

    data = frappe.db.sql(
        """
        SELECT
            rb.name                          AS batch,
            rb.posting_date                  AS date,
            bc.cost_per_kg                   AS cost_kg,
            sii.base_rate                    AS sell_kg,
            (sii.base_rate - bc.cost_per_kg) AS margin,
            ROUND(((sii.base_rate - bc.cost_per_kg) / bc.cost_per_kg) * 100, 2) AS margin_pct
        FROM `tabBatch Cost` bc
        JOIN `tabRoast Batch`        rb  ON bc.batch_no = rb.name
        JOIN `tabSales Invoice Item` sii ON sii.batch_no = rb.name
        WHERE (%(date_from)s IS NULL OR rb.posting_date >= %(date_from)s)
          AND (%(date_to)s   IS NULL OR rb.posting_date <= %(date_to)s)
          AND (%(company)s   IS NULL OR sii.company       = %(company)s)
        ORDER BY rb.posting_date DESC
        """,
        {
            "date_from": date_from,
            "date_to":   date_to,
            "company":   company,
        },
        as_dict=True,
    )

    return columns, data