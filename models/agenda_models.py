def adicionar_agendamento(username, email, telefone, data, servico):
    from app_server import Agenda, db
    novo_agendamento = Agenda(username=username, email=email, telefone=telefone, data=data, servico=servico)
    db.session.add(novo_agendamento)
    db.session.commit()
    print("Agendamento criado com sucesso !")
    return ("Agendamento criado com sucesso !")
