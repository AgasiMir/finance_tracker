from fastapi import Request


def wallet_key_builder(
    func,
    namespace: str = "",
    request: Request | None = None,
    response=None,
    *args,
    **kwargs,
):
    """
    Генерирует предсказуемый ключ вида:
    fastapi-cache:wallets:wallet:<user.id>:<wallet_name>
    """

    data = kwargs.get("kwargs")
    user = data.get("current_user")
    wallet_name = data.get("wallet_name")

    return f"{namespace}:wallet:{user.id}:{wallet_name}"
