import os
from PIL import Image, ImageDraw, ImageFont

def gerar_gabarito(total_questoes, alternativas, orientacao, id_prova):
  pasta = "../examples"

  if not os.path.exists(pasta):
    os.makedirs(pasta)
  
  caminho = os.path.join(pasta, f'{id_prova}.png')

  # Parâmetros do layout
  y_inicio = 150
  margem_inferior = 100
  espacamento_linha = 40
  espacamento_alternativa = 40
  raio = 10

  # Tamanho da imagem
  largura = 800
  altura = y_inicio + (total_questoes * espacamento_linha) + margem_inferior

  imagem = Image.new('RGB', (largura, altura), 'white')
  draw =ImageDraw.Draw(imagem)

  # Título
  titulo = f'Gabarito - Prova {id_prova}'
  draw.text((50, 50), titulo, fill='black')

  letras = ['A', 'B', 'C', 'D', 'E']

  for a in range(alternativas):
    # Letra da alternativa
    x = 150 + a * espacamento_alternativa
    y = 110
    draw.text((x - 5, y + 15), letras[a], fill='black')

  for q in range(total_questoes):
    y = y_inicio + q * espacamento_linha

    # Número da questão
    draw.text((50, y), str(q + 1), fill='black')

    for a in range(alternativas):
      x = 150 + a * espacamento_alternativa

      # Desenhar círculo
      draw.ellipse(
        (
          x - raio,
          y - raio,
          x + raio,
          y + raio
        ),
        outline='black',
        width=2
      )

  imagem.save(caminho)

  return caminho