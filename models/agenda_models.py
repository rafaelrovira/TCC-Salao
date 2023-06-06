def adicionar_agendamento(user_id ,username, email, telefone, data, servico):
    from app import Agenda, db
    novo_agendamento = Agenda(user_id=user_id, username=username, email=email, telefone=telefone, data=data, servico=servico)
    db.session.add(novo_agendamento)
    db.session.commit()
    print("Agendamento criado com sucesso !")
    return ("Agendamento criado com sucesso !")


def excluir_agendamento(id_agendamento):
    from app import Agenda, db
    agendamento = Agenda.query.filter_by(id=id_agendamento).first()
    if agendamento:
        db.session.delete(agendamento)
        db.session.commit()
        print("Agendamento removido com sucesso !")
        return ("Agendamento removido com sucesso !")
    else:
        print("Agendamento não encontrado")
        return ("Agendamento não encontrado")

