frappe.ui.form.on('Combined Coffee Report', {
    refresh: function(frm) {
        // Add a button to fetch and display data
        frm.add_custom_button(__('Generate Report'), function() {
            if (frm.doc.roast_batch) {
                frm.call('get_combined_data', { roast_batch: frm.doc.roast_batch })
                    .then(r => {
                        if (r.message) {
                            frm.events.display_report(frm, r.message);
                        }
                    });
            } else {
                frappe.msgprint("Please select a Roast Batch first.");
            }
        });
    },
    
    display_report: function(frm, data) {
        // Create HTML to display the combined data
        const extrinsic = data.extrinsic;
        const descriptive = data.descriptive;
        
        let html = `
            <div class="row">
                <div class="col-md-6">
                    <h4>Extrinsic Data (Origin/Processing)</h4>
                    <p><strong>Country:</strong> ${extrinsic.country}</p>
                    <p><strong>Farm:</strong> ${extrinsic.farm_or_coop_name}</p>
                    <p><strong>Process:</strong> ${extrinsic.process_type}</p>
                </div>
                <div class="col-md-6">
                    <h4>Descriptive Data (Sensory)</h4>
                    <p><strong>Roast Level:</strong> ${descriptive.roast_level}</p>
                    <p><strong>Fragrance:</strong> ${descriptive.fragrance_attributes.join(', ')}</p>
                    <p><strong>Acidity Score:</strong> ${descriptive.acidity_intensity}/10</p>
                </div>
            </div>
        `;
        
        // Display in a new dialog
        const dialog = new frappe.ui.Dialog({
            title: `Report for ${frm.doc.roast_batch}`,
            fields: [
                {
                    fieldtype: "HTML",
                    fieldname: "report_html"
                }
            ],
            size: 'large'
        });
        
        dialog.fields_dict.report_html.$wrapper.html(html);
        dialog.show();
    }
});
