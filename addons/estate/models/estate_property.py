from odoo import fields, models


class EstateProperty(models.Model):
    _name = "estate.property"
    _description = "Real Estate Property"

    # Basic Information
    name = fields.Char(
        string="Property Name",
        required=True,
    )

    description = fields.Text(
        string="Description",
    )

    postcode = fields.Char(
        string="Postcode",
    )

    date_availability = fields.Date(
        string="Date Availability",
    )

    expected_price = fields.Float(
        string="Expected Price",
    )

    # Property Type
    property_type = fields.Selection(
        [
            ("house", "House"),
            ("apartment", "Apartment"),
            ("land", "Land"),
        ],
        string="Property Type",
    )