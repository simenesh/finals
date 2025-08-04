# Script Report: Combined Assessment Report
# frappe and _ are available; avoid external imports

def execute(filters=None):
    # 1) Require roast_batch filter
    if not filters or not filters.get("roast_batch"):
        frappe.throw(_("Please select a Roast Batch"))
    roast_batch = filters["roast_batch"]

    # 2) Define field mappings based on the provided DocTypes for maintainability.
    DESCRIPTIVE_FIELDS = [
        "sample_no", "roast_date", "roast_time", "roast_level",
        "fragrance_intensity", "aroma_intensity", "acidity_intensity",
        "sweetness_intensity", "mouthfeel_intensity", "acidity_notes", "sweetness_notes"
    ]

    EXTRINSIC_FIELDS = [
        "assessor_name", "assessment_date", "purpose", "country", "region",
        "farm_or_coop_name", "producer_name", "species", "variety", "harvest_date_year",
        "other_farming_attribute", "farming_notes", "processor_name", "process_type",
        "processing_notes", "trading_size_grade", "trading_ico_number",
        "trading_other_grade", "trading_other_attribute", "trading_notes",
        "certifications", "certification_notes", "general_notes"
    ]

    # Checkbox flag groups from the 'Descriptive Assessment' DocType
    ATTRIBUTE_FLAGS = {
        "fragrance": [
            "floral", "fruity", "berry", "dried_fruit", "citrus_fruit", "sweet",
            "brown_sugar", "vanilla", "roasted", "cereal", "nutty_cocoa", "cocoa",
            "burnt", "tobacco", "spice", "sour", "fermented", "green_veg",
            "musty_earthy", "woody", "chemical", "other"
        ],
        "aroma": [
            "floral", "fruity", "berry", "dried_fruit", "citrus_fruit", "sweet",
            "brown_sugar", "vanilla", "roasted", "cereal", "nutty_cocoa", "cocoa",
            "burnt", "tobacco", "spice", "sour", "fermented", "green_veg",
            "musty_earthy", "woody", "chemical", "other"
        ],
        "mouthfeel": ["rough", "oily", "smooth", "drying", "metallic"]
    }

    # Generate full field names for all checkbox flags
    flag_fields = [f"{group}_{flag}" for group, flags in ATTRIBUTE_FLAGS.items() for flag in flags]

    # 3) Fetch all 'Descriptive Assessment' records for the selected batch
    desc_records = frappe.get_all(
        "Descriptive Assessment",
        fields=DESCRIPTIVE_FIELDS + flag_fields,
        filters={"roast_batch": roast_batch},
        ignore_permissions=True,
        as_list=False
    )

    # 4) Fetch the single latest 'Extrinsic Assessment' record for the selected batch
    ext_entries = frappe.get_all(
        "Extrinsic Assessment",
        fields=EXTRINSIC_FIELDS,
        filters={"roast_batch": roast_batch},
        order_by="assessment_date desc, creation desc", # Get the most recent entry
        limit=1,
        ignore_permissions=True,
        as_list=False
    )
    ext_data = ext_entries[0] if ext_entries else {}

    # 5) Build the report rows by combining the data
    data = []
    if desc_records:
        # If descriptive data exists, create a row for each entry
        for record in desc_records:
            row = {}
            # Add all descriptive and extrinsic data to the row
            row.update({k: record.get(k) for k in DESCRIPTIVE_FIELDS})
            row.update({k: ext_data.get(k) for k in EXTRINSIC_FIELDS})

            # Aggregate checkbox flags into readable, comma-separated strings
            for group, flags in ATTRIBUTE_FLAGS.items():
                row[f"{group}_attributes"] = aggregate_flags(record, group, flags)
            
            data.append(row)
    elif ext_data:
        # If ONLY extrinsic data exists, create a single row for it
        data.append(ext_data)

    # 6) Normalize all data for safe rendering in the report
    normalized_data = [normalize_row(row) for row in data]
    
    # If no data was found after all queries, inform the user and exit gracefully.
    if not normalized_data:
        frappe.msgprint(_("No assessment data found for the selected Roast Batch."))
        return [], []

    # 7) Define all possible columns and then filter out any that are completely empty
    columns = get_column_definitions()
    
    # Determine which columns actually contain data across all rows
    used_columns = {key for row in normalized_data for key, val in row.items() if val not in (None, "", [], 0)}
    # Ensure certain key columns are always shown
    always_include = {"sample_no", "roast_date", "roast_time", "roast_level"}
    
    final_columns = [c for c in columns if c["fieldname"] in used_columns or c["fieldname"] in always_include]

    return final_columns, normalized_data


def aggregate_flags(doc, group_name, flags):
    """Helper function to create a comma-separated string from a list of checkbox fields."""
    labels = [
        _(flag.replace("_", " ").title())
        for flag in flags
        if doc.get(f"{group_name}_{flag}")
    ]
    return ", ".join(labels)


def normalize_row(row):
    """Makes every field in a row safe for the report (no None values or complex types)."""
    out = {}
    for k, v in row.items():
        if v is None:
            out[k] = ""
        elif isinstance(v, (int, float)):
            out[k] = v
        else:
            # Force everything else to a string type for consistency
            out[k] = str(v)
    return out


def get_column_definitions():
    """Returns a list of all possible column dictionaries for the report."""
    return [
        {"label": _(label), "fieldname": fname, "fieldtype": ftype, "width": w}
        for label, fname, ftype, w in [
            ("Sample No.", "sample_no", "Data", 80),
            ("Roast Date", "roast_date", "Date", 90),
            ("Roast Time", "roast_time", "Time", 80),
            ("Roast Level", "roast_level", "Data", 100),
            ("Fragrance Intensity", "fragrance_intensity", "Int", 90),
            ("Fragrance Attributes", "fragrance_attributes", "Data", 200),
            ("Aroma Intensity", "aroma_intensity", "Int", 90),
            ("Aroma Attributes", "aroma_attributes", "Data", 200),
            ("Acidity Intensity", "acidity_intensity", "Int", 90),
            ("Acidity Notes", "acidity_notes", "Data", 200),
            ("Sweetness Intensity", "sweetness_intensity", "Int", 90),
            ("Sweetness Notes", "sweetness_notes", "Data", 200),
            ("Mouthfeel Intensity", "mouthfeel_intensity", "Int", 90),
            ("Mouthfeel Attributes", "mouthfeel_attributes", "Data", 200),
            ("Assessor", "assessor_name", "Data", 120),
            ("Assessment Date", "assessment_date", "Date", 90),
            ("Purpose", "purpose", "Data", 150),
            ("Country", "country", "Data", 120),
            ("Region", "region", "Data", 120),
            ("Farm/Co-op", "farm_or_coop_name", "Data", 150),
            ("Producer", "producer_name", "Data", 150),
            ("Species", "species", "Data", 120),
            ("Variety", "variety", "Data", 120),
            ("Harvest Date/Year", "harvest_date_year", "Data", 120),
            ("Other Farming Attr.", "other_farming_attribute", "Data", 200),
            ("Farming Notes", "farming_notes", "Data", 200),
            ("Processor", "processor_name", "Data", 150),
            ("Process Type", "process_type", "Data", 100),
            ("Processing Notes", "processing_notes", "Data", 200),
            ("Size Grade", "trading_size_grade", "Data", 100),
            ("ICO Number", "trading_ico_number", "Data", 120),
            ("Other Grade", "trading_other_grade", "Data", 120),
            ("Other Trading Attr.", "trading_other_attribute", "Data", 150),
            ("Trading Notes", "trading_notes", "Data", 200),
            ("Certifications", "certifications", "Data", 150),
            ("Certification Notes", "certification_notes", "Data", 200),
            ("Overall Notes", "general_notes", "Data", 200),
        ]
    ]