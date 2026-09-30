class CompilerError(Exception):
    def __init__(self, message, error_type, extra=None):
        super().__init__(message)
        self.message = message
        self.error_type = error_type
        self.extra = extra or {}


class LexicalError(CompilerError):
    def __init__(self, message, extra=None):
        super().__init__(message, "LEXICAL_ERROR", extra)


class KPCLSyntaxError(CompilerError):
    def __init__(self, message, extra=None):
        super().__init__(message, "SYNTAX_ERROR", extra)


class SemanticError(CompilerError):
    def __init__(self, message, extra=None):
        super().__init__(message, "SEMANTIC_ERROR", extra)
