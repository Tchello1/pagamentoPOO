#eu uso hash no cartão melhor que isso
def mascarar_dados(dado: str, mostrar_ultimos: int = 0) -> str:
    """Mascara dados sensíveis, mostrando apenas os últimos 'mostrar_ultimos' caracteres"""
    if not dado:
        return ""
    
    tamanho = len(dado)
    if tamanho <= mostrar_ultimos:
        return dado
    
    parte_mascarada = '*' * (tamanho - mostrar_ultimos)
    parte_visivel = dado[-mostrar_ultimos:] if mostrar_ultimos > 0 else ""
    
    return parte_mascarada + parte_visivel