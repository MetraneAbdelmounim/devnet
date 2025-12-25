from typing import List, Dict
import os

from ntc_templates.parse import parse_output as ntc_parse_output


def parse_output(
    platform: str,
    command: str,
    data: str,
) -> List[Dict]:
    """
    Wrapper around ntc_templates.parse.parse_output

    Args:
        platform (str): Device platform (e.g. "cisco_ios")
        command (str): CLI command executed
        data (str): Raw CLI output

    Returns:
        List[Dict]: Parsed structured data
    """
    try:
        parsed = ntc_parse_output(
            platform=platform,
            command=command,
            data=data,
        )
        return parsed
    except Exception as exc:
        print(f"ERROR: Failed to parse output for '{command}': {exc}")
        return []
