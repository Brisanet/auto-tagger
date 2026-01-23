# auto-tagger
Auto-tag é uma implementação feita em Python para automatização de tags no GitHub. <br><br>
Exemplo clássico: <br><br>
Ao fazer pull request, é preciso subir uma tag, e a tag pode ser uma trigger para gerar uma nova att, <br>
geralmente ocorre de forma manual, mas com o auto-tagger é feito de forma automatizada via Python <br> 
junto à API do GitHub. A tag deve seguir o padrão v0.0.0. Major, minor, patch. <br><br>

# Importante
É necessário liberar a permissão para o PAT de Contents (read e write).

> Para utilizar o auto-tagger deve haver uma tag já criada anteriormente, pode ser qualquer versão, se não tiver, crie a **v0.0.0**. <br>

<br> É preciso criar Personal Token para autenticação: <br>
1. Crie o personal token, por exemplo (classic), e armazene o segredo. <br>
- Pode ser qualquer tipo de token, será usado somente para autenticação. <br><br>

2. Crie um segredo com o token anteriormente criado, em **Secrets and variables** > Actions > Repository secrets <br>
 - Com o nome: **AUTO_TAG_TOKEN** e o personal token como segredo. <br><br>

## Workflow
Adicione no workflow GitHub ou crie um com o seguinte código abaixo: <br><br>

```
jobs:
  auto-tagger:
    runs-on: ubuntu-latest
    name: 'Checkout auto-tagger repos'
    steps:
      - name: Check out code
        uses: actions/checkout@v4
        with:
          repository: 'Brisanet/auto-tagger'

      - name: Set up Python 3.13
        uses: actions/setup-python@v5
        with:
          python-version: 3.13

      - name: Install dependencies
        working-directory: ./auto_tagger
        run: pip install -r requirements.txt

      - name: Auto tagger
        working-directory: ./
        run: python3 deploy_tag.py --repo "${{ github.repository }}"
        env:
          AUTO_TAG_TOKEN: ${{secrets.AUTO_TAG_TOKEN}}
```

