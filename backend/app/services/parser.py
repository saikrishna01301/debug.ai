import re
from typing import Dict

# parse error to structured data


class ErrorParser:
    def __init__(self):
        # regex patterns
        self.python_patterns = {
            "error_type": r"(\w+Error|\w+Exception):",
            "file_line": r'File "([^"]+)", line (\d+)',
            "function": r"in (\w+)",
        }

        # JavaScript error patterns
        self.js_patterns = {
            "error_type": r"(TypeError|ReferenceError|SyntaxError|RangeError|Error):",
            "file_line": r"at .+ \((.+):(\d+):(\d+)\)",
            "file_line_alt": r"at (.+):(\d+):(\d+)",
            "function": r"at (\w+)",
        }

    def parse(self, error_message: str) -> dict:
        language = self.detect_language(error_message)

        if language == "python":
            return self.parse_python_error(error_message)
        elif language == "javascript":
            return self._parse_javascript(error_message)
        else:
            return self.parse_unknown_error(error_message)

    def detect_language(self, error_message: str) -> str:
        # Python indicators
        if "Traceback" in error_message or 'File "' in error_message:
            return "python"

        # JavaScript indicators
        if any(
            indicator in error_message
            for indicator in [
                "    at ",
                "TypeError:",
                "ReferenceError:",
                "SyntaxError:",
                ".js:",
                ".jsx:",
                ".ts:",
                ".tsx:",
            ]
        ):
            return "javascript"

        return "unknown"

    def parse_python_error(self, error_message: str) -> dict:
        result = {
            "raw_error_log": error_message,
            "language": "python",
            "error_type": None,
            "error_message": None,
            "file_path": None,
            "line_number": None,
            "function_name": None,
            "stack_trace": [],
            "confidence": 0,
        }

        # extract error type
        error_match = re.search(self.python_patterns.get("error_type"), error_message)
        if error_match:
            result["error_type"] = error_match.group(1)
            result["confidence"] += 30

        # extract file and line number
        file_match = re.findall(self.python_patterns.get("file_line"), error_message)

        if file_match:
            file_path, line_number = file_match[-1]  # last occurrence
            result["file_path"] = file_path
            result["line_number"] = int(line_number)
            result["confidence"] += 30

        # extract function name
        function_match = re.search(self.python_patterns.get("function"), error_message)
        if function_match:
            result["function_name"] = function_match.group(1)
            result["confidence"] += 30

        # extract error message
        if result.get("error_type"):
            message_pattern = f"{result.get('error_type')}: (.+?)(?:\n|$)"
            message_match = re.search(message_pattern, error_message)
            if message_match:
                result["error_message"] = message_match.group(1).strip()
                result["confidence"] += 10

        return result

    def _parse_javascript(self, error_log: str) -> Dict:

        # Parse JavaScript/TypeScript error logs

        result = {
            "raw_error_log": error_log,
            "language": "javascript",
            "error_type": None,
            "error_message": None,
            "file_path": None,
            "line_number": None,
            "function_name": None,
            "stack_trace": [],
            "confidence": 0,
        }

        # Extract error type
        error_match = re.search(self.js_patterns["error_type"], error_log)
        if error_match:
            result["error_type"] = error_match.group(1)
            result["confidence"] += 30

        # Extract error message
        if result["error_type"]:
            message_pattern = f'{result["error_type"]}: (.+?)(?:\n|$)'
            message_match = re.search(message_pattern, error_log)
            if message_match:
                result["error_message"] = message_match.group(1).strip()
                result["confidence"] += 20

        # Extract file and line number
        file_matches = re.findall(self.js_patterns["file_line"], error_log)
        if not file_matches:
            file_matches = re.findall(self.js_patterns["file_line_alt"], error_log)

        if file_matches:
            # Get the first occurrence (usually the error location)
            if len(file_matches[0]) == 3:
                file_path, line, column = file_matches[0]
                result["file_path"] = file_path
                result["line_number"] = int(line)
                result["confidence"] += 30

                # Store stack trace
                result["stack_trace"] = [
                    {"file": f, "line": int(l), "column": int(c)}
                    for f, l, c in file_matches
                ]

        # Extract function name
        function_match = re.search(self.js_patterns["function"], error_log)
        if function_match:
            result["function_name"] = function_match.group(1)
            result["confidence"] += 20

        # Detect if it's React-specific
        if "react" in error_log.lower() or "jsx" in error_log.lower():
            result["framework"] = "react"
        elif "node" in error_log.lower():
            result["framework"] = "node"

        return result

    def parse_unknown_error(self, error_message: str) -> dict:
        """Fallback parser for unknown error formats"""
        return {
            "raw_error_log": error_message,
            "language": "unknown",
            "error_type": "Unknown",
            "error_message": error_message[:500],  # First 500 chars
            "file_path": None,
            "line_number": None,
            "function_name": None,
            "stack_trace": [],
            "confidence": 10,  # Low confidence for unknown errors
        }
