# -*- coding: utf-8 -*-
import frappe
from frappe import _
from frappe.utils import flt

# ───────────────────────────────────────────────────────────────
def execute(filters=None):
    filters = filters or {}
    return _columns(), _rows(filters)

# ───────────────────────────────────────────────────────────────
def key_field(doctype):
    return "sample_id" if frappe.get_meta(doctype).get_field("sample_id") else "name"

# NEW ▶ find the first text-like “note” field
def find_note_field(doctype, candidates=None):
    candidates = candidates or ("descriptive_notes", "notes",
                                "overall_comments", "general_notes",
                                "description", "comments")
    meta = frappe.get_meta(doctype)
    for c in candidates:
        if meta.get_field(c):
            return c
    return None

def map_by_sample(doctype, extra_fields, filters=None):
    kf = key_field(doctype)
    query_fields = [f"{kf} as sample_id"] + extra_fields
    filt = (filters or {}).copy()
    if kf != "sample_id" and "sample_id" in filt:
        filt[kf] = filt.pop("sample_id")
    rows = frappe.get_all(doctype, filters=filt, fields=query_fields)
    out = {}
    for r in rows:
        out.setdefault(r.sample_id or "", []).append(r)
    return out

def ecx_grade(defects, cup_score):
    defects, cup_score = defects or 0, cup_score or 0
    if defects <= 3 and cup_score >= 85:  return "1 (Specialty)"
    if defects <= 12 and cup_score >= 80: return "2"
    if defects <= 25 and cup_score >= 75: return "3"
    if defects <= 45 and cup_score >= 70: return "4"
    if defects <= 100 and cup_score >= 65: return "5"
    return "6–9 (Undergrade)"

# ───────────────────────────────────────────────────────────────
def _rows(filters):
    affective   = map_by_sample(
        "Affective Assessment",
        ["overall_comments as affective_notes"], filters
    )

    # NEW ▶ dynamically pick the correct note column for Descriptive
    desc_note = find_note_field("Descriptive Assessment") or "description"
    descriptive = map_by_sample(
        "Descriptive Assessment",
        [f"{desc_note} as descriptive_notes"], filters
    )

    physical    = map_by_sample(
        "Physical Assessment",
        ["total_defects", "cup_score"], filters
    )
    extrinsic   = map_by_sample(
        "Extrinsic Assessment",
        ["assessment_date", "assessor_name", "general_notes"], filters
    )

    sample_ids = set()
    for dt in ("Affective Assessment", "Descriptive Assessment",
               "Physical Assessment", "Extrinsic Assessment"):
        sample_ids.update(
            frappe.get_all(dt, filters=filters, pluck=key_field(dt))
        )

    data = []
    for sid in sorted(sample_ids):
        aff  = (affective  .get(sid) or [{}])[0]
        desc = (descriptive.get(sid) or [{}])[0]
        phy  = (physical   .get(sid) or [{}])[0]
        ex   = (extrinsic  .get(sid) or [{}])[0]

        data.append({
            "Sample ID":         sid,
            "Date":              ex.get("assessment_date", ""),
            "Assessor":          ex.get("assessor_name", ""),
            "Affective Notes":   aff.get("affective_notes", ""),
            "Descriptive Notes": desc.get("descriptive_notes", ""),
            "Defects":           phy.get("total_defects", 0),
            "Cup Score":         flt(phy.get("cup_score", 0), 2),
            "ECX Grade":         ecx_grade(phy.get("total_defects"),
                                           phy.get("cup_score")) if phy else "",
            "Extrinsic Notes":   ex.get("general_notes", ""),
        })
    return data

# ───────────────────────────────────────────────────────────────
def _columns():
    return [
        _("Sample ID")         + ":Data:120",
        _("Date")              + ":Date:100",
        _("Assessor")          + ":Data:120",
        _("Affective Notes")   + ":Text:200",
        _("Descriptive Notes") + ":Text:200",
        _("Defects")           + ":Int:80",
        _("Cup Score")         + ":Float:80",
        _("ECX Grade")         + ":Data:100",
        _("Extrinsic Notes")   + ":Text:200",
    ]
