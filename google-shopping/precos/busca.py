"""Pesquisa no Google Shopping e extração das ofertas."""

import re
import time
import unicodedata
from urllib.parse import parse_qs, quote_plus, urlparse

from .config import ESPERA_MAX_CAPTCHA_SEG, MOSTRAR_NAVEGADOR
from .modelos import Oferta, ResultadoBusca
from .template import Status

URL_BUSCA = "https://www.google.com/search?tbm=shop&hl=pt-BR&gl=br&tbs=p_ord:p&q={termo}"
USER_AGENT = ("Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
              "(KHTML, like Gecko) Chrome/130.0.0.0 Safari/537.36")
TIMEOUT_CARREGAMENTO_MS = 45_000
ESPERA_RENDERIZACAO_MS  = 2_500
ESPERA_ROLAGEM_MS       = 1_500
SINAIS_DE_CAPTCHA = ("unusual traffic", "tráfego incomum", "recaptcha")
BOTOES_COOKIES = ("Aceitar tudo", "Accept all")
PROPORCAO_MINIMA_PALAVRAS = 0.6
INTERVALO_CHECAGEM_CAPTCHA_SEG = 3


class BloqueioDoGoogle(Exception):
    """O Google exibiu captcha / página de tráfego incomum."""


# ---------- Regras de texto (puras, fáceis de testar) ----------

def extrair_preco(texto):
    """'R$ 1.234,56' -> 1234.56; None se não houver preço."""
    achado = re.search(r"R\$\s*(\d{1,3}(?:\.\d{3})*|\d+)(?:,(\d{2}))?", texto or "")
    if not achado:
        return None
    reais, centavos = achado.group(1).replace(".", ""), achado.group(2) or "00"
    return float(f"{reais}.{centavos}")


def _sem_acentos(texto):
    decomposto = unicodedata.normalize("NFKD", texto.lower())
    return "".join(c for c in decomposto if not unicodedata.combining(c))


def titulo_corresponde_ao_item(nome_item, titulo):
    """True se o título contém a maioria das palavras relevantes do item."""
    palavras = [p for p in re.findall(r"\w+", _sem_acentos(nome_item)) if len(p) > 2]
    if not palavras:
        return True
    titulo_normalizado = _sem_acentos(titulo)
    encontradas = sum(p in titulo_normalizado for p in palavras)
    return encontradas / len(palavras) >= PROPORCAO_MINIMA_PALAVRAS


def link_final(href):
    """Troca o redirecionamento do Google (/url?q=...) pelo link direto da loja."""
    if not href:
        return ""
    if href.startswith("/"):
        href = "https://www.google.com" + href
    url = urlparse(href)
    parametros = parse_qs(url.query)
    if url.path == "/url" and ("q" in parametros or "url" in parametros):
        return (parametros.get("q") or parametros.get("url"))[0]
    return href


def link_de_busca(titulo):
    return URL_BUSCA.format(termo=quote_plus(titulo))


# ---------- Leitura da página ----------

JS_EXTRAIR_CARDS = r"""
() => {
  const precoRe = /R\$\s?\d[\d.]*(,\d{2})?/;
  const ruido = /^(R\$|frete|entrega|\d+([.,]\d+)?\s*(\(|$)|avalia|compar|mais lojas|loja(s)? (oficial|verificada)|usado|\+|em até|à vista|ver |patrocinad|anúncio|oferta|desconto|-?\d+%)/i;
  const visto = new Set(), out = [];
  const folhas = [...document.querySelectorAll('span,div,b,strong')]
    .filter(e => e.children.length === 0 && precoRe.test(e.textContent) && e.textContent.length < 40);
  for (const f of folhas) {
    if (getComputedStyle(f).textDecorationLine.includes('line-through')) continue; // preço antigo riscado
    let card = f.parentElement;
    for (let i = 0; i < 10 && card; i++, card = card.parentElement) {
      const linhas = card.innerText.split('\n').map(s => s.trim()).filter(Boolean);
      if (linhas.length >= 3 && (card.matches('a[href]') || card.querySelector('a[href]') || card.closest('a[href]'))) break;
    }
    if (!card || visto.has(card)) continue;
    // ignora containers grandes (lista inteira) – um card tem só 1 ou 2 preços
    const precos = card.innerText.match(new RegExp(precoRe.source, 'g')) || [];
    if (precos.length > 3) continue;
    visto.add(card);
    const linhas = card.innerText.split('\n').map(s => s.trim()).filter(Boolean);
    const iPreco = linhas.findIndex(l => l.includes(f.textContent.trim()));
    const candidatos = linhas.filter(l => !precoRe.test(l) && !ruido.test(l));
    const titulo = candidatos.slice().sort((a, b) => b.length - a.length)[0] || '';
    let loja = '';
    for (const l of linhas.slice(iPreco + 1)) {
      if (!precoRe.test(l) && !ruido.test(l) && l !== titulo && l.length <= 40) { loja = l; break; }
    }
    const links = [...card.querySelectorAll('a[href]')].map(a => a.href);
    if (card.closest('a[href]')) links.unshift(card.closest('a[href]').href);
    const externo = links.find(h => !/google\./.test(new URL(h, location.href).hostname));
    out.push({titulo, preco_txt: f.textContent.trim(), loja, link: externo || links[0] || ''});
  }
  return out;
}
"""


def aceitar_cookies(pagina):
    for texto in BOTOES_COOKIES:
        botao = pagina.get_by_role("button", name=texto)
        if botao.count():
            botao.first.click()
            return


def pagina_tem_captcha(pagina):
    html = pagina.content().lower()
    return "/sorry/" in pagina.url or any(sinal in html for sinal in SINAIS_DE_CAPTCHA)


def aguardar_captcha_resolvido(pagina):
    """Com o navegador visível, espera a pessoa resolver o captcha na janela."""
    print(f"   >> Captcha! Resolva na janela do Chrome (até {ESPERA_MAX_CAPTCHA_SEG // 60} min)...")
    limite = time.monotonic() + ESPERA_MAX_CAPTCHA_SEG
    while time.monotonic() < limite:
        time.sleep(INTERVALO_CHECAGEM_CAPTCHA_SEG)
        if not pagina_tem_captcha(pagina):
            print("   >> Captcha resolvido, continuando.")
            return
    raise BloqueioDoGoogle()


def tratar_captcha(pagina, nome_item):
    if not pagina_tem_captcha(pagina):
        return
    if not MOSTRAR_NAVEGADOR:
        raise BloqueioDoGoogle()
    aguardar_captcha_resolvido(pagina)
    abrir_busca(pagina, nome_item)  # depois do captcha o Google nem sempre volta à busca
    if pagina_tem_captcha(pagina):
        raise BloqueioDoGoogle()


def abrir_busca(pagina, nome_item):
    pagina.goto(URL_BUSCA.format(termo=quote_plus(nome_item)),
                wait_until="domcontentloaded", timeout=TIMEOUT_CARREGAMENTO_MS)
    aceitar_cookies(pagina)
    pagina.wait_for_timeout(ESPERA_RENDERIZACAO_MS)


def carregar_resultados(pagina, nome_item):
    abrir_busca(pagina, nome_item)
    tratar_captcha(pagina, nome_item)
    pagina.mouse.wheel(0, 3000)  # força o carregamento de mais cards
    pagina.wait_for_timeout(ESPERA_ROLAGEM_MS)


def cards_para_ofertas(cards, nome_item, filtrar_titulo):
    """Converte os cards brutos em Ofertas válidas, sem duplicatas."""
    ofertas, vistas = [], set()
    for card in cards:
        preco = extrair_preco(card["preco_txt"])
        if preco is None or not card["titulo"]:
            continue
        if filtrar_titulo and not titulo_corresponde_ao_item(nome_item, card["titulo"]):
            continue
        chave = (card["titulo"].lower(), card["loja"].lower(), preco)
        if chave in vistas:
            continue
        vistas.add(chave)
        ofertas.append(Oferta(titulo=card["titulo"], preco=preco, loja=card["loja"],
                              link=link_final(card["link"]) or link_de_busca(card["titulo"])))
    return ofertas


def mais_baratas(ofertas, quantidade):
    return sorted(ofertas, key=lambda o: o.preco)[:quantidade]


def buscar_item(pagina, item, quantidade, filtrar_titulo):
    """Pesquisa um item. Só propaga erro em caso de bloqueio do Google."""
    try:
        carregar_resultados(pagina, item.nome)
        cards = pagina.evaluate(JS_EXTRAIR_CARDS)
    except BloqueioDoGoogle:
        raise
    except Exception as erro:
        return ResultadoBusca(item, f"{Status.ERRO}: {type(erro).__name__}")

    ofertas = mais_baratas(cards_para_ofertas(cards, item.nome, filtrar_titulo), quantidade)
    return ResultadoBusca(item, Status.OK if ofertas else Status.SEM_RESULTADO, ofertas)
