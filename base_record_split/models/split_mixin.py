from odoo import fields, models


class SplitMixin(models.AbstractModel):
    _name = "split.mixin"
    _description = "Mixin para registros que podem ser divididos"

    split_from_id = fields.Many2one(
        comodel_name="self",
        string="Dividido de",
        readonly=True,
        help="Registro original do qual este foi dividido",
    )

    split_child_ids = fields.One2many(
        comodel_name="self",
        inverse_name="split_from_id",
        string="Registros Divididos",
        help="Registros criados a partir da divisão deste",
    )
