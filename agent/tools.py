"""
tools.py
Custom tools given to the coder agent. Kept deliberately narrow: write
the generated file, and run the existing compile-check logic. No
general shell/file access -- the agent's capability surface matches its
actual job (write code, verify it compiles), not arbitrary execution.
This is the enforcement mechanism for the spec's "cannot self-certify"
rule: compile_check is the only way to get a PASS/FAIL signal, and it's
real subprocess output, not the agent's own claim.
"""
from pathlib import Path

from claude_agent_sdk import tool

from compile_check import compile_arduino_sketch, check_python_syntax

OUTPUT_DIR = Path(__file__).parent.parent / "generated"


@tool(
    "write_code",
    "Write generated code to a file in the generated/ output directory. "
    "Overwrites if the file already exists (expected during the retry "
    "loop after a failed compile_check).",
    {"filename": str, "code": str},
)
async def write_code(args: dict) -> dict:
    OUTPUT_DIR.mkdir(exist_ok=True)
    path = OUTPUT_DIR / args["filename"]
    path.write_text(args["code"], encoding="utf-8")
    return {"content": [{"type": "text", "text": f"Wrote {path}"}]}


@tool(
    "compile_check",
    "Run a headless compile/syntax check on a previously-written file "
    "(no hardware involved). toolchain must be 'arduino-cli' (compiles "
    "against the given fqbn) or 'python' (syntax check only). Returns "
    "PASS or FAIL plus the raw compiler/interpreter output -- use that "
    "output to fix the code and retry. This is the only source of truth "
    "for whether generated code works; never report success without a "
    "PASS from this tool.",
    {"filename": str, "toolchain": str, "fqbn": str},
)
async def run_compile_check(args: dict) -> dict:
    path = OUTPUT_DIR / args["filename"]
    if not path.exists():
        return {
            "content": [
                {"type": "text", "text": f"ERROR: {path} does not exist -- call write_code first."}
            ]
        }
    code = path.read_text(encoding="utf-8")

    toolchain = args["toolchain"]
    if toolchain == "arduino-cli":
        success, output = compile_arduino_sketch(code, args.get("fqbn", ""))
    elif toolchain == "python":
        success, output = check_python_syntax(code)
    else:
        return {"content": [{"type": "text", "text": f"ERROR: unknown toolchain '{toolchain}'"}]}

    status = "PASS" if success else "FAIL"
    return {"content": [{"type": "text", "text": f"{status}\n{output}"}]}
