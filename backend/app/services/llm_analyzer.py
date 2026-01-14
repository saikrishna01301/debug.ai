import json
import logging
import os
from openai import OpenAI
from typing import List, Dict


class LLMAnalyzer:

    def __init__(self):
        # Initialize OpenAI client for GitHub Models (Azure)
        self.client = OpenAI(
            base_url="https://models.inference.ai.azure.com",
            api_key=os.getenv("GITHUB_TOKEN"),
        )
        self.model = "gpt-4o"

    # search_results = []
    def analyze_error(self, parsed_error: Dict, search_results: List[Dict]) -> Dict:

        # build context from search_results to pass in LLM
        context = self._build_context(search_results)

        # system prompt and user prompt
        system_prompt = self._get_system_prompt()
        user_prompt = self._create_user_prompt(parsed_error, context)

        ## Calling OpenAI with function calling for structured output

        response = self.client.chat.completions.create(
            model=self.model,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
            tools=[self._get_analysis_function()],
            tool_choice={"type": "function", "function": {"name": "provide_analysis"}},
        )

        # Extract the function call result
        tool_call = response.choices[0].message.tool_calls[0]
        analysis = json.loads(tool_call.function.arguments)

        return analysis

    def _get_system_prompt(self) -> str:
        prompt = """You are an expert debugging assistant helping developers solve errors.
            Your job:
            1. Analyze the error with provided context from Stack Overflow and documentation
            2. Identify the root cause with step-by-step reasoning
            3. Provide 2-3 ranked solutions with code examples
            4. Include confidence scores for each solution
            5. Link to relevant sources

            Guidelines:
            - Prioritize solutions from highly-voted Stack Overflow posts
            - Consider the user's language/framework
            - Explain WHY each solution works, not just HOW
            - Be honest about uncertainty (confidence < 0.7 if unsure)
            - Keep solutions practical and actionable
        """
        return prompt

    def _create_user_prompt(self, parsed_error: Dict, context: str) -> str:
        return f"""Please analyze this error:

                ERROR DETAILS:
                - Type: {parsed_error.get('error_type', 'Unknown')}
                - Message: {parsed_error.get('error_message', 'N/A')}
                - Language: {parsed_error.get('language', 'Unknown')}
                - File: {parsed_error.get('file_path', 'N/A')}
                - Line: {parsed_error.get('line_number', 'N/A')}
                - Function: {parsed_error.get('function_name', 'N/A')}

                RAW ERROR LOG:
                {parsed_error.get('raw_error_log', 'N/A')}

                RELEVANT CONTEXT FROM KNOWLEDGE BASE:
                {context}

                Provide your analysis with root cause, reasoning, and solutions.
            """

    # build context
    """
        It converts the raw search results from ChromaDB into a formatted, 
        readable string that the LLM (GPT-4o) can understand and use to generate helpful debugging advice.
    """

    def _build_context(self, search_results):
        # converting search_results into dictionary

        if not search_results:
            logging.info("No relevant context found in knowledge base.")

        context_parts = []

        for i, result in enumerate(search_results):
            content = result.get("content")[:800]  # limiting the context per result

            context_parts.append(
                f"""--- Source {i} (Votes: {result.get('votes', 0)}, Relevance: {1 - result['distance']:.2f}) ---
                Title: {result.get('title', 'N/A')}
                URL: {result.get('url', 'N/A')}
                Tags: {', '.join(result.get('tags', []))}
                Content:{content}
            """
            )
        return "\n".join(context_parts)

    # Function definition for structured output
    # later move the function to tools.py and tool_registry
    def _get_analysis_function(self) -> Dict:
        return {
            "type": "function",
            "function": {
                "name": "provide_analysis",
                "description": "Provide debugging analysis with solutions",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "root_cause": {
                            "type": "string",
                            "description": "The fundamental cause of the error",
                        },
                        "reasoning": {
                            "type": "string",
                            "description": "Step-by-step explanation of why this error occurs",
                        },
                        "solutions": {
                            "type": "array",
                            "description": "List of solutions ranked by effectiveness",
                            "items": {
                                "type": "object",
                                "properties": {
                                    "title": {
                                        "type": "string",
                                        "description": "Brief title for the solution",
                                    },
                                    "explanation": {
                                        "type": "string",
                                        "description": "Detailed explanation of the solution",
                                    },
                                    "code": {
                                        "type": "string",
                                        "description": "Code example showing the fix",
                                    },
                                    "confidence": {
                                        "type": "number",
                                        "description": "Confidence score 0-1",
                                        "minimum": 0,
                                        "maximum": 1,
                                    },
                                    "source_urls": {
                                        "type": "array",
                                        "description": "URLs to relevant Stack Overflow posts",
                                        "items": {"type": "string"},
                                    },
                                },
                                "required": [
                                    "title",
                                    "explanation",
                                    "code",
                                    "confidence",
                                ],
                            },
                            "minItems": 2,
                            "maxItems": 3,
                        },
                    },
                    "required": ["root_cause", "reasoning", "solutions"],
                },
            },
        }
