async def dispatch(request, call_next):
    response = await call_next(request)
    # Добавляем заголовки для предотвращения кэширования браузером
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Pragma"] = "no-cache"
    response.headers["Expires"] = "0"
    return response
