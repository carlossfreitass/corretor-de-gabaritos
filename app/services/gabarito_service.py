import os
import json
import qrcode
import datetime
from PIL import Image, ImageDraw, ImageFont

def calcular_dimensoes(total_questoes):
  largura = 1400
  altura = 550 + (total_questoes * 70)

  return largura, altura

def criar_folha(total_questoes):
  largura, altura = calcular_dimensoes(total_questoes)

  imagem = Image.new('RGB', (largura, altura), 'white')
  draw = ImageDraw.Draw(imagem)

  return imagem, draw, largura, altura

def carregar_fontes(largura):
  font_titulo = ImageFont.truetype('../fonts/arialbd.ttf', int(largura * 0.035))
  font_texto = ImageFont.truetype('../fonts/arialbd.ttf', int(largura * 0.022))
  font_questao = ImageFont.truetype('../fonts/arialbd.ttf', int(largura * 0.020))

  return font_titulo, font_texto, font_questao

def desenhar_titulo(draw, largura, font_titulo):
  texto = f'PROVA - {datetime.date.today().year}'

  draw.text(
    (largura / 2, 60),
    texto,
    fill='black',
    anchor='mm',
    font=font_titulo
  )

def desenhar_linhas_cabecalho(draw, largura):
  draw.line((40, 110, largura - 40, 110), fill='black', width=3)

def desenhar_linhas_rodape(draw, largura, altura):
  draw.line((40, altura - 110, largura - 40, altura - 110), fill='black', width=3)

def gerar_qrcode(imagem, largura, altura, id_prova, total_questoes, alternativas):
  metadata = {
    "id_prova": id_prova,
    "total_questoes": total_questoes,
    "alternativas": alternativas
  }

  qr = qrcode.make(json.dumps(metadata))

  margem = 40
  largura_caixa = int(largura * 0.32) + 50
  area_livre_esquerda = largura - largura_caixa - 120 - (margem * 2)

  altura_util = altura - 220
  tamanho_qr = int(min(area_livre_esquerda, altura_util * 0.35))
  tamanho_qr = max(200, min(tamanho_qr, 500))

  qr = qr.resize((tamanho_qr, tamanho_qr))

  x = int((area_livre_esquerda / 2) - (tamanho_qr / 2)) + margem

  y_centro = 110 + (altura_util / 2)
  y = int(y_centro - (tamanho_qr / 2))

  imagem.paste(qr, (x, y))

  return x + (tamanho_qr // 2), y + tamanho_qr

def escrever_id_prova(draw, pos_x, pos_y, id_prova, font_texto):
  draw.text(
    (pos_x, pos_y + 40),
    f'Prova: {id_prova}',
    fill='black',
    anchor='mm',
    font=font_texto
  )

def desenhar_caixa_respostas(draw, largura, altura):
  largura_caixa = int(largura * 0.32) + 50

  x1 = largura - largura_caixa - 120
  y1 = 250

  x2 = largura - 120
  y2 = altura - 200

  draw.rectangle((x1, y1, x2, y2), outline='black', width=4)

  return x1, y1, x2, y2

def desenhar_registration_anchors(draw, largura, altura):
  tamanho = 35

  anchors = [
    (40, 40),
    (largura - 40 - tamanho , 40),
    (40, altura - 40 - tamanho),
    (largura - 40 - tamanho, altura - 40 - tamanho)
  ]

  for x, y in anchors:
    draw.rectangle((x, y, x + tamanho, y + tamanho), fill='black')

def desenhar_marcadores_caixa(draw, x1, y1, x2, y2):
  tamanho = 30

  pontos = [
    (x1 + 15, y1 + 15),
    (x2 - 45, y1 + 15),
    (x1 + 15, y2 - 45),
    (x2 - 45, y2 - 45)
  ]

  for x, y in pontos:
    draw.rectangle((x, y, x + tamanho, y + tamanho), fill='black')

def desenhar_grade(draw, x1, y1, x2, y2, total_questoes, alternativas, largura, font_texto, font_questao):
  largura_grade = x2 - x1 - 120

  espacamento_coluna = largura_grade / alternativas
  espacamento_linha = 65

  largura_total_conteudo = (alternativas * espacamento_coluna) + 100
  altura_total_conteudo = total_questoes * espacamento_linha

  margem_x = ((x2 - x1 + 30) -  largura_total_conteudo) / 2
  margem_y = ((y2 - y1) - altura_total_conteudo) / 2

  raio = int(largura * 0.010)

  letras = ['A', 'B', 'C', 'D', 'E']

  x_inicio = x1 + margem_x + 100
  y_inicio = y1 + margem_y + 30

  for i in range(alternativas):
    x = x_inicio + (i * espacamento_coluna)

    draw.text(
      (x, y_inicio - 40),
      letras[i].lower(),
      fill='black',
      anchor='mm',
      font=font_texto
    )

    for q in range(total_questoes):
      y = y_inicio + (q * espacamento_linha)

      draw.text(
        (x_inicio - 40, y),
        f'Q{q + 1}',
        fill='black',
        anchor='rm',
        font=font_questao
      )

      for a in range(alternativas):
        x = x_inicio + (a * espacamento_coluna)

        draw.ellipse(
          (
            x - raio,
            y - raio,
            x + raio,
            y + raio
          ),
          outline='black',
          width=3
        )

def escrever_id_rodape(draw, largura, altura, id_prova, font_texto):
  draw.text(
    (largura / 2, altura - 60),
    f'Prova: {id_prova}',
    fill='black',
    anchor='mm',
    font=font_texto
  )

def salvar(imagem, id_prova):
  pasta = '../examples'

  if not os.path.exists(pasta):
    os.makedirs(pasta)
  
  caminho = os.path.join(pasta, f'{id_prova}.png')

  imagem.save(caminho)

  return caminho

def gerar_gabarito(total_questoes, alternativas, orientacao, id_prova):
  imagem, draw, largura, altura = criar_folha(total_questoes)
  font_titulo, font_texto, font_questao = carregar_fontes(largura)
  desenhar_registration_anchors(draw, largura, altura)
  desenhar_titulo(draw, largura, font_titulo)
  desenhar_linhas_cabecalho(draw, largura)
  pos_x, pos_y = gerar_qrcode(imagem, largura, altura, id_prova, total_questoes, alternativas)
  escrever_id_prova(draw, pos_x, pos_y, id_prova, font_texto)
  x1, y1, x2, y2 = desenhar_caixa_respostas(draw, largura, altura)
  desenhar_marcadores_caixa(draw, x1, y1, x2, y2)
  desenhar_grade(draw, x1, y1, x2, y2, total_questoes, alternativas, largura, font_texto, font_questao)
  desenhar_linhas_rodape(draw, largura, altura)
  escrever_id_rodape(draw, largura, altura, id_prova, font_texto)
  caminho = salvar(imagem, id_prova)

  return caminho