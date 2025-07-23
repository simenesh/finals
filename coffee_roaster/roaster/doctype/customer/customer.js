frappe.ui.form.on('Customer', {
    refresh: function(frm) {
        // 1. Auto-fill company if empty
        if (frm.is_new() && !frm.doc.company) {
            const default_company = frappe.defaults.get_user_default("Company");
            if (default_company) {
                frm.set_value("company", default_company);
            }
        }

        // 2. Add custom "Create Opportunity" button
        if (!frm.is_new()) {
            frm.add_custom_button('Create Opportunity', function() {
                frappe.new_doc('Opportunity', {
                    customer: frm.doc.name,
                    party_name: frm.doc.full_name,
                    company: frm.doc.company
                });
            }, __('Create'));
        }

        // 3. Make status read-only for non-System Managers
        if (!frappe.user.has_role("System Manager")) {
            frm.set_df_property("status", "read_only", 1);
        } else {
            frm.set_df_property("status", "read_only", 0);
        }
    },

    validate: function(frm) {
        // 4. Ensure required fields are filled
        if (!frm.doc.full_name || !frm.doc.customer_type) {
            frappe.throw(__('Full Name and Customer Type are required'));
        }

        // 5. Optional: Validate email format
        if (frm.doc.email && !frappe.utils.validate_type(frm.doc.email, "email")) {
            frappe.throw(__('Please enter a valid email address'));
        }
    }
});
