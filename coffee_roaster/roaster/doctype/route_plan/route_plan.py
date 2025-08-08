from frappe.model.document import Document

class RoutePlan(Document):
    def before_save(self):
        self.total_outlets = sum([
            self.gov, self.ngo, self.emb, self.corp, self.edu, self.smkt,
            self.expo, self.retail, self.dist, self.caf, self.hotel, self.rest
        ])
