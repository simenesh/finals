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
    raw_total       = flt(sum([row.amount for row in doc.raw_bean_costs]))
    overhead_total  = flt(sum([row.amount for row in doc.overheads]))
    packaging_total = flt(sum([row.amount for row in doc.packaging_costs]))
    total_cost      = raw_total + overhead_total + packaging_total

    # Create Journal Entry
    je = frappe.new_doc("Journal Entry")
    je.voucher_type  = "Journal Entry"
    je.posting_date  = nowdate()
    je.user_remark   = f"Batch Cost for {doc.name}"

    # Debit cost accounts
    je.append("accounts", {
        "account":                  doc.raw_bean_expense_account,
        "debit":                    raw_total,
        "credit":                   0,
        "against_voucher_type":     "Batch Cost",
        "against_voucher":          doc.name
    })
    je.append("accounts", {
        "account":                  doc.overhead_expense_account,
        "debit":                    overhead_total,
        "credit":                   0,
        "against_voucher_type":     "Batch Cost",
        "against_voucher":          doc.name
    })
    je.append("accounts", {
        "account":                  doc.packaging_expense_account,
        "debit":                    packaging_total,
        "credit":                   0,
        "against_voucher_type":     "Batch Cost",
        "against_voucher":          doc.name
    })

    # Credit inventory / finished goods
    je.append("accounts", {
        "account":                  doc.inventory_account,
        "debit":                    0,
        "credit":                   total_cost,
        "against_voucher_type":     "Batch Cost",
        "against_voucher":          doc.name
    })

    je.insert(ignore_permissions=True)
    je.submit()
def apply_vat_on_invoice(doc, method):
    """
    On Sales Invoice validate, add or update a VAT line based on Roaster Settings.
    """
    # Only for submitted Sales Invoices
    if doc.doctype != "Sales Invoice" or doc.docstatus != 1:
        return

    settings    = frappe.get_single("Roaster Settings")
    # ← safe-get so missing fields return defaults
    vat_rate    = flt(settings.get("vat_rate", 0))
    vat_account = settings.get("vat_account")

    if not vat_rate or not vat_account:
        return

    # Compute VAT amount on Net Total
    tax_amount = flt(doc.net_total) * vat_rate / 100.0

    # Look for existing VAT line
    for tax in doc.taxes:
        if tax.account_head == vat_account:
            tax.rate       = vat_rate
            tax.tax_amount = tax_amount
            tax.description = tax.description or "VAT"
            break
    else:
        # Append VAT line if not found
        doc.append("taxes", {
            "charge_type":  "On Net Total",
            "account_head": vat_account,
            "rate":         vat_rate,
            "tax_amount":   tax_amount,
            "description":  "VAT"
        })

