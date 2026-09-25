# ============================================================
# ZEPTO SUPPORT ASSISTANT - OPTIONAL REAL LLM SUPPORT
# ============================================================

import json
import os

from groq import Groq

from .models import AskResponse


def call_real_llm(prompt: str) -> AskResponse:
    """
    Call Groq when MOCK_LLM=0.

    The LLM must return JSON matching the AskResponse
    Pydantic schema:

        {
            "answer": "string",
            "sources": ["doc_01"],
            "confidence": 0.95
        }

    Retry behavior:
        - 1 initial attempt
        - Maximum 2 retries
        - Total maximum attempts = 3

    Important:
        MOCK_LLM=1 does NOT call this function.
        Therefore, the normal graded mock mode does not
        require a Groq API key.
    """

    # --------------------------------------------------------
    # GET GROQ API KEY
    # --------------------------------------------------------

    api_key = os.getenv("GROQ_API_KEY")

    if not api_key:
        raise RuntimeError(
            "GROQ_API_KEY is required when MOCK_LLM=0."
        )


    # --------------------------------------------------------
    # CREATE GROQ CLIENT
    # --------------------------------------------------------

    client = Groq(
        api_key=api_key
    )


    # --------------------------------------------------------
    # MODEL CONFIGURATION
    # --------------------------------------------------------

    # The model can be changed using the GROQ_MODEL
    # environment variable.
    model_name = os.getenv(
        "GROQ_MODEL",
        "llama-3.1-8b-instant"
    )


    # Store the most recent error so we can report it
    # if all attempts fail.
    last_error = None


    # --------------------------------------------------------
    # INITIAL ATTEMPT + MAXIMUM 2 RETRIES
    # --------------------------------------------------------

    for attempt in range(3):

        try:

            # ------------------------------------------------
            # CALL GROQ LLM
            # ------------------------------------------------

            completion = client.chat.completions.create(
                model=model_name,
                messages=[
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                temperature=0
            )


            # ------------------------------------------------
            # EXTRACT LLM RESPONSE
            # ------------------------------------------------

            raw_response = (
                completion
                .choices[0]
                .message
                .content
            )


            # ------------------------------------------------
            # CONVERT RESPONSE TO JSON
            # ------------------------------------------------

            parsed_response = json.loads(
                raw_response
            )


            # ------------------------------------------------
            # PYDANTIC VALIDATION
            # ------------------------------------------------
            #
            # AskResponse validates:
            #
            # answer     -> string
            # sources    -> list[str]
            # confidence -> float between 0 and 1
            #

            validated_response = (
                AskResponse.model_validate(
                    parsed_response
                )
            )


            # ------------------------------------------------
            # SUCCESS
            # ------------------------------------------------

            return validated_response


        except Exception as exc:

            # Save the error from this attempt.
            last_error = exc

            print(
                f"Real LLM validation attempt "
                f"{attempt + 1} failed: {exc}"
            )


    # --------------------------------------------------------
    # ALL THREE ATTEMPTS FAILED
    # --------------------------------------------------------

    raise RuntimeError(
        "Real LLM failed after initial attempt "
        "and 2 retries."
    ) from last_error