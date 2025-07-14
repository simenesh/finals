import frappe

def execute(filters=None):
    batch = filters.get("roast_batch")
    columns = [
        {"label": "Time", "fieldtype": "Datetime", "fieldname": "reading_time", "width": 150},
        {"label": "Bean Temp (°C)", "fieldtype": "Float", "fieldname": "bean_temp"},
        {"label": "Env Temp (°C)", "fieldtype": "Float", "fieldname": "environment_temp"},
        {"label": "RoR (°C/min)", "fieldtype": "Float", "fieldname": "ror"}
    ]
    data = frappe.get_all(
        "Roast Machine Telemetry",
        fields=["reading_time", "bean_temp", "environment_temp", "ror"],
        filters={"roast_batch": batch},
        order_by="reading_time"
    )
    # Chart—line graph with three datasets
    chart = {
        "data": {
            "labels": [d.reading_time.strftime("%H:%M:%S") for d in data],
            "datasets": [
                {"name": "Bean Temp", "values": [d.bean_temp for d in data]},
                {"name": "Env Temp", "values": [d.environment_temp for d in data]},
                {"name": "RoR", "values": [d.ror for d in data]}
            ]
        },
        "type": "line",
        "height": 300
    }
    return columns, data, None, chart
