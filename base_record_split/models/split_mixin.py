from odoo import api, fields, models


class SplitMixin(models.AbstractModel):
    _name = "split.mixin"
    _description = "Mixin para registros que podem ser divididos"

    split_from_id = fields.Many2one(
        string="Dividido de",
        readonly=True,
        help="Registro original do qual este foi dividido",
    )

    split_child_ids = fields.One2many(
        string="Registros Divididos",
        help="Registros criados a partir da divisão deste",
    )

    def action_view_split_children(self):
        self.ensure_one()
        return {
            "type": "ir.actions.act_window",
            "name": "Registros Divididos",
            "res_model": self._name,
            "view_mode": "tree,form",
            "domain": [("id", "in", self.split_child_ids.ids)],
            "context": dict(self.env.context),
        }

    def action_open_split_wizard(self):
        """Abre a wizard genérica de divisão de registros"""
        self.ensure_one()
        return {
            "name": "Dividir Registro",
            "type": "ir.actions.act_window",
            "res_model": "base.record.split.wizard",
            "view_mode": "form",
            "target": "new",
            "context": {
                "default_model_name": self._name,
                "default_res_id": self.id,
            },
        }

    @api.model
    def _setup_fields(self):
        """Define dinamicamente os modelos de relação para os campos split_from/child"""
        result = super()._setup_fields()
        model_name = self._name
        if model_name != "split.mixin":
            self._fields["split_from_id"].comodel_name = model_name
            self._fields["split_child_ids"].comodel_name = model_name
            self._fields["split_child_ids"].inverse_name = "split_from_id"
        return result
