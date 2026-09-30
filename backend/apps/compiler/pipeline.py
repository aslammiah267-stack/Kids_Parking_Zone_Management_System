"""KPCL compiler pipeline: Input → Lexer → Parser → Semantic → IR → Executor."""

from .errors import CompilerError, LexicalError, KPCLSyntaxError, SemanticError
from .executor import Executor
from .intermediate_code import generate
from .lexer import tokenize
from .parser import parse
from .semantic import analyze


PIPELINE_STAGES = [
    "INPUT",
    "LEXICAL_ANALYSIS",
    "TOKENS",
    "SYNTAX_ANALYSIS",
    "SEMANTIC_ANALYSIS",
    "INTERMEDIATE_CODE",
    "EXECUTION",
    "OUTPUT",
]


def compile_command(command: str, execute=True):
    """Run one KPCL command through every compiler phase."""
    stages_completed = ["INPUT"]
    tokens = []
    ast = None
    semantic_ast = None
    intermediate_code = []
    result = None

    response = {
        "success": False,
        "command": command,
        "tokens": [],
        "syntax_valid": False,
        "semantic_valid": False,
        "intermediate_code": [],
        "ast": None,
        "stages_completed": stages_completed,
        "pipeline": PIPELINE_STAGES,
    }

    try:
        tokens = tokenize(command)
        stages_completed.extend(["LEXICAL_ANALYSIS", "TOKENS"])
        response["tokens"] = [token.to_dict() for token in tokens]

        ast = parse(tokens)
        stages_completed.append("SYNTAX_ANALYSIS")
        response["syntax_valid"] = True
        response["ast"] = ast

        semantic_ast = analyze(ast)
        stages_completed.append("SEMANTIC_ANALYSIS")
        response["semantic_valid"] = True
        response["ast"] = semantic_ast

        intermediate_code = generate(semantic_ast)
        stages_completed.append("INTERMEDIATE_CODE")
        response["intermediate_code"] = intermediate_code

        if execute:
            result = Executor().execute(semantic_ast)
            stages_completed.extend(["EXECUTION", "OUTPUT"])
            response["result"] = result
        else:
            response["result"] = "Execution skipped."

        response["success"] = True
        response["stages_completed"] = stages_completed
        return response
    except CompilerError as exc:
        response["error_type"] = exc.error_type
        response["message"] = exc.message
        response["details"] = exc.extra
        response["stages_completed"] = stages_completed
        if isinstance(exc, LexicalError):
            response["tokens"] = [token.to_dict() for token in tokens]
        if isinstance(exc, KPCLSyntaxError):
            response["tokens"] = [token.to_dict() for token in tokens]
        if isinstance(exc, SemanticError):
            response["tokens"] = [token.to_dict() for token in tokens]
            response["syntax_valid"] = True
        return response


def compile_script(source: str, execute=True):
    """Execute multiple newline-separated KPCL commands sequentially."""
    lines = [line.strip() for line in (source or "").splitlines() if line.strip() and not line.strip().startswith("#")]
    if not lines:
        return {
            "success": False,
            "error_type": "SYNTAX_ERROR",
            "message": "Empty command.",
            "command": source,
            "tokens": [],
            "syntax_valid": False,
            "semantic_valid": False,
            "results": [],
        }

    if len(lines) == 1:
        return compile_command(lines[0], execute=execute)

    results = []
    overall_success = True
    for line in lines:
        item = compile_command(line, execute=execute)
        results.append(item)
        if not item.get("success"):
            overall_success = False
            break
    last = results[-1]
    return {
        "success": overall_success,
        "command": source,
        "tokens": last.get("tokens", []),
        "syntax_valid": last.get("syntax_valid", False),
        "semantic_valid": last.get("semantic_valid", False),
        "intermediate_code": last.get("intermediate_code", []),
        "result": last.get("result"),
        "results": results,
        "error_type": None if overall_success else last.get("error_type"),
        "message": None if overall_success else last.get("message"),
        "stages_completed": last.get("stages_completed", []),
        "pipeline": PIPELINE_STAGES,
    }
