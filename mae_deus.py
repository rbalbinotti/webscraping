import requests
from bs4 import BeautifulSoup
import pandas as pd
import time
import html

BASE = "https://centroclinicomaededeus.com.br"
API  = f"{BASE}/wp-json/wp/v2/medicos_e_medicas"
HEADERS = {"User-Agent": "Mozilla/5.0 (compatible; Scraper/1.0)"}

def listar_todos_medicos_via_api():
    """Percorre todas as páginas da API REST e retorna a lista de médicos."""
    medicos = []
    page = 1
    while True:
        url = f"{API}?per_page=100&page={page}&_fields=id,slug,link,title"
        resp = requests.get(url, headers=HEADERS, timeout=30)
        if resp.status_code == 400:  # página além do total
            break
        resp.raise_for_status()
        dados = resp.json()
        if not dados:
            break
        medicos.extend(dados)
        total_pages = int(resp.headers.get("X-WP-TotalPages", page))
        print(f"  Página {page}/{total_pages} — {len(dados)} médicos")
        if page >= total_pages:
            break
        page += 1
        time.sleep(0.5)
    return medicos

def extrair_contatos(url_medico):
    """Extrai contatos da página individual de um médico."""
    resp = requests.get(url_medico, headers=HEADERS, timeout=30)
    soup = BeautifulSoup(resp.text, "html.parser")

    nome_tag = soup.select_one("h1.elementor-heading-title")
    nome = nome_tag.get_text(strip=True) if nome_tag else ""

    def decode_cfemail(cfemail: str) -> str:
        if not cfemail or len(cfemail) < 4:
            return ""
        key = int(cfemail[:2], 16)
        return "".join(
            chr(int(cfemail[i:i+2], 16) ^ key)
            for i in range(2, len(cfemail), 2)
    )

    def texto_por_icone(classe_icone):
        icone = soup.select_one(f"i.{classe_icone.replace(' ', '.')}")
        if not icone:
            return ""
        li = icone.find_parent("li")
        if not li:
            return ""
        texto_tag = li.select_one(".elementor-icon-list-text")
        if not texto_tag:
            return ""

        # Caso 1: e-mail protegido pelo Cloudflare
        cf = texto_tag.select_one("a.__cf_email__[data-cfemail]")
        if cf:
            return decode_cfemail(cf["data-cfemail"])

        # Caso 2: texto normal
        texto = texto_tag.get_text(strip=True)
        if "email" in texto.lower() and "protected" in texto.lower():
            return ""
        return texto

    telefone = texto_por_icone("xi xi-phone-6")
    whatsapp = texto_por_icone("icon icon-whatsapp-1")
    email    = texto_por_icone("icon icon-email")

    def campo_por_strong(rotulo):
        for h2 in soup.select("h2.elementor-heading-title"):
            strong = h2.find("strong")
            if strong and rotulo.lower() in strong.get_text(strip=True).lower():
                return h2.get_text(strip=True).replace(strong.get_text(strip=True), "").strip()
        return ""

    crm           = campo_por_strong("CRM")
    sala          = campo_por_strong("Sala")
    especialidade = campo_por_strong("Especialidade")

    convenios = ""
    for div in soup.select("div.elementor-widget-text-editor"):
        strong = div.find("strong")
        if strong and "convênio" in strong.get_text(strip=True).lower():
            convenios = div.get_text(strip=True).replace(strong.get_text(strip=True), "").strip()
            break

    return {
        "Nome": nome, "CRM": crm, "Sala": sala,
        "Especialidade": especialidade, "Convênios": convenios,
        "Telefone": telefone, "WhatsApp": whatsapp,
        "E-mail": email, "URL": url_medico,
    }

if __name__ == "__main__":
    print("Coletando lista de médicos via API REST...")
    medicos = listar_todos_medicos_via_api()
    print(f"Total: {len(medicos)} médicos\n")

    resultados = []
    for i, m in enumerate(medicos, 1):
        url = m["link"]
        nome_api = html.unescape(m["title"]["rendered"])
        print(f"[{i}/{len(medicos)}] {nome_api}")
        try:
            dados = extrair_contatos(url)
            dados["ID"] = m["id"]
            dados["Slug"] = m["slug"]
            resultados.append(dados)
        except Exception as e:
            print(f"  ⚠️ Erro: {e}")
        time.sleep(1)

    df = pd.DataFrame(resultados)
    df.to_csv("medicos_contatos.csv", index=False, encoding="utf-8-sig")
    print(f"\n✅ {len(df)} registros salvos em medicos_contatos.csv")
    print(df.head(10).to_string(index=False))