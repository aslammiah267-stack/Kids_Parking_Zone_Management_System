"""KPCL Intermediate Code Generator.

After syntax and semantic analysis succeed, the compiler emits a machine-like
sequence of instructions. This is not executed directly by Python; the executor
interprets these instructions against Django services.
"""


def generate(ast):
    command_type = ast["type"]
    if command_type == "REGISTER_COMMAND":
        return [
            {"instruction": "LOAD", "operand": ast["identifier"]},
            {"instruction": "VALIDATE_UNIQUE", "operand": ast["identifier"]},
            {"instruction": "CREATE", "operand": ast["id_type"]},
            {"instruction": "UPDATE STATUS", "operand": None},
        ]
    if command_type == "PARK_COMMAND":
        return [
            {"instruction": "LOAD", "operand": ast["vehicle_id"]},
            {"instruction": "CHECK", "operand": ast["slot_id"]},
            {"instruction": "ASSIGN", "operand": f"{ast['vehicle_id']}, {ast['slot_id']}"},
            {"instruction": "UPDATE STATUS", "operand": None},
        ]
    if command_type == "ENTRY_COMMAND":
        return [
            {"instruction": "LOAD", "operand": ast["vehicle_id"]},
            {"instruction": "VERIFY_ASSIGNMENT", "operand": ast["vehicle_id"]},
            {"instruction": "START_TIMER", "operand": ast["vehicle_id"]},
            {"instruction": "UPDATE STATUS", "operand": None},
        ]
    if command_type == "EXIT_COMMAND":
        return [
            {"instruction": "LOAD", "operand": ast["vehicle_id"]},
            {"instruction": "CALCULATE DURATION", "operand": ast["vehicle_id"]},
            {"instruction": "CALCULATE FEE", "operand": ast["vehicle_id"]},
            {"instruction": "RELEASE SLOT", "operand": ast["vehicle_id"]},
            {"instruction": "UPDATE HISTORY", "operand": None},
        ]
    if command_type == "PAY_COMMAND":
        return [
            {"instruction": "LOAD", "operand": ast["vehicle_id"]},
            {"instruction": "LOAD_RECORD", "operand": ast.get("record_id")},
            {"instruction": "COLLECT_PAYMENT", "operand": ast["vehicle_id"]},
            {"instruction": "UPDATE STATUS", "operand": None},
        ]
    return [{"instruction": "NOP", "operand": None}]
