from odoo import api, fields, models


class BaseRecordSplitWizard(models.TransientModel):
    _name = "base.record.split.wizard"
    _description = "Assistente Genérico de Divisão de Registro"

    model_name = fields.Char(string="Modelo", required=True)
    res_id = fields.Integer(string="ID do Registro Original", required=True)
    archive_original = fields.Boolean(
        string="Arquivar registro original",
        default=True,
        help="Se marcado, o registro original será arquivado após a divisão",
    )
    line_ids = fields.One2many(
        "base.record.split.line", "wizard_id", string="Novos Registros"
    )

    @api.model
    def default_get(self, fields_list):
        res = super().default_get(fields_list)
        if self._context.get("active_model") and self._context.get("active_id"):
            res.update(
                {
                    "model_name": self._context["active_model"],
                    "res_id": self._context["active_id"],
                }
            )
        return res

    def action_split_records(self):
        self.ensure_one()
        Model = self.env[self.model_name]
        original_record = Model.browse(self.res_id)
        new_records = Model.browse()

        for line in self.line_ids:
            values = line.get_create_values(original_record)
            new_record = Model.create(values)

            # Copia mensagens e seus anexos
            message_vals = []
            for message in original_record.message_ids.filtered(
                lambda m: not m.internal
            ):
                msg_vals = message.copy_data()[0]
                msg_vals.update(
                    {
                        "res_id": new_record.id,
                        "model": self.model_name,
                    }
                )
                for field in ["id", "message_id", "notification_ids"]:
                    msg_vals.pop(field, None)
                message_vals.append(msg_vals)

            self.env["mail.message"].create(message_vals)

            # Copia seguidores
            follower_vals = []
            for follower in original_record.message_follower_ids:
                fol_vals = follower.copy_data()[0]
                fol_vals.update(
                    {
                        "res_id": new_record.id,
                        "res_model": self.model_name,
                    }
                )
                follower_vals.append(fol_vals)
            self.env["mail.followers"].create(follower_vals)

            # Copia atividades
            for activity in original_record.activity_ids:
                activity.copy(
                    {
                        "res_id": new_record.id,
                        "res_model_id": self.env["ir.model"]._get_id(self.model_name),
                    }
                )

            if "split_from_id" in Model._fields:
                new_record.split_from_id = original_record.id

            new_records |= new_record

        if self.archive_original and "active" in Model._fields:
            original_record.write({"active": False})

        return {
            "type": "ir.actions.act_window",
            "res_model": self.model_name,
            "view_mode": "tree,form",
            "domain": [("id", "in", new_records.ids)],
        }


class BaseRecordSplitWizardLine(models.TransientModel):
    _name = "base.record.split.line"
    _description = "Linha de Divisão de Registro"

    wizard_id = fields.Many2one(
        "base.record.split.wizard", required=True, ondelete="cascade"
    )
    name = fields.Char(string="Nome", required=True)
    description = fields.Text(string="Descrição")

    def get_create_values(self, original_record):
        values = {
            "name": self.name,
            "description": self.description
            or getattr(original_record, "description", False),
        }
        for field in ["team_id", "user_id", "partner_id"]:
            if hasattr(original_record, field):
                values[field] = getattr(original_record, field).id
        return values
