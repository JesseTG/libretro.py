
class UnsupportedEnvCall(Exception):
    def __init__(self, message):
        super().__init__(message)


__all__ = [
    'UnsupportedEnvCall',
]
