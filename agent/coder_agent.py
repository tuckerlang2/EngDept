"""
coder_agent.py
Headless entry point for the primary coder agent -- callable by an
orchestrator (or run standalone for testing) with no human in the loop
during execution. Implements the contract in docs/primary-coder-agent-spec.md.

Usage:
    python3 coder_agent.py path/to/spec.yaml

Exit code is 0 on STATUS: PASS, 1 otherwise (ESCALATE, FAIL_RETRY_EXCEEDED,
or an SDK-level error) -- a calling orchestrator can branch on the exit
code alone if it just needs pass/fail, or parse the printed STATUS block
for the detail (the question to escalate, or the last compile error).

NOT YET RUN against the real SDK/CLI -- this is a first-pass scaffold.
Before relying on it: confirm `claude-agent-sdk` + the Claude Code CLI
it shells out to are both installed and authenticated, and run it
against a known-simple spec (e.g. the Arduino Uno PIR+LED case from the
old repo's Session 2) to validate the whole loop end to end.
"""
import asyncio
import sys
from pathlib import Path

import yaml
from claude_agent_sdk import (
    AssistantMessage,
    ClaudeAgentOptions,
    ClaudeSDKClient,
    ClaudeSDKError,
    TextBlock,
    create_sdk_mcp_server,
)

from hardware_lookup import get_board_meta, get_reference_text
from spec_schema import ComponentSpec, ProjectSpec
from tools import run_compile_check, write_code

MAX_RETRIES = 3


def load_spec(spec_path: Path) -> ProjectSpec:
    raw = yaml.safe_load(spec_path.read_text())
    components = [ComponentSpec(**c) for c in raw.get("components", [])]
    return ProjectSpec(
        board=raw["board"],
        goal=raw["goal"],
        components=components,
        constraints=raw.get("constraints", []),
    )


def build_user_message(spec: ProjectSpec, board_meta: dict, reference_text: str) -> str:
    component_lines = "\n".join(
        f"  - {c.name} ({c.connection}): {c.notes or 'no additional notes'}"
        for c in spec.components
    )
    return f"""SPEC:
board: {spec.board} ({board_meta['display_name']})
toolchain: {board_meta['toolchain']}
fqbn: {board_meta.get('fqbn', 'N/A -- not an arduino-cli board')}
goal: {spec.goal}
components:
{component_lines}
constraints: {', '.join(spec.constraints) or 'none stated'}

HARDWARE REFERENCE ({spec.board}):
{reference_text}

Generate the code for this spec. Write it with write_code, then verify
it with compile_check before reporting your final STATUS line. Use
toolchain="{board_meta['toolchain']}" and fqbn="{board_meta.get('fqbn', '')}"
when calling compile_check."""


async def run_coder_agent(spec_path: Path) -> int:
    spec = load_spec(spec_path)

    # Mandatory grounding step -- NOT a tool the agent can choose to call
    # or skip. If the board is unknown or its reference doc is missing,
    # fail loudly here, before the agent ever runs, rather than letting
    # it generate ungrounded code.
    try:
        board_meta = get_board_meta(spec.board)
        reference_text = get_reference_text(spec.board)
    except (ValueError, FileNotFoundError) as e:
        print(f"STATUS: ESCALATE\n{e}")
        return 1

    system_prompt = (Path(__file__).parent / "system_prompt.md").read_text().format(
        max_retries=MAX_RETRIES
    )

    tool_server = create_sdk_mcp_server(
        name="coder-tools", version="1.0.0", tools=[write_code, run_compile_check]
    )

    options = ClaudeAgentOptions(
        system_prompt=system_prompt,
        mcp_servers={"tools": tool_server},
        allowed_tools=["mcp__tools__write_code", "mcp__tools__compile_check"],
        # Generous headroom for write+check+fix cycles: each retry is
        # roughly a write_code turn + a compile_check turn + a reasoning
        # turn, plus room for the final summary.
        max_turns=MAX_RETRIES * 3 + 4,
    )

    user_message = build_user_message(spec, board_meta, reference_text)

    final_text = ""
    try:
        async with ClaudeSDKClient(options=options) as client:
            await client.query(user_message)
            async for msg in client.receive_response():
                if isinstance(msg, AssistantMessage):
                    text = "".join(b.text for b in msg.content if isinstance(b, TextBlock))
                    if text:
                        print(text)
                        final_text += text
    except ClaudeSDKError as e:
        print(f"STATUS: ESCALATE\nSDK error, not a code-generation failure: {e}")
        return 1

    if "STATUS: PASS" in final_text:
        return 0
    return 1


def main():
    if len(sys.argv) != 2:
        print("Usage: python3 coder_agent.py path/to/spec.yaml", file=sys.stderr)
        sys.exit(2)
    spec_path = Path(sys.argv[1])
    if not spec_path.exists():
        print(f"Spec file not found: {spec_path}", file=sys.stderr)
        sys.exit(2)
    sys.exit(asyncio.run(run_coder_agent(spec_path)))


if __name__ == "__main__":
    main()
