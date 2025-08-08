frappe.ui.form.on('Route Plan', {
    refresh: function(frm) {
        frm.set_df_property("total_outlets", "read_only", 1);
    },
    gov: calculate_total,
    ngo: calculate_total,
    emb: calculate_total,
    corp: calculate_total,
    edu: calculate_total,
    smkt: calculate_total,
    expo: calculate_total,
    retail: calculate_total,
    dist: calculate_total,
    caf: calculate_total,
    hotel: calculate_total,
    rest: calculate_total
});

function calculate_total(frm) {
    let total = 0;
    const outlet_fields = ['gov', 'ngo', 'emb', 'corp', 'edu', 'smkt', 'expo', 'retail', 'dist', 'caf', 'hotel', 'rest'];
    outlet_fields.forEach(field => {
        total += parseInt(frm.doc[field] || 0);
    });
    frm.set_value("total_outlets", total);
}
