import os

def gerar_gabarito(total_questoes, alternativas, orientacao, id_prova):
  """
  Gera um gabarito personalizado
  (implementação completa virá posteriormente)
  """

  pasta = "../examples"

  if not os.path.exists(pasta):
    os.makedirs(pasta)
  
  caminho = os.path.join(pasta, f'{id_prova}.png')

  # Aqui futuramente será a geração de imagem
  with open(caminho, 'w') as f:
    f.write('placeholder')

  return caminho