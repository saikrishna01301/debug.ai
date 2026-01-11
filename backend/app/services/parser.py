import re

# parse error to structured data


class ErrorParser:
    def __init__(self):
        # regex patterns
        self.python_patterns = {
            "error_type": r"(\w+Error|\w+Exception):",
            "file_line": r'File "([^"]+)", line (\d+)',
            "function": r"in (\w+)",
        }

    def parse(self, error_message: str) -> dict:
        language = self.detect_language(error_message)

        if language == "python":
            return self.parse_python_error(error_message)
        elif language == "javascript":
            return self.parse_javascript_error(error_message)
        else:
            return self.parse_unknown_error(error_message)

    def detect_language(self, error_message: str) -> str:
        # Python indicators
        if "Traceback" in error_message or 'File "' in error_message:
            return "python"

        # JavaScript indicators
        if (
            "    at " in error_message
            or "TypeError:" in error_message
            and ".js:" in error_message
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

    def parse_javascript_error(self, error_message: str) -> dict:
        pass

    def parse_unknown_error(self, error_message: str) -> dict:
        # Fallback parser for unknown languages uses LLM
        pass
