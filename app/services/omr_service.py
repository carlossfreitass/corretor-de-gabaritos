import math
import cv2
import numpy as np
import json
from pyzbar.pyzbar import decode
from utils.image_utils import convert_to_gray

def ordenar_pontos(pontos):
  # ORDENA OS 4 PONTOS
  pontos = pontos.reshape((4, 2))
  novos_pontos = np.zeros((4, 1, 2), dtype=np.float32)

  soma = pontos.sum(1)
  novos_pontos[0] = pontos[np.argmin(soma)]
  novos_pontos[2] = pontos[np.argmax(soma)]

  diff = np.diff(pontos, axis=1)
  novos_pontos[1] = pontos[np.argmin(diff)]
  novos_pontos[3] = pontos[np.argmax(diff)]

  return novos_pontos

def alinhar_folha(imagem):
  # PRÉ-PROCESSAMENTO
  gray = convert_to_gray(imagem)
  blurred = cv2.GaussianBlur(gray, (5, 5), 0)
  edged = cv2.Canny(blurred, 75, 200)

  # CONTORNOS
  contornos, _ = cv2.findContours(edged.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
  contornos = sorted(contornos, key=cv2.contourArea, reverse=True)

  for c in contornos:
    perimetro = cv2.arcLength(c, True)
    approx = cv2.approxPolyDP(c, 0.02 * perimetro, True)

    if len(approx) == 4:
      pontos_ordenados = ordenar_pontos(approx)

      largura_final, altura_final = 1000, 1400
      pts_destino = np.float32([
        [0, 0], [largura_final, 0], [largura_final, altura_final], [0, altura_final]
      ])

      matriz = cv2.getPerspectiveTransform(pontos_ordenados, pts_destino)
      warped = cv2.warpPerspective(imagem, matriz, (largura_final, altura_final))

      return warped
  
  return None

def ler_dados_qrcode(imagem):
  qr_codes = decode(imagem)

  for qr in qr_codes:
    dados = qr.data.decode('utf-8')
    try:
      return json.loads(dados)
    except json.JSONDecodeError:
      continue
  
  return None

def isolar_caixa_respostas(imagem):
  gray = convert_to_gray(imagem)

  # ANCHORS INTERNOS
  blurred = cv2.GaussianBlur(gray, (3, 3), 0)
  edged = cv2.Canny(blurred, 50, 150)
  contornos, _ = cv2.findContours(edged, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)

  altura_img, largura_img = imagem.shape[:2]
  area_imagem = altura_img * largura_img
  candidatos = []

  for c in contornos:
    perimetro = cv2.arcLength(c, True)
    approx = cv2.approxPolyDP(c, 0.02 * perimetro, True)

    # FILTRO PARA A CAIXA DE RESPOSTAS
    if len(approx) == 4:
      area = cv2.contourArea(c)
      if not (0.10 * area_imagem < area < 0.75 * area_imagem):
        continue

      x, y, w, h = cv2.boundingRect(approx)
      aspect_ratio = h / w
      if not (0.8 < aspect_ratio < 3.5):
        continue

      candidatos.append((area, approx, x, y, w, h))

  if not candidatos:
    return None, None, None, None, None

  candidatos.sort(key=lambda c: c[0], reverse=True)
  _, _, x, y, w, h = candidatos[0]

  # RECORTE SEM MARGEM
  x1 = max(0, x)
  y1 = max(0, y)
  x2 = min(largura_img, x + w)
  y2 = min(altura_img, y + h)

  return imagem[y1:y2, x1:x2], x1, y1, x2, y2

def calcular_colunas(total_questoes):
  questoes_por_coluna = 10
  colunas = math.ceil(total_questoes / questoes_por_coluna)
  return colunas, questoes_por_coluna

def calcular_dimensoes(total_questoes):
  # ESCALA DO ROI - ESPELHO DO GERADOR
  colunas, _ = calcular_colunas(total_questoes)
  largura_base_qr = 450
  largura_por_coluna = 320
  margem_direita = 100
  largura = largura_base_qr + (colunas * largura_por_coluna) + margem_direita
  altura = int(700 + (10 * 85))
  return int(largura), int(altura)

def mapear_coordenadas_bolhas(roi_shape, total_questoes, alternativas):
  # CALCULA A ALTURA E LARGURA DO RECORTE
  altura_caixa, largura_caixa = roi_shape[:2]
  colunas, questoes_por_coluna = calcular_colunas(total_questoes)

  # ESCALA DO ROI EM RELAÇÃO AO GERADOR
  largura_gerador, altura_gerador = calcular_dimensoes(total_questoes)
  largura_caixa_gerador = (largura_gerador - 60) - 400
  altura_caixa_gerador  = (altura_gerador - 200) - 260
  escala_x = largura_caixa / largura_caixa_gerador
  escala_y = altura_caixa  / altura_caixa_gerador

  # CONSTANTES ESCALADAS EM RELAÇÃO AO GERADOR
  largura_coluna    = 320 * escala_x
  espacamento_linha = (altura_caixa * 0.75) / questoes_por_coluna
  raio              = max(1, int(16 * escala_x))
  espacamento_bolha = 45  * escala_x
  letras = ["A", "B", "C", "D", "E"]

  # CENTRALIZAÇÃO VERTICAL
  altura_bloco = ((questoes_por_coluna - 1) * espacamento_linha) + 50 * escala_y + raio
  margem_superior = (altura_caixa - altura_bloco) / 2
  y_base = margem_superior + 30 * escala_y

  # CENTRALIZAÇÃO HORIZONTAL
  largura_visual_ultima_coluna = 80 * escala_x + ((alternativas - 1) * espacamento_bolha) + raio
  largura_bloco = ((colunas - 1) * largura_coluna) + largura_visual_ultima_coluna
  margem_esquerda = (largura_caixa - largura_bloco) / 2

  coordenadas = {}

  for coluna in range(colunas):
      x_inicio = margem_esquerda + (coluna * largura_coluna)
      y_inicio = y_base

      for q in range(questoes_por_coluna):
          numero = coluna * questoes_por_coluna + q
          if numero >= total_questoes:
              break

          y = y_inicio + (q * espacamento_linha) + 20 * escala_y
          
          chave_questao = f"Q{numero + 1:02}"
          coordenadas[chave_questao] = {}

          for a in range(alternativas):
              x = x_inicio + 80 * escala_x + (a * espacamento_bolha)
              coordenadas[chave_questao][letras[a]] = (int(x), int(y))

  return coordenadas, raio

def corrigir_gabarito(file):
  file_bytes = np.frombuffer(file.read(), np.uint8)
  img = cv2.imdecode(file_bytes, cv2.IMREAD_COLOR)

  # ALINHAMENTO
  folha_alinhada = alinhar_folha(img)
  if folha_alinhada is None:
    return {"erro": "Não foi possível detectar as bordas da folha."}
  
  # QR CODE
  dados_prova = ler_dados_qrcode(folha_alinhada)
  if not dados_prova:
    return {"erro": "QR Code ilegível ou ausente na imagem."}
  
  # ISOLAR CAIXA DE RESPOSTAS
  roi_respostas, cx1, cy1, cx2, cy2 = isolar_caixa_respostas(folha_alinhada)
  if roi_respostas is None:
    return {"erro": "Não foi possível localizar os delimitadores da grade de respostas."}
  
  total_q = dados_prova['total_questoes']
  total_alt = dados_prova['alternativas']
  
  mapa_bolhas, raio = mapear_coordenadas_bolhas(roi_respostas.shape, total_q, total_alt)

  # DEBUG VISUAL: CÍRCULO VERMELHO
  roi_debug = roi_respostas.copy()
  for questao, alternativas in mapa_bolhas.items():
      for letra, (x, y) in alternativas.items():
          cv2.circle(roi_debug, (x, y), raio, (0, 0, 255), 2) 

  cv2.imwrite("debug_coordenadas.png", roi_debug)

  return {
      "prova": dados_prova['id_prova'],
      "status": "Recorte da prova com debug gerado."
  }