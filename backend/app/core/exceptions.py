class HTTPValueError(ValueError):
    """HTTP 정보를 포함한 ValueError"""
    def __init__(self, detail: str, status_code: int):
        self.detail = detail
        self.status_code = status_code
        super().__init__(detail)