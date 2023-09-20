class VerificationFailedError(Exception):
    def __init__(self, status_code: int, error: str, details: str = None):
        self.status_code = status_code
        self.error = error
        self.details = details

    def __str__(self):
        return f"Verification failed with status code {self.status_code} and error type {self.error}"
