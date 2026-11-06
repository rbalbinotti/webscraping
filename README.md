# README — Scraper de Médicos (Centro Clínico Mãe de Deus)

## 📋 Descrição

Script em Python para coletar informações de contato dos médicos e médicas cadastrados no site do **Centro Clínico Mãe de Deus** (https://centroclinicomaededeus.com.br), utilizando a API REST do WordPress e técnicas de web scraping com BeautifulSoup.

O resultado é exportado para um arquivo CSV (`medicos_contatos.csv`) contendo nome, CRM, sala, especialidade, convênios, telefone, WhatsApp, e-mail e URL do perfil de cada profissional.

---

## ⚙️ Como funciona

O script executa duas etapas principais:

1. **Listagem via API REST do WordPress**
   - Consome o endpoint `/wp-json/wp/v2/medicos_e_medicas`
   - Pagina automaticamente (100 registros por página) até esgotar os resultados
   - Respeita o cabeçalho `X-WP-TotalPages` retornado pela API

2. **Extração de dados de cada perfil**
   - Para cada médico listado, acessa a URL individual do perfil
   - Extrai os dados com `BeautifulSoup`, localizando elementos por classes CSS e ícones (telefone, WhatsApp, e-mail)
   - Trata e-mails protegidos pelo Cloudflare (`__cf_email__`) decodificando o atributo `data-cfemail`
   - Coleta campos rotulados por `<strong>` (CRM, Sala, Especialidade, Convênios)

---

## 🛠️ Requisitos

- **Python 3.8+**
- Bibliotecas:
  - `requests`
  - `beautifulsoup4`
  - `pandas`

### Instalação

```bash
pip install requests beautifulsoup4 pandas
```

---

## 🚀 Uso

Execute o script diretamente:

```bash
python scraper_medicos.py
```

O script exibirá o progresso no terminal (página atual da API e cada médico processado) e, ao final, salvará o arquivo `medicos_contatos.csv` no diretório de execução.

### Saída esperada

```
Coletando lista de médicos via API REST...
  Página 1/3 — 100 médicos
  Página 2/3 — 100 médicos
  ...
Total: 245 médicos

[1/245] Dr. Fulano de Tal
[2/245] Dra. Ciclana de Tal
...

✅ 245 registros salvos em medicos_contatos.csv
```

### Colunas do CSV

| Coluna | Descrição |
|---|---|
| `Nome` | Nome do médico (extraído do `<h1>` do perfil) |
| `CRM` | Número do CRM |
| `Sala` | Sala de atendimento |
| `Especialidade` | Especialidade médica |
| `Convênios` | Convênios aceitos |
| `Telefone` | Telefone de contato |
| `WhatsApp` | Número de WhatsApp |
| `E-mail` | E-mail (decodificado se protegido pelo Cloudflare) |
| `URL` | Link do perfil no site |
| `ID` | ID do post na API do WordPress |
| `Slug` | Slug do perfil na API |

O arquivo é salvo em **UTF-8 com BOM** (`utf-8-sig`) para compatibilidade com o Excel.

---

## 🧩 Estrutura do código

| Função | Responsabilidade |
|---|---|
| `listar_todos_medicos_via_api()` | Percorre todas as páginas da API REST e retorna a lista de médicos |
| `extrair_contatos(url_medico)` | Extrai os dados de contato de uma página individual de médico |
| `decode_cfemail(cfemail)` | Decodifica e-mails ofuscados pelo Cloudflare |
| `texto_por_icone(classe_icone)` | Localiza o texto associado a um ícone (telefone, WhatsApp, e-mail) |
| `campo_por_strong(rotulo)` | Localiza campos rotulados por `<strong>` (CRM, Sala, Especialidade) |
| `__main__` | Orquestra a coleta, exporta o CSV e exibe o resumo |

---

## ⚠️ Observações importantes

- **Rate limiting:** O script aguarda `1s` entre requisições de perfis e `0.5s` entre páginas da API para não sobrecarregar o servidor. Ajuste com cautela.
- **User-Agent:** Definido no cabeçalho `HEADERS` como `Mozilla/5.0 (compatible; Scraper/1.0)`. Modifique se necessário.
- **E-mails protegidos:** O Cloudflare ofusca e-mails em atributos `data-cfemail`. O script os decodifica automaticamente.
- **Falhas parciais:** Erros em um perfil individual são registrados no console (`⚠️ Erro: ...`) sem interromper a execução — o médico é simplesmente ignorado no CSV final.
- **Uso responsável:** Utilize o script em conformidade com os termos de uso do site e a LGPD. Os dados coletados são de profissionais expostos publicamente no site, mas trate-os com responsabilidade.

---

## 🔧 Personalização

- **Outro endpoint:** Altere a constante `API` para apontar para outro tipo de post do WordPress.
- **Mais campos:** Adicione novas funções de extração no dicionário retornado por `extrair_contatos`.
- **Outro formato de saída:** Substitua `df.to_csv(...)` por `df.to_excel(...)` (requer `openpyxl`) ou `df.to_json(...)`.

---

## 📄 Licença

Script fornecido para fins educacionais e de pesquisa. Verifique a política de uso de dados do site antes de redistribuir os resultados.