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
        for message in original_record.message_ids.filtered(lambda m: not m.internal):
            # Prepara valores para a cópia da mensagem
            msg_vals = message.copy_data()[0]
            msg_vals.update(
                {
                    "res_id": new_record.id,
                    "model": self.model_name,
                }
            )
            # Remove campos que não devem ser copiados
            for field in ["id", "message_id", "notification_ids"]:
                msg_vals.pop(field, None)
            message_vals.append(msg_vals)

        # Cria as mensagens em batch
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

        # Referência cruzada (se o modelo tiver o campo)
        if "split_from_id" in Model._fields:
            new_record.split_from_id = original_record.id

        new_records |= new_record

    # Arquivar o registro original, se aplicável
    if self.archive_original and "active" in Model._fields:
        original_record.write({"active": False})

    return {
        "type": "ir.actions.act_window",
        "res_model": self.model_name,
        "view_mode": "tree,form",
        "domain": [("id", "in", new_records.ids)],
    }
