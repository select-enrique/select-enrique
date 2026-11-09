"""Dados que circulam entre a planilha e a busca."""

from dataclasses import dataclass, field


@dataclass(frozen=True)
class Item:
    """Produto da aba Entrega que será pesquisado."""
    item_id: str
    nome: str
    loja_shopee: str
    preco_shopee: object  # número quando possível


@dataclass(frozen=True)
class Oferta:
    """Uma oferta encontrada no Google Shopping."""
    titulo: str
    preco: float
    loja: str
    link: str


@dataclass
class ResultadoBusca:
    item: Item
    status: str
    ofertas: list = field(default_factory=list)
