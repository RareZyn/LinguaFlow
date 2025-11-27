import os
import google.generativeai as genai
from google.api_core import exceptions

class GeminiController:
    def __init__(self, api_key=None):
        """
        Initialize the Gemini controller with API key and System Instructions.
        """
        self.api_key = api_key or os.getenv('GEMINI_API_KEY')

        if not self.api_key:
            raise ValueError(
                "Gemini API key not provided. Either pass it to the constructor or set GEMINI_API_KEY environment variable."
            )

        genai.configure(api_key=self.api_key)

        # Define the system prompt for semantic resolution of operation words
        system_instruction = """
        You are a semantic resolver for a grammar-based mathematical interpreter.

        Your ONLY task is to determine if a single word represents a mathematical operation.

        When given a word, respond with ONLY ONE of these symbols:
        - + (for addition: sum, add, plus, total, accumulate, aggregate, combine, etc.)
        - - (for subtraction: subtract, minus, difference, take away, remove, etc.)
        - * (for multiplication: multiply, times, product, etc.)
        - / (for division: divide, split, quotient, etc.)

        Rules:
        1. Respond with ONLY the symbol: +, -, *, or /
        2. NO explanations, NO extra text, ONLY the symbol
        3. If the word is NOT a mathematical operation, respond with: ERROR
        4. Consider synonyms and common variations
        5. Be case-insensitive

        Examples:
        Input: "sum" → Output: +
        Input: "accumulate" → Output: +
        Input: "multiply" → Output: *
        Input: "quotient" → Output: /
        Input: "gibberish" → Output: ERROR
        Input: "hello" → Output: ERROR
        """

        # Initialize the model with the system instruction
        # Note: 'gemini-2.5-flash' is the basic stable model
        self.model = genai.GenerativeModel(
            model_name='gemini-2.5-flash',
            system_instruction=system_instruction
        )

    def resolve_operation_word(self, word):
        """
        Resolve a single word to a mathematical operator symbol.

        This is the NEW interface following grammar-first design:
        - Input: A single word (e.g., "sum", "accumulate", "multiply")
        - Output: A single symbol (+, -, *, /) or ERROR

        Args:
            word (str): The operation word to resolve

        Returns:
            tuple: (symbol, error)
                - symbol: One of '+', '-', '*', '/' or None if error
                - error: Error message or None if successful

        Example:
            >>> resolve_operation_word("sum")
            ('+', None)
            >>> resolve_operation_word("gibberish")
            (None, "Unknown operation word: 'gibberish'")
        """
        try:
            response = self.model.generate_content(word)
            result = response.text.strip()

            # Validate response
            if result in ['+', '-', '*', '/']:
                return result, None
            elif result == "ERROR":
                return None, f"Unknown operation word: '{word}'"
            else:
                # LLM returned unexpected format - treat as error
                return None, f"Cannot resolve '{word}' to a mathematical operation"

        except exceptions.ResourceExhausted:
            return None, "LLM quota exceeded. Please try again later."
        except Exception as e:
            return None, f"LLM error: {str(e)}"

    # Keep old method for backwards compatibility during transition
    def convert_to_expression(self, natural_language_input):
        """
        DEPRECATED: Old interface for full sentence conversion.
        Use resolve_operation_word() instead for grammar-first approach.
        """
        try:
            response = self.model.generate_content(natural_language_input)
            result = response.text.strip()

            if result.startswith("ERROR"):
                return None, result

            return result, None

        except exceptions.ResourceExhausted:
            return None, "ERROR: Quota exceeded. Please try again later."
        except Exception as e:
            return None, f"ERROR: Gemini API error - {str(e)}"

    def test_connection(self):
        """
        Test the connection.
        """
        try:
            # Simple test
            response = self.model.generate_content("Output the number 1")
            return response.text is not None
        except Exception as e:
            print(f"Connection test failed: {str(e)}")
            return False

# Singleton setup remains the same
_gemini_instance = None

def get_gemini_controller(api_key=None):
    global _gemini_instance
    if _gemini_instance is None:
        _gemini_instance = GeminiController(api_key)
    return _gemini_instance