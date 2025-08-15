import json
import shutil
import subprocess
from datetime import datetime
from pathlib import Path

from base import CodeCheckResult, ESLintInfo


def run_eslint(filename: str, output_filename: str) -> CodeCheckResult:
    curr_dir = Path()
    base_dir = curr_dir.resolve()
    eslint_dir = base_dir / "output"
    file_path = eslint_dir / "app" / filename
    results_dir = eslint_dir / "results"
    backup_dir = results_dir / "backup"
    output_path = results_dir / output_filename

    print(f"curr_dir: {curr_dir}")
    print(f"base_dir: {base_dir}")
    print(f"eslint_dir: {eslint_dir}")
    print(f"file_path: {file_path}")
    print(f"results_dir: {results_dir}")
    print(f"backup_dir: {backup_dir}")
    print(f"output_path: {output_path}")

    # for Directory check
    if not eslint_dir.exists():
        error_msg = f"ESLint directory not found : {eslint_dir}"

        eslint_result = CodeCheckResult(
            result=False, output_filename=None, error_detail=error_msg
        )
        return eslint_result

    # for backup
    if output_path.exists():
        results_dir.mkdir(exist_ok=True)
        backup_dir.mkdir(exist_ok=True)

        mtime = datetime.fromtimestamp(output_path.stat().st_mtime)
        timestamp = mtime.strftime("%Y%m%d_%H%M%S")

        stem = output_path.stem
        suffix = output_path.suffix.lstrip(".")

        backup_filename = f"{stem}_{timestamp}.{suffix}"
        backup_path = results_dir / backup_dir / backup_filename
        print(f"backup_path: {backup_path}")

        shutil.copy2(output_path, backup_path)
        print(f"Backup created: {backup_path}")

    command = ["npx", "eslint", str(file_path), "--format", "./eslint.formatter.mjs"]

    with output_path.open("w", encoding="utf-8") as f:
        result = subprocess.run(
            command, cwd=eslint_dir, stdout=f, stderr=subprocess.PIPE, text=True
        )

    print(f"ESLint process exited with return code: {result.returncode}")

    try:
        with output_path.open("r", encoding="utf-8") as f:
            eslint_output = json.load(f)

        print("--- create eslint_info_list ---")
        print(f"eslint_output: {eslint_output}")
        eslint_info_list = []
        for file_result in eslint_output:
            messages = file_result.get("messages", [])
            is_check_ok = len(messages) == 0

            print(f"messages: {messages}")
            for msg in messages:
                rule_id = msg.get("ruleId", "")
                print(f"rule_id: {rule_id}")
                description = ""

                rules_meta = msg.get("rulesMeta", {})
                if rule_id in rules_meta:
                    description = (
                        rules_meta[rule_id].get("docs", {}).get("description", "")
                    )
                    print(f"description: {description}")

                raw_message = msg.get("message", "")
                parsed_message = raw_message
                parsed_instruction = ""
                try:
                    parsed_json = json.loads(raw_message)
                    parsed_message = parsed_json.get("message", raw_message)
                    parsed_instruction = parsed_json.get("instruction", "")
                except (json.JSONDecodeError, TypeError):
                    parsed_message = raw_message

                full_message = parsed_message
                print(f"full_message(1): {full_message}")
                if parsed_instruction:
                    full_message += f" ({parsed_instruction})"
                print(f"full_message(2): {full_message}")

                eslint_info_list.append(
                    ESLintInfo(
                        message=full_message,
                        description=description,
                        rule_id=rule_id,
                    )
                )

        print("Formatted ESLint Output:")
        formatted_json = json.dumps(eslint_output, indent=2, ensure_ascii=False)

        with output_path.open("w", encoding="utf-8") as f:
            f.write(formatted_json)

    except json.JSONDecodeError as e:
        error_msg = f"Failed to parse JSON from {output_path} : {e}"
        eslint_result = CodeCheckResult(
            result=False, output_filename=None, error_detail=error_msg
        )
        return eslint_result

    eslint_result = CodeCheckResult(
        result=True,
        output_filename=str(output_path),
        error_detail=None,
        eslint_result=is_check_ok,
        eslint_info=eslint_info_list,
    )
    return eslint_result
