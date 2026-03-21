import os
import json
import qrcode
import datetime
from PIL import Image, ImageDraw, ImageFont

# DIMENSÕES
def calcular_dimensoes(total_questoes):
  largura = 1400
  altura = int(600 + (total_questoes * 70))
  return largura, altura

# CRIAÇÃO DA IMAGEM
def criar_folha(total_questoes):
  largura, altura = calcular_dimensoes(total_questoes)
  imagem = Image.new('RGB', (largura, altura), 'white')
  draw = ImageDraw.Draw(imagem)
  return imagem, draw, largura, altura

# FONTES
def carregar_fontes(largura):
  return (
    ImageFont.truetype('../fonts/arialbd.ttf', int(largura * 0.055)),
    ImageFont.truetype('../fonts/arialbd.ttf', int(largura * 0.032)),
    ImageFont.truetype('../fonts/arialbd.ttf', int(largura * 0.030)),
  )

# BORDA EXTERNA
def desenhar_borda_externa(draw, largura, altura):
  margem = 20
  draw.rectangle(
    (margem, margem, largura - margem, altura - margem),
    outline='black',
    width=3
  )

# TÍTULO
def desenhar_titulo(draw, largura, font):
  texto = f'PROVA - {datetime.date.today().year}'
  draw.text((largura / 2, 70), texto, fill='black', anchor='mm', font=font)

# LINHAS CABEÇALHO
def desenhar_linhas_cabecalho(draw, largura):
  draw.line((20, 130, largura - 20, 130), fill='black', width=3)

# LINHAS RODAPÉ
def desenhar_linhas_rodape(draw, largura, altura):
  draw.line((20, altura - 130, largura - 20, altura - 130), fill='black', width=3)

# QR CODE RESPONSIVO
def gerar_qrcode(imagem, largura, altura, id_prova, total_questoes, alternativas):
  metadata = {
    "id_prova": id_prova,
    "total_questoes": total_questoes,
    "alternativas": alternativas
  }

  qr = qrcode.make(json.dumps(metadata))

  tamanho_qr = int(min(largura * 0.22, altura * 0.25))
  qr = qr.resize((tamanho_qr, tamanho_qr))

  x = int(largura * 0.12)
  y = int((altura / 2) - (tamanho_qr / 2))

  imagem.paste(qr, (x, y))

  return x + tamanho_qr // 2, y + tamanho_qr

# ESCREVER ID EMBAIXO DO QR CODE
def escrever_id_prova(draw, x, y, id_prova, font):
  draw.text((x, y + 40), f'Prova: {id_prova}', fill='black', anchor='mm', font=font)

# ESCREVER ID NO RODAPÉ
def escrever_id_rodape(draw, largura, altura, id_prova, font):
  draw.text((largura / 2, altura - 70), f'Prova: {id_prova}', fill='black', anchor='mm', font=font)

# ANCHORS (REGISTRO)
def desenhar_anchors(draw, largura, altura):
  tamanho = 50
  margem = 50

  pontos = [
    (margem, margem),
    (largura - margem - tamanho, margem),
    (margem, altura - margem - tamanho),
    (largura - margem - tamanho, altura - margem - tamanho)
  ]

  for x, y in pontos:
    draw.rectangle((x, y, x + tamanho, y + tamanho), fill='black')

# CAIXA DE RESPOSTAS
def desenhar_caixa_respostas(draw, largura, altura):
  largura_caixa = int(largura * 0.50)

  x1 = largura - largura_caixa - 100
  y1 = 175
  x2 = largura - 75
  y2 = altura - 200

  draw.rectangle((x1, y1, x2, y2), outline='black', width=4)

  return x1, y1, x2, y2

# ANCHORS (REGISTRO) DA CAIXA DE RESPOSTA 
def desenhar_marcadores_caixa(draw, x1, y1, x2, y2):
  tamanho = 35

  pontos = [
    (x1 + 15, y1 + 15),
    (x2 - 50, y1 + 15),
    (x1 + 15, y2 - 50),
    (x2 - 50, y2 - 50)
  ]

  for x, y in pontos:
    draw.rectangle((x, y, x + tamanho, y + tamanho), fill='black')

# GRADE OMR (RECONHECIMENTO ÓPTICO DE MARCAS)
def desenhar_grade(draw, x1, y1, x2, y2, total_questoes, alternativas, largura, font_texto, font_questao):
  largura_util = x2 - x1 - 140
  altura_util = y2 - y1 - 120

  espacamento_linha = altura_util / total_questoes
  espacamento_coluna = largura_util / alternativas

  raio = int(largura * 0.013)

  letras = ['A', 'B', 'C', 'D', 'E']

  x_inicio = x1 + 155
  y_inicio = y1 + 80

  # LETRAS
  for i in range(alternativas):
    x = x_inicio + i * espacamento_coluna
    draw.text((x, y_inicio - 30), letras[i].lower(), fill='black', anchor='mm', font=font_texto)
  
  # QUESTÕES
  for q in range(total_questoes):
    y = y_inicio + q * espacamento_linha

    draw.text(
      (x_inicio - 50, y + 20),
      f'Q{q + 1}:',
      fill='black',
      anchor='rm',
      font=font_questao
    )

    # BOLHAS DE ALTERNATIVAS
    for a in range (alternativas):
      x = x_inicio + a * espacamento_coluna

      draw.ellipse(
        (x - raio, (y + 20) - raio, x + raio, (y + 20) + raio),
        outline='black',
        width=3
      )

# SALVAR IMAGEM EM PASTA
def salvar(imagem, id_prova):
  pasta = '../examples'

  if not os.path.exists(pasta):
    os.makedirs(pasta)
  
  caminho = os.path.join(pasta, f'{id_prova}.png')
  imagem.save(caminho)

  return caminho

# FUNÇÃO PRINCIPAL
def gerar_gabarito(total_questoes, alternativas, orientacao, id_prova):
  imagem, draw, largura, altura = criar_folha(total_questoes)

  font_titulo, font_texto, font_questao = carregar_fontes(largura)

  desenhar_borda_externa(draw, largura, altura)
  desenhar_anchors(draw, largura, altura)

  desenhar_titulo(draw, largura, font_titulo)
  desenhar_linhas_cabecalho(draw, largura)

  pos_x, pos_y = gerar_qrcode(imagem, largura, altura, id_prova, total_questoes, alternativas)
  escrever_id_prova(draw, pos_x, pos_y, id_prova, font_texto)

  x1, y1, x2, y2 = desenhar_caixa_respostas(draw, largura, altura)
  desenhar_marcadores_caixa(draw, x1, y1, x2, y2)

  desenhar_grade(draw, x1, y1, x2, y2, total_questoes, alternativas, largura, font_texto, font_questao)

  desenhar_linhas_rodape(draw, largura, altura)
  escrever_id_rodape(draw, largura, altura, id_prova, font_texto)

  return salvar(imagem, id_prova)