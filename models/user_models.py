from app_server import User, db



# Adicionar usuário
def adicionar_user(username, password, email, telefone):
    new_user = User(username=username, password=password,
                    email=email, telefone=telefone)
    db.session.add(new_user)
    db.session.commit()
    print("Usuário criado com sucesso !")
    return ("Usuário criado com sucesso !")


# Consultar dados do usuário
def consultar_user(email):
    dados = User.query.filter_by(email=f'{email}').first()
    if dados:
        return dados  # retorna o objeto com os dados do user
    else:
        return "Nenhum usuário encontrado"


# Alterar usuário pelo id
def alterar_user(username, password, email, telefone):
    objeto = consultar_user(email)
    if objeto:
        id = objeto.id
        user = User.query.get(id)
        user.username = username
        user.password = password
        user.email = email
        user.telefone = telefone
        db.session.commit()
        print("Usuário alterado com sucesso !")
        return ("Usuário alterado com sucesso !")
    else:
        return ("Usuário não encontrado")


# Deleta usuário pelo id
def deleta_user(email):
    objeto = consultar_user(email)
    if objeto != 'Nenhum usuário encontrado':
        id = objeto.id
        user = User.query.get(id)
        user.query.filter_by(id=id).delete()
        db.session.commit()
        print("Usuário deletado com sucesso")
        return ("Usuário deletado com sucesso")
    else:
        print("Usuário não encontrado")
