
from odoo import api, fields, models
from odoo.exceptions import ValidationError


class EstatePropertyOffer(models.Model):
    _name = "estate.property.offer"
    _description = "Real Estate Property Offer"
    _order = "price desc"

    price = fields.Float(
        string="Offer Price",
        required=True,
    )

    status = fields.Selection(
        [
            ("pending", "Pending"),
            ("accepted", "Accepted"),
            ("refused", "Refused"),
        ],
        string="Status",
        default="pending",
        required=True,
        copy=False,
    )

    partner_id = fields.Many2one(
        "res.partner",
        string="Buyer",
        required=True,
    )

    property_id = fields.Many2one(
        "estate.property",
        string="Property",
        required=True,
        ondelete="cascade",
    )

    validity = fields.Integer(
        string="Validity (Days)",
        default=7,
    )

    date_deadline = fields.Date(
        string="Deadline",
        compute="_compute_date_deadline",
        inverse="_inverse_date_deadline",
        store=True,
    )


    # Automatically update Property Status when an Offer is created
    @api.model_create_multi
    def create(self, vals_list):
        offers = super().create(vals_list)

        for offer in offers:
            property_record = offer.property_id

            if property_record.state == "new":
                property_record.state = "offer_received"

            elif property_record.state != "offer_received":
                raise ValidationError(
                    "New offers can only be added to properties "
                    "with New or Offer Received status."
                )

        return offers

    @api.depends("validity", "create_date")
    def _compute_date_deadline(self):
        for offer in self:
            if offer.create_date:
                create_date = fields.Datetime.to_datetime(
                    offer.create_date
                ).date()
                offer.date_deadline = fields.Date.add(
                    create_date,
                    days=offer.validity,
                )
            else:
                offer.date_deadline = False

    def _inverse_date_deadline(self):
        for offer in self:
            if offer.create_date and offer.date_deadline:
                create_date = fields.Datetime.to_datetime(
                    offer.create_date
                ).date()
                offer.validity = (
                    fields.Date.to_date(offer.date_deadline)
                    - create_date
                ).days

    @api.constrains("price", "validity")
    def _check_offer_values(self):
        for offer in self:
            if offer.price <= 0:
                raise ValidationError(
                    "Offer Price must be greater than zero."
                )

            if offer.validity < 0:
                raise ValidationError(
                    "Validity cannot be negative."
                )


    # Offer Actions
    def action_accept(self):
        for offer in self:
            if offer.status != "pending":
                raise ValidationError(
                    "Only pending offers can be accepted."
                )

            property_record = offer.property_id

            if property_record.state in ("sold", "canceled"):
                raise ValidationError(
                    "Offers cannot be accepted for sold "
                    "or canceled properties."
                )

            if property_record.state not in (
                "new",
                "offer_received",
            ):
                raise ValidationError(
                    "This property is not available "
                    "for offer acceptance."
                )

            existing_offer = self.search(
                [
                    ("property_id", "=", property_record.id),
                    ("status", "=", "accepted"),
                    ("id", "!=", offer.id),
                ],
                limit=1,
            )

            if existing_offer:
                raise ValidationError(
                    "Another offer has already been accepted "
                    "for this property."
                )

            # Move through the allowed status transitions.
            if property_record.state == "new":
                property_record.state = "offer_received"

            property_record.state = "offer_accepted"
            offer.status = "accepted"


    def action_refuse(self):
        for offer in self:
            if offer.status != "pending":
                raise ValidationError(
                    "Only pending offers can be refused."
                )

            offer.status = "refused"