"""Erros de domínio."""


class RegraNegocio(Exception):
    """Violação de uma regra de negócio (mostrada ao usuário sem stack trace)."""
