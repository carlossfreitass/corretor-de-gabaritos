import os
import json
import qrcode
import math
from PIL import Image, ImageDraw, ImageFont

# CÁLCULO DE COLUNAS
def calcular_colunas(total_questoes):
    questoes_por_coluna = 10
    colunas = math.ceil(total_questoes / questoes_por_coluna)
    return colunas, questoes_por_coluna

# DIMENSÕES DA FOLHA
def calcular_dimensoes(total_questoes):
    colunas, questoes_por_coluna = calcular_colunas(total_questoes)

    largura_base_qr = 450 
    largura_por_coluna = 320 
    margem_direita = 100

    largura = largura_base_qr + (colunas * largura_por_coluna) + margem_direita
    # Aumentada a altura base para acomodar a nova seção de nome sem apertar o rodapé
    altura = int(700 + (questoes_por_coluna * 85))

    return int(largura), int(altura)

# CRIAR IMAGEM
def criar_folha(total_questoes):
    largura, altura = calcular_dimensoes(total_questoes)
    imagem = Image.new("RGB", (largura, altura), "white")
    draw = ImageDraw.Draw(imagem)
    return imagem, draw, largura, altura

# FONTES
def carregar_fontes():
    try:
        return (
            ImageFont.truetype("../fonts/arialbd.ttf", 50),
            ImageFont.truetype("../fonts/arialbd.ttf", 35),
            ImageFont.truetype("../fonts/arialbd.ttf", 30),
        )
    except IOError:
        return (ImageFont.load_default(), ImageFont.load_default(), ImageFont.load_default())

# BORDA
def desenhar_borda_externa(draw, largura, altura):
    margem = 20
    draw.rectangle((margem, margem, largura - margem, altura - margem), outline="black", width=3)

# TÍTULO
def desenhar_titulo(nome_prova, draw, largura, font):
    texto = f"{(nome_prova or 'GABARITO').upper()}"
    draw.text((largura / 2, 70), texto, fill="black", anchor="mm", font=font)

# SEÇÃO DO NOME
def desenhar_secao_nome(draw, largura, font):
    x1, y1 = 20, 130
    x2, y2 = largura - 20, 220
    
    draw.rectangle((x1, y1, x2, y2), outline="black", width=3)
    
    draw.text((x1 + 25, y1 + 45), "Nome:", fill="black", anchor="lm", font=font)
    
    draw.line((x1 + 130, y1 + 65, x2 - 25, y1 + 65), fill="black", width=2)

# LINHA CABEÇALHO
def desenhar_linhas_cabecalho(draw, largura):
    draw.line((20, 130, largura - 20, 130), fill="black", width=3)

# LINHA RODAPÉ
def desenhar_linhas_rodape(draw, largura, altura):
    draw.line((20, altura - 130, largura - 20, altura - 130), fill="black", width=3)

# QR CODE
def gerar_qrcode(imagem, altura, id_prova, total_questoes, alternativas, x1):
    metadata = {
        "id_prova": id_prova,
        "total_questoes": total_questoes,
        "alternativas": alternativas,
    }
    qr = qrcode.make(json.dumps(metadata))
    tamanho_qr = 250 
    qr = qr.resize((tamanho_qr, tamanho_qr))

    area_centro = (x1 - tamanho_qr) / 2
    x = int(area_centro)
    y = int((altura / 2) - (tamanho_qr / 2)) + 50 

    imagem.paste(qr, (x, y))
    return x + tamanho_qr // 2, y + tamanho_qr

# TEXTO QR
def escrever_id_prova(draw, x, y, id_prova, font):
    draw.text((x, y + 40), f"Prova: {id_prova}", fill="black", anchor="mm", font=font)

# TEXTO RODAPÉ
def escrever_id_rodape(draw, largura, altura, id_prova, font):
    draw.text((largura / 2, altura - 70), f"Prova: {id_prova}", fill="black", anchor="mm", font=font)

# ANCHORS EXTERNOS
def desenhar_anchors(draw, largura, altura):
    tamanho = 50
    margem = 50
    pontos = [
        (margem, margem),
        (largura - margem - tamanho, margem),
        (margem, altura - margem - tamanho),
        (largura - margem - tamanho, altura - margem - tamanho),
    ]
    for x, y in pontos:
        draw.rectangle((x, y, x + tamanho, y + tamanho), fill="black")

# CAIXA DE RESPOSTAS
def desenhar_caixa_respostas(draw, largura, altura):
    x1 = 400 
    y1 = 260
    x2 = largura - 60
    y2 = altura - 200

    draw.rectangle((x1, y1, x2, y2), outline="black", width=4)
    return x1, y1, x2, y2

# ANCHORS DA CAIXA
def desenhar_marcadores_caixa(draw, x1, y1, x2, y2):
    tamanho = 35
    pontos = [
        (x1 + 15, y1 + 15),
        (x2 - 50, y1 + 15),
        (x1 + 15, y2 - 50),
        (x2 - 50, y2 - 50),
    ]
    for x, y in pontos:
        draw.rectangle((x, y, x + tamanho, y + tamanho), fill="black")

# GRADE OMR (RECONHECIMENTO ÓPTICO DE MARCAS)
def desenhar_grade(draw, x1, y1, x2, y2, total_questoes, alternativas, largura, font_texto, font_questao):
    colunas, questoes_por_coluna = calcular_colunas(total_questoes)

    altura_caixa = y2 - y1
    largura_caixa = x2 - x1

    largura_coluna = 320 
    espacamento_linha = (altura_caixa * 0.75) / questoes_por_coluna

    raio = 16 
    espacamento_bolha = 45 
    letras = ["a", "b", "c", "d", "e"]

    # CÁLCULO DE CENTRALIZAÇÃO VERTICAL
    altura_bloco = ((questoes_por_coluna - 1) * espacamento_linha) + 50 + raio
    margem_superior = (altura_caixa - altura_bloco) / 2
    y_base = y1 + margem_superior + 30 

    # CÁLCULO DE CENTRALIZAÇÃO HORIZONTAL
    largura_visual_ultima_coluna = 80 + ((alternativas - 1) * espacamento_bolha) + raio
    largura_bloco = ((colunas - 1) * largura_coluna) + largura_visual_ultima_coluna
    margem_esquerda = (largura_caixa - largura_bloco) / 2

    for coluna in range(colunas):
        x_inicio = x1 + margem_esquerda + (coluna * largura_coluna)
        y_inicio = y_base

        # ALTERNATIVAS
        for i in range(alternativas):
            x = x_inicio + 80 + (i * espacamento_bolha)
            draw.text((x, y_inicio - 30), letras[i], fill="black", anchor="mm", font=font_texto)

        # QUESTÕES
        for q in range(questoes_por_coluna):
            numero = coluna * questoes_por_coluna + q
            if numero >= total_questoes: break
            y = y_inicio + (q * espacamento_linha)
            draw.text((x_inicio + 50, y + 20), f"Q{numero + 1:02}:", fill="black", anchor="rm", font=font_questao)
            for a in range(alternativas):
                x = x_inicio + 80 + a * espacamento_bolha
                draw.ellipse((x - raio, y + 20 - raio, x + raio, y + 20 + raio), outline="black", width=3)

# SALVAR
def salvar(imagem, id_prova):
    pasta = '../examples'

    if not os.path.exists(pasta):
        os.makedirs(pasta)

    caminho = os.path.join(pasta, f"{id_prova}.png")
    imagem.save(caminho)

    return caminho

# FUNÇÃO PRINCIPAL (Arquitetura mantida com nova ordem de chamadas)
def gerar_gabarito(nome_prova, id_prova, total_questoes, alternativas):
    imagem, draw, largura, altura = criar_folha(total_questoes)
    font_titulo, font_texto, font_questao = carregar_fontes()

    desenhar_borda_externa(draw, largura, altura)
    desenhar_anchors(draw, largura, altura)
    desenhar_titulo(nome_prova, draw, largura, font_titulo)
    desenhar_linhas_cabecalho(draw, largura)

    desenhar_secao_nome(draw, largura, font_texto)

    x1, y1, x2, y2 = desenhar_caixa_respostas(draw, largura, altura)
    desenhar_marcadores_caixa(draw, x1, y1, x2, y2)

    pos_x, pos_y = gerar_qrcode(imagem, altura, id_prova, total_questoes, alternativas, x1)
    escrever_id_prova(draw, pos_x, pos_y, id_prova, font_texto)
    desenhar_grade(draw, x1, y1, x2, y2, total_questoes, alternativas, largura, font_texto, font_questao)

    desenhar_linhas_rodape(draw, largura, altura)
    escrever_id_rodape(draw, largura, altura, id_prova, font_texto)

    return salvar(imagem, id_prova)