class VerificationFailedError(Exception):
    def __init__(self, status_code: int, error_type: str):
        self.status_code = status_code
        self.error_type = error_type

    def __str__(self):
        return f"Verification failed with status code {self.status_code} and error type {self.error_type}"
