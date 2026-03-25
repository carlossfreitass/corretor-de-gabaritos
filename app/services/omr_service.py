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
  edged = cv2.Canny(gray, 75, 200)
  contornos, _ = cv2.findContours(edged, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
  anchors = []

  for c in contornos:
    perimetro = cv2.arcLength(c, True)
    approx = cv2.approxPolyDP(c, 0.02 * perimetro, True)

    # FILTRO PARA OS ANCHORS DA CAIXA
    if len(approx) == 4:
      area = cv2.contourArea(c)
      if 800 < area < 2500:
        anchors.append(approx)
  
  if len(anchors) >= 4:
    todos_pontos = np.concatenate(anchors).reshape(-1, 2)
    x_min, y_min = np.min(todos_pontos, axis=0)
    x_max, y_max = np.max(todos_pontos, axis=0)

    # RECORTE DA IMAGEM
    return imagem[int(y_min):int(y_max), int(x_min):int(x_max)]
  
  return None

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
  roi_respostas = isolar_caixa_respostas(folha_alinhada)
  if roi_respostas is None:
    return {"erro": "Não foi possível localizar os delimitadores da grade de respostas."}
  
  return {
    "prova_identificada": dados_prova['id_prova'],
    "total_questoes": dados_prova['total_questoes'],
    "alternativas": dados_prova['alternativas']
  }