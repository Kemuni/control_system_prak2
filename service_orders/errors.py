
class ApiException(Exception):
    """Кастомная ошибка для нашего API"""
    def __init__(self, code: str, message: str):
        self.code = code
        self.message = message
