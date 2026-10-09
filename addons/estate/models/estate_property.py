from odoo import api, fields, models
from odoo.exceptions import ValidationError


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
        default=0.0,
    )

    # Buyer & Salesperson
    buyer_id = fields.Many2one(
        "res.partner",
        string="Buyer",
        copy=False,
    )

    salesperson_id = fields.Many2one(
        "res.users",
        string="Salesperson",
        default=lambda self: self.env.user,
        copy=False,
    )

    # Property Offers
    offer_ids = fields.One2many(
        "estate.property.offer",
        "property_id",
        string="Offers",
        copy=False,
    )

    # Property Type
    property_type_id = fields.Many2one(
        "estate.property.type",
        string="Property Type",
    )

    # Property Details
    bedrooms = fields.Integer(
        string="Bedrooms",
        default=2,
    )

    living_area = fields.Float(
        string="Living Area (sqm)",
        default=0.0,
    )

    garden = fields.Boolean(
        string="Garden",
        default=False,
    )

    garden_area = fields.Float(
        string="Garden Area (sqm)",
        default=0.0,
    )

    # Property Status
    state = fields.Selection(
        [
            ("new", "New"),
            ("offer_received", "Offer Received"),
            ("offer_accepted", "Offer Accepted"),
            ("sold", "Sold"),
            ("canceled", "Canceled"),
        ],
        string="Status",
        default="new",
        required=True,
        copy=False,
    )

    # Garden Behavior
    @api.onchange("garden")
    def _onchange_garden(self):
        if not self.garden:
            self.garden_area = 0.0


    # Status Transition Validation
    def write(self, vals):
        if "state" in vals:
            new_state = vals["state"]

            allowed_transitions = {
                "new": {
                    "offer_received",
                    "sold",
                    "canceled",
                },
                "offer_received": {
                    "offer_accepted",
                    "sold",
                    "canceled",
                },
                "offer_accepted": {
                    "sold",
                    "canceled",
                },
                "sold": set(),
                "canceled": set(),
            }

            for record in self:
                if (
                    new_state != record.state
                    and new_state not in allowed_transitions.get(
                        record.state, set()
                    )
                ):
                    raise ValidationError(
                        "This property status transition is not allowed."
                    )

        return super().write(vals)

    # Property Actions
    def action_sold(self):
        for record in self:
            if record.state == "canceled":
                raise ValidationError(
                    "A canceled property cannot be marked as sold."
                )

            if record.state == "sold":
                raise ValidationError(
                    "This property is already sold."
                )

            record.state = "sold"

    def action_cancel(self):
        for record in self:
            if record.state == "sold":
                raise ValidationError(
                    "A sold property cannot be canceled."
                )

            if record.state == "canceled":
                raise ValidationError(
                    "This property is already canceled."
                )

            record.state = "canceled"

    # Data Validation
    @api.constrains(
        "living_area",
        "garden_area",
        "expected_price",
        "bedrooms",
    )
    def _check_property_values(self):
        for record in self:
            if record.living_area < 0:
                raise ValidationError(
                    "Living Area cannot be negative."
                )

            if record.garden_area < 0:
                raise ValidationError(
                    "Garden Area cannot be negative."
                )

            if record.expected_price < 0:
                raise ValidationError(
                    "Expected Price cannot be negative."
                )

            if record.bedrooms < 0:
                raise ValidationError(
                    "Bedrooms cannot be negative."
                )