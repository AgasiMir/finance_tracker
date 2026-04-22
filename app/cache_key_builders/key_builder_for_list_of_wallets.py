import hashlib
from fastapi import Request


def key_builder_for_list_of_wallets(
    func,
    namespace: str = "",
    request: Request | None = None,
    response=None,
    *args,
    **kwargs,
):
    """
    Генерирует предсказуемый ключ вида:
    "all-wallets:<user_id>:<cache_key>"
    """

    cache_kw = {}
    data = kwargs.get("kwargs")
    user = data.get("current_user")

    for key, value in data.items():
        if key not in ["db", "current_user"]:
            cache_kw[key] = value

    cache_kw["user_id"] = user.id
    cache_kw["user_email"] = user.email

    cache_key = hashlib.md5(  # noqa: S324
        f"{func.__module__}:{func.__name__}:{cache_kw}".encode()
    ).hexdigest()

    return f"all-wallets:{user.id}:{cache_key}"
