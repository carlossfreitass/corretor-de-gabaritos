![Corretor de Gabaritos](https://i.ibb.co/Gfpq1wMQ/github-header.png)
<p align="center">
  <a href="https://skillicons.dev">
    <img src="https://skillicons.dev/icons?i=python,flask,opencv,postman,docker" />
  </a>
</p>

## Objetivo
Desenvolver um microsserviço em Python/Flask para geração e correção automática de folhas de respostas (OMR — Optical Mark Recognition) via processamento de imagem com OpenCV, sem necessidade de GPU.

---

## Sumário
 
- [Tecnologias](#tecnologias)
- [Estrutura do projeto](#estrutura-do-projeto)
- [Instalação local](#instalação-local)
- [Executando com Docker](#executando-com-docker)
- [Rotas da API](#rotas-da-api)
  - [POST /gerar-gabarito](#post-gerar-gabarito)
  - [POST /corrigir-gabarito](#post-corrigir-gabarito)
- [Exemplos de uso](#exemplos-de-uso)
 
---
 
## Tecnologias
 
| Tecnologia | Função |
|---|---|
| Python 3.11 | Linguagem principal |
| Flask | Framework web |
| OpenCV | Processamento de imagem e OMR |
| Pillow | Geração da folha de respostas |
| pyzbar | Leitura de QR Code |
| Docker | Containerização |
 
---
 
## Estrutura do projeto
 
```
├── app/
│   ├── main.py               → Entry point do Flask
│   ├── fonts/
│   │   └── arialbd.ttf       → Fonte utilizada na geração do gabarito
│   ├── services/
│   │   ├── gabarito_service.py  → Geração da folha de respostas
│   │   ├── omr_service.py       → Processamento de imagem e OMR
│   │   └── resultado_service.py → Correção e cálculo de nota
│   └── utils/
│       └── image_utils.py       → Helpers de pré-processamento
├── examples/                 → Gabaritos gerados
├── Dockerfile
├── docker-compose.yml
├── requirements.txt
└── README.md
```
 
> **Dockerfile e docker-compose.yml ficam na raiz do projeto**, no mesmo nível de `requirements.txt` e da pasta `app/`. O Docker Compose usa o `Dockerfile` da raiz para buildar a imagem e monta `app/` dentro do container como `/app`.
 
---
 
## Instalação local
 
**Pré-requisitos:** Python 3.11+, `libzbar0` instalado no sistema.
 
```bash
# Linux
sudo apt-get install libzbar0 libgl1
 
# macOS
brew install zbar
```
 
```bash
# Clone o repositório e entre na pasta
git clone <url-do-repositorio>
cd <nome-do-projeto>
 
# Crie e ative o ambiente virtual
python -m venv venv
source venv/bin/activate       # Linux/macOS
venv\Scripts\activate          # Windows
 
# Instale as dependências
pip install -r requirements.txt
 
# Execute
python app/main.py
```
 
O serviço estará disponível em `http://localhost:5000`.
 
---
 
## Executando com Docker
 
```bash
# Suba o serviço (primeira vez faz o build automaticamente)
docker-compose up --build
 
# Execuções seguintes (sem rebuild)
docker-compose up
 
# Parar o serviço
docker-compose down
```
 
O serviço estará disponível em `http://localhost:5000`.
 
---
 
## Rotas da API
 
### POST /gerar-gabarito
 
Gera uma folha de respostas em PNG com QR Code embutido. 

**Content-Type:** `application/json`
 
**Corpo da requisição:**
 
```json
{
  "nome_prova": "Desenvolvimento de Jogos",
  "id_prova": "DJ-2026",
  "total_questoes": 20,
  "alternativas": 5
}
```
 
| Campo | Tipo | Obrigatório | Descrição |
|---|---|---|---|
| `nome_prova` | string | sim | Título exibido no topo da folha |
| `id_prova` | string | sim | Identificador único da prova |
| `total_questoes` | integer | sim | Número de questões (máx. recomendado: 50) |
| `alternativas` | integer | sim | Número de alternativas por questão (2–5) |
 
**Resposta:**
 
```json
{
  "mensagem": "gabarito gerado",
  "caminho": "../examples/DJ-2026.png"
}
```
 
---
 
### POST /corrigir-gabarito
 
Recebe uma imagem da folha preenchida e retorna as respostas detectadas junto com a correção completa.
 
**Content-Type:** `multipart/form-data`
 
| Campo | Tipo | Obrigatório | Descrição |
|---|---|---|---|
| `file` | File | sim | Imagem da folha preenchida (PNG ou JPG) |
| `gabarito_oficial` | Text (JSON) | sim | Gabarito de referência para correção |
| `valor_prova` | Text (float) | não | Valor máximo da prova. Padrão: `10.0` |
| `pesos` | Text (JSON) | não | Valor em pontos de cada questão. Se omitido, divide `valor_prova` igualmente |
 
> **Nota sobre pesos:** cada valor representa quantos pontos aquela questão vale. A soma de todos os pesos deve ser igual a `valor_prova`.
 
**Resposta:**
 
```json
{
  "id_prova": "DJ-2026",
  "resumo": {
    "nota": 7.5,
    "valor_prova": 10.0,
    "total_acertos": 7,
    "total_erros": 2,
    "total_brancos": 1,
    "total_rasuras": 0,
    "total_questoes": 10
  },
  "detalhado": [
    {
      "numero": "Q01",
      "status": "CORRETO",
      "marcado_pelo_aluno": "A",
      "resposta_correta": "A",
      "valor_questao": 2.0
    },
    {
      "numero": "Q02",
      "status": "INCORRETO",
      "marcado_pelo_aluno": "B",
      "resposta_correta": "C",
      "valor_questao": 1.0
    },
    {
      "numero": "Q03",
      "status": "VAZIO",
      "marcado_pelo_aluno": "BRANCO",
      "resposta_correta": "B",
      "valor_questao": 1.0
    },
    {
      "numero": "Q04",
      "status": "RASURA",
      "marcado_pelo_aluno": "RASURA",
      "resposta_correta": "E",
      "valor_questao": 1.0
    }
  ]
}
```
 
| Status | Significado |
|---|---|
| `CORRETO` | Alternativa marcada bate com o gabarito |
| `INCORRETO` | Alternativa marcada é diferente do gabarito |
| `VAZIO` | Nenhuma alternativa foi marcada |
| `RASURA` | Mais de uma alternativa foi marcada |
 
---
 
## Exemplos de uso

### Gerar gabarito (Postman)

- Método: `POST`
- URL: `http://localhost:5000/gerar-gabarito`
- Aba **Body → raw → JSON**
```json
{
  "nome_prova": "Desenvolvimento de Jogos",
  "id_prova": "DJ-2026",
  "total_questoes": 10,
  "alternativas": 5
}
```

### Corrigir gabarito (Postman — form-data)

- URL: `http://localhost:5000/corrigir-gabarito`
 
| Key | Value | Type |
|---|---|---|
| `file` | _(selecione o arquivo .png)_ | File |
| `gabarito_oficial` | `{"Q01":"A","Q02":"C","Q03":"B","Q04":"E","Q05":"A","Q06":"D","Q07":"B","Q08":"C","Q09":"E","Q10":"A"}` | Text |
| `valor_prova` | `10.0` | Text |
| `pesos` | `{"Q01":2,"Q02":1,"Q03":1,"Q04":1,"Q05":1,"Q06":1,"Q07":1,"Q08":1,"Q09":0.5,"Q10":0.5}` | Text |