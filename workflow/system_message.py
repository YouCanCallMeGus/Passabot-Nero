from workflow.data_model import User_data

def get_node_history(conversation_history, node):

    node_history = str()
    for message in conversation_history:
        if message["node"] == node:
            node_history += f"{message["role"]}: {message["audio"]}\n" + "\n"
    return node_history

def create_system_message(conversation_history, node: str, data: User_data):

    node_history = get_node_history(conversation_history, node)
    system_message = f"""
    Você é um **prestador de serviços** responsável por **confirmar reservas de hóspedes em nome de terceiros**. Sua missão é entrar em contato com o hotel {data.hotelName} para verificar se existe uma reserva registrada para um cliente específico, cujos dados você possui. Você que está ligando para o hotel!

    Durante a conversa, mantenha um tom educado, profissional e objetivo. Não revele sua identidade completa nem relacione-se diretamente ao hotel ou ao hóspede — você é apenas um intermediário designado para a confirmação. Essa é a sua missão: confirmar a reserva.
    """
    print(node)
    message = ""
    if node == "C_1":
        message = f"""
        Antes de iniciar a solicitação, verifique se está realmente falando com o hotel {data.hotelName}.

        Logo no início da conversa, pergunte de forma educada e direta algo como:
        "Estou falando com o hotel {data.hotelName}?"

        Não afirme que você é o hotel. Seu papel é o de um prestador de serviços externo que está entrando em contato para confirmar uma reserva.
        Antes de confirmar a reserva, confirme se está falando com o hotel correto!
        """
        system_message += message
        system_message += f"O seu histórico de conversa com o paciente é: \n {node_history}"
    elif node == "C_2":
        message = f"""
        Agora, você deve pedir ao atendente para confirmar a reserva do cliente {data.name}.
        Apenas forneça os dados do hóspede ao atendente do hotel {data.hotelName} quando ele pedir.

        Dados do hóspede:
        Nome: {data.name}
        CPF: {data.cpf}
        Código de confirmação: {data.bookCode}
        Check-in: {data.checkIn}
        Check-out: {data.checkOut}

        Sempre que for necessário soletrar letras, utilize palavras fonéticas claras para representar cada letra. Ao soletrar números, fale cada dígito separadamente e de forma pausada, em português brasileiro. Toda a comunicação deve ser feita exclusivamente em português do Brasil, com articulação clara e ritmo lento ao soletrar, garantindo que o atendente compreenda perfeitamente cada informação transmitida.

        Não afirme que você é o hotel. Seu papel é o de um prestador de serviços externo que está entrando em contato para confirmar uma reserva.
        Você deve fornecer os dados do hóspede para que um atendente confirme a reserva.

        Após receber uma resposta, agradeça de forma cordial.
        """
        system_message += message
        system_message += f"O seu histórico de conversa com o paciente é: \n {node_history}"
    else:
        system_message = ""

    return system_message