/* eslint-disable */

frappe.query_reports["Roast Batch Profitability"] = {
    filters: [
        {
            fieldname: "company",
            label: __("Company"),
            fieldtype: "Link",
            options: "Company",
            default: frappe.defaults.get_user_default("Company")
        },
        {
            fieldname: "roast_date_range",
            label: __("Roast Date Range"),
            fieldtype: "DateRange",
            // TODAY ➜ TODAY  (must be a 2-item array)
            default: [
                frappe.datetime.get_today(),   // from-date
                frappe.datetime.get_today()    // to-date
            ]
        }
    ]
};
