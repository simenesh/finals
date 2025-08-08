frappe.ui.form.on('Master Route Plan', {
  setup: function(frm) {
    frm.set_query("customer", () => {
      return {
        filters: {
          disabled: 0
        }
      };
    });
  }
});