def processar_resultado_final(id_prova, respostas_aluno, gabarito_oficial, valor_prova=10.0, pesos=None, total_alternativas=5):
    # VALIDAÇÃO DE ALTERNATIVAS
    letras_validas = {chr(ord('A') + i) for i in range(total_alternativas)}

    alternativas_invalidas = {
        questao: resposta
        for questao, resposta in gabarito_oficial.items()
        if resposta.upper() not in letras_validas
    }

    if alternativas_invalidas:
        return {
            "erro": (
                f"O gabarito contém alternativas inválidas para uma prova com "
                f"{total_alternativas} alternativas ({', '.join(sorted(letras_validas))})."
            ),
            "alternativas_invalidas": alternativas_invalidas,
        }

    # VALIDAÇÃO DE INTEGRIDADE
    questoes_gabarito = set(gabarito_oficial.keys())
    questoes_aluno = set(respostas_aluno.keys())

    questoes_ausentes = questoes_gabarito - questoes_aluno
    questoes_extras = questoes_aluno - questoes_gabarito

    if questoes_ausentes or questoes_extras:
        return {
            "erro": "Divergência entre gabarito e folha detectada.",
            "questoes_ausentes_na_folha": sorted(questoes_ausentes),
            "questoes_extras_na_folha": sorted(questoes_extras),
        }

    # PESOS
    if pesos is None:
        valor_por_questao = valor_prova / len(gabarito_oficial)
        pesos = {questao: valor_por_questao for questao in gabarito_oficial}

    # VALIDAÇÃO DOS PESOS
    soma_pesos = round(sum(pesos.values()), 2)
    if abs(soma_pesos - valor_prova) > 0.01:
        return {
            "erro": (
                f"A soma dos pesos ({soma_pesos}) "
                f"não corresponde ao valor da prova ({valor_prova})."
            )
        }

    # COMPARAÇÃO QUESTÃO A QUESTÃO
    nota = 0.0
    total_acertos = 0
    total_erros = 0
    total_brancos = 0
    total_rasuras = 0
    detalhado = []

    for questao in sorted(gabarito_oficial.keys()):
        resposta_correta = gabarito_oficial[questao].upper()
        marcado = respostas_aluno.get(questao, 'BRANCO')
        valor_questao = pesos.get(questao, 0)

        if marcado == 'BRANCO':
            status = 'VAZIO'
            total_brancos += 1

        elif marcado == 'RASURA':
            status = 'RASURA'
            total_rasuras += 1

        elif marcado.upper() == resposta_correta:
            status = 'CORRETO'
            total_acertos += 1
            nota += valor_questao

        else:
            status = 'INCORRETO'
            total_erros += 1

        detalhado.append({
            "numero": questao,
            "status": status,
            "marcado_pelo_aluno": marcado,
            "resposta_correta": resposta_correta,
            "valor_questao": valor_questao,
        })

    return {
        "id_prova": id_prova,
        "resumo": {
            "nota": round(nota, 2),
            "valor_prova": valor_prova,
            "total_acertos": total_acertos,
            "total_erros": total_erros,
            "total_brancos": total_brancos,
            "total_rasuras": total_rasuras,
            "total_questoes": len(gabarito_oficial),
        },
        "detalhado": detalhado,
    }