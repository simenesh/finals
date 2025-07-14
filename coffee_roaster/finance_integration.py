# File: apps/coffee_roaster/coffee_roaster/finance_integration.py
import frappe
from datetime import date


def flt(value, precision=None):
    """
    Convert a value to float. If precision is provided, round to that precision.
    """
    try:
        val = float(value)
        return round(val, precision) if precision is not None else val
    except (TypeError, ValueError):
        return 0.0


def nowdate():
    """
    Return today's date as an ISO string.
    """
    return date.today().isoformat()


def post_batch_cost_gl_entry(doc, method):
    """
    On submission of a Batch Cost, create a Journal Entry posting the batch's costs.
    Prevents duplicates by checking Journal Entry Accounts against this voucher.
    """
    if doc.docstatus != 1:
        return
    # Prevent duplicate JE
    exists = frappe.db.exists("Journal Entry Account", {
        "against_voucher_type": "Batch Cost", 
        "against_voucher": doc.name
    })
    if exists:
        return

    # Aggregate costs
    raw_total = flt(sum([row.amount for row in doc.raw_bean_costs]))
    overhead_total = flt(sum([row.amount for row in doc.overheads]))
    packaging_total = flt(sum([row.amount for row in doc.packaging_costs]))
    total_cost = raw_total + overhead_total + packaging_total

    # Create Journal Entry
    je = frappe.new_doc("Journal Entry")
    je.voucher_type = "Journal Entry"
    je.posting_date = nowdate()
    je.user_remark = f"Batch Cost for {doc.name}"

    # Debit cost accounts (replace placeholder fields with your actual fields)
    je.append("accounts", {
        "account": doc.raw_bean_expense_account,    # e.g., 'Cost of Goods Sold - COF', customize
        "debit": raw_total,
        "credit": 0,
        "against_voucher_type": "Batch Cost",
        "against_voucher": doc.name
    })
    je.append("accounts", {
        "account": doc.overhead_expense_account,    # e.g., 'Overheads - COF'
        "debit": overhead_total,
        "credit": 0,
        "against_voucher_type": "Batch Cost",
        "against_voucher": doc.name
    })
    je.append("accounts", {
        "account": doc.packaging_expense_account,  # e.g., 'Packaging Costs - COF'
        "debit": packaging_total,
        "credit": 0,
        "against_voucher_type": "Batch Cost",
        "against_voucher": doc.name
    })
    # Credit inventory or finished goods
    je.append("accounts", {
        "account": doc.inventory_account,          # e.g., 'Finished Goods - COF'
        "debit": 0,
        "credit": total_cost,
        "against_voucher_type": "Batch Cost",
        "against_voucher": doc.name
    })

    je.insert(ignore_permissions=True)
    je.submit()


def apply_vat_on_invoice(doc, method):
    """
    On Sales Invoice validate, ensure VAT line is added or updated based on Roaster Settings.
    """
    settings = frappe.get_single("Roaster Settings")
    vat_rate = flt(settings.vat_rate)
    vat_account = settings.vat_account
    if not vat_rate or not vat_account:
        return

    # Look for existing VAT line
    found = False
    for tax in doc.taxes:
        if tax.account_head == vat_account:
            tax.rate = vat_rate
            found = True
            break

    # Append VAT line if missing
    if not found:
        doc.append("taxes", {
            "charge_type": "On Net Total",
            "account_head": vat_account,
            "rate": vat_rate,
            "description": "VAT"
        })


def execute_sku_profit(filters=None):
    """
    Script Report: returns cost, revenue, profit, margin per Roasted Item.
    """
    columns = [
        {"label": "Item", "fieldname": "item", "fieldtype": "Link", "options": "Item", "width": 200},
        {"label": "Total Cost", "fieldname": "total_cost", "fieldtype": "Currency"},
        {"label": "Total Sales", "fieldname": "total_sales", "fieldtype": "Currency"},
        {"label": "Profit", "fieldname": "profit", "fieldtype": "Currency"},
        {"label": "Margin %", "fieldname": "margin_pct", "fieldtype": "Percent"}
    ]

    # Aggregate from Batch Cost and Sales Invoice
    data = []
    items = frappe.get_all("Item", filters={"item_group": "Roasted Coffee"}, pluck="name")
    for item in items:
        # Sum costs
        cost = flt(frappe.db.get_value("Batch Cost", {"item_code": item, "docstatus": 1}, "sum(total_cost)"))
        # Sum sales
        sales = flt(frappe.db.sql(
            """
            SELECT SUM(`tabSales Invoice Item`.amount) 
            FROM `tabSales Invoice Item`
            JOIN `tabSales Invoice` ON `tabSales Invoice`.name = `tabSales Invoice Item`.parent
            WHERE `tabSales Invoice Item`.item_code=%s AND `tabSales Invoice`.docstatus=1
            """, (item,))[0][0]
        )
        profit = sales - cost
        margin = (profit / sales * 100) if sales else 0
        data.append({
            "item": item,
            "total_cost": cost,
            "total_sales": sales,
            "profit": profit,
            "margin_pct": margin
        })

    # Optional: chart omitted for simplicity
    return columns, data
