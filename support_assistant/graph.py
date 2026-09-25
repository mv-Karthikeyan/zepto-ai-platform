# ============================================================
# ZEPTO SUPPORT ASSISTANT - LANGGRAPH WORKFLOW
# ============================================================

import os
from typing import TypedDict, List, Dict, Any

from langgraph.graph import StateGraph, START, END

from .retrieval import retrieve_documents
from .models import AskResponse
from .prompts import POLICY_PROMPT_TEMPLATE
from .llm import call_real_llm


# ============================================================
# CONFIGURATION
# ============================================================

# MOCK_LLM is the default graded mode.
#
# MOCK_LLM=1 or unset:
#     No external LLM call is made.
#
# MOCK_LLM=0:
#     Optional Groq real-LLM path is used.
MOCK_LLM = os.getenv(
    "MOCK_LLM",
    "1"
)


# Required policy keywords
POLICY_KEYWORDS = [
    "delivery",
    "return",
    "refund",
    "membership",
    "tracking",
    "cancel",
    "gift card",
    "support hours",
]


# ============================================================
# LANGGRAPH STATE
# ============================================================

class AssistantState(TypedDict, total=False):

    query: str

    intent: str

    retrieved_documents: List[
        Dict[str, Any]
    ]

    answer: str

    sources: List[str]

    confidence: float


# ============================================================
# NODE 1 - CLASSIFY INTENT
# ============================================================

def classify_intent(
    state: AssistantState
):
    """
    Classify the user's question.

    In MOCK_LLM=1 mode, the required deterministic
    keyword heuristic is used.
    """

    query = state["query"]

    query_lower = query.lower()


    # --------------------------------------------------------
    # MOCK MODE
    # --------------------------------------------------------

    if MOCK_LLM != "0":

        if any(
            keyword in query_lower
            for keyword in POLICY_KEYWORDS
        ):

            intent = "policy_question"

        else:

            intent = "general_question"


    # --------------------------------------------------------
    # OPTIONAL REAL MODE
    # --------------------------------------------------------
    #
    # Intent classification intentionally remains
    # deterministic so routing remains predictable.
    #
    # Real LLM generation happens in the generation nodes.
    # --------------------------------------------------------

    else:

        if any(
            keyword in query_lower
            for keyword in POLICY_KEYWORDS
        ):

            intent = "policy_question"

        else:

            intent = "general_question"


    return {
        "intent": intent
    }


# ============================================================
# CONDITIONAL ROUTER
# ============================================================

def route_by_intent(
    state: AssistantState
):
    """
    Route to the correct LangGraph node.
    """

    if (
        state["intent"]
        == "policy_question"
    ):

        return "retrieve_and_answer"

    return "direct_answer"


# ============================================================
# NODE 2 - RETRIEVE AND ANSWER
# ============================================================

def retrieve_and_answer(
    state: AssistantState
):
    """
    Handle Zepto policy questions.

    Retrieval is real in BOTH modes.

    MOCK_LLM=1:
        Real ChromaDB retrieval +
        deterministic mock answer.

    MOCK_LLM=0:
        Real ChromaDB retrieval +
        structured prompt +
        Groq generation +
        Pydantic validation/retries.
    """

    query = state["query"]


    # --------------------------------------------------------
    # REAL TOP-3 RETRIEVAL
    # --------------------------------------------------------

    retrieved = retrieve_documents(
        query,
        top_k=3
    )


    if not retrieved:

        return {
            "retrieved_documents": [],
            "answer": (
                "No relevant Zepto policy "
                "context was found."
            ),
            "sources": [],
            "confidence": 0.0
        }


    # Most relevant document
    top_document = retrieved[0]


    # Approximately first 200 characters
    top_chunk_snippet = (
        top_document["text"][:200]
    )


    # All top-3 document IDs
    sources = [
        document["id"]
        for document in retrieved
    ]


    # Similarity from most relevant document
    confidence = max(
        0.0,
        min(
            1.0,
            float(
                top_document["similarity"]
            )
        )
    )


    # --------------------------------------------------------
    # MOCK GENERATION
    # --------------------------------------------------------

    if MOCK_LLM != "0":

        answer = (
            "Based on the retrieved context: "
            f"{top_chunk_snippet}"
        )


    # --------------------------------------------------------
    # OPTIONAL REAL LLM GENERATION
    # --------------------------------------------------------

    else:

        # Build context containing both source IDs
        # and policy text.
        context = "\n\n".join(
            (
                f"Source: {document['id']}\n"
                f"{document['text']}"
            )
            for document in retrieved
        )


        # Build the structured prompt.
        prepared_prompt = (
            POLICY_PROMPT_TEMPLATE.format(
                context=context,
                query=query
            )
        )


        # call_real_llm performs:
        #
        # 1. Groq generation
        # 2. JSON parsing
        # 3. Pydantic validation
        # 4. Initial attempt + up to 2 retries

        real_response = call_real_llm(
            prepared_prompt
        )


        answer = real_response.answer


        # Only accept source IDs that were actually
        # returned by ChromaDB.
        retrieved_ids = [
            document["id"]
            for document in retrieved
        ]


        sources = [
            source
            for source in real_response.sources
            if source in retrieved_ids
        ]


        confidence = (
            real_response.confidence
        )


    # --------------------------------------------------------
    # FINAL PYDANTIC VALIDATION
    # --------------------------------------------------------

    validated_response = AskResponse(
        answer=answer,
        sources=sources,
        confidence=round(
            float(confidence),
            4
        )
    )


    return {
        "retrieved_documents": retrieved,

        "answer":
            validated_response.answer,

        "sources":
            validated_response.sources,

        "confidence":
            validated_response.confidence
    }


# ============================================================
# NODE 3 - DIRECT ANSWER
# ============================================================

def direct_answer(
    state: AssistantState
):
    """
    Handle general/non-policy questions.

    MOCK mode returns the required deterministic response.
    """

    if MOCK_LLM != "0":

        answer = (
            "I can only answer questions about "
            "Zepto policies right now."
        )

        sources = []

        confidence = 1.0


    else:

        # General questions are intentionally restricted.
        #
        # We do not allow an external LLM to invent policy
        # information for unrelated questions.

        answer = (
            "I can only answer questions about "
            "Zepto policies right now."
        )

        sources = []

        confidence = 1.0


    validated_response = AskResponse(
        answer=answer,
        sources=sources,
        confidence=confidence
    )


    return {
        "answer":
            validated_response.answer,

        "sources":
            validated_response.sources,

        "confidence":
            validated_response.confidence
    }


# ============================================================
# BUILD LANGGRAPH
# ============================================================

workflow = StateGraph(
    AssistantState
)


# ------------------------------------------------------------
# ADD THREE REQUIRED NAMED NODES
# ------------------------------------------------------------

workflow.add_node(
    "classify_intent",
    classify_intent
)

workflow.add_node(
    "retrieve_and_answer",
    retrieve_and_answer
)

workflow.add_node(
    "direct_answer",
    direct_answer
)


# ------------------------------------------------------------
# START -> CLASSIFY
# ------------------------------------------------------------

workflow.add_edge(
    START,
    "classify_intent"
)


# ------------------------------------------------------------
# CONDITIONAL EDGE
# ------------------------------------------------------------

workflow.add_conditional_edges(
    "classify_intent",

    route_by_intent,

    {
        "retrieve_and_answer":
            "retrieve_and_answer",

        "direct_answer":
            "direct_answer",
    }
)


# ------------------------------------------------------------
# END EDGES
# ------------------------------------------------------------

workflow.add_edge(
    "retrieve_and_answer",
    END
)

workflow.add_edge(
    "direct_answer",
    END
)


# ------------------------------------------------------------
# COMPILE GRAPH
# ------------------------------------------------------------

graph = workflow.compile()


# ============================================================
# LOCAL TEST
# ============================================================

if __name__ == "__main__":

    print(
        "MOCK_LLM:",
        MOCK_LLM
    )


    # --------------------------------------------------------
    # TEST 1 - POLICY QUESTION
    # --------------------------------------------------------

    policy_query = {
        "query":
            "What is the delivery fee?"
    }


    policy_result = graph.invoke(
        policy_query
    )


    print(
        "\nPOLICY QUESTION"
    )

    print(
        "-" * 60
    )

    print(
        "Query:",
        policy_query["query"]
    )

    print(
        "Intent:",
        policy_result["intent"]
    )

    print(
        "Answer:",
        policy_result["answer"]
    )

    print(
        "Sources:",
        policy_result["sources"]
    )

    print(
        "Confidence:",
        policy_result["confidence"]
    )


    # --------------------------------------------------------
    # TEST 2 - GENERAL QUESTION
    # --------------------------------------------------------

    general_query = {
        "query":
            "Who won the cricket match yesterday?"
    }


    general_result = graph.invoke(
        general_query
    )


    print(
        "\nGENERAL QUESTION"
    )

    print(
        "-" * 60
    )

    print(
        "Query:",
        general_query["query"]
    )

    print(
        "Intent:",
        general_result["intent"]
    )

    print(
        "Answer:",
        general_result["answer"]
    )

    print(
        "Sources:",
        general_result["sources"]
    )

    print(
        "Confidence:",
        general_result["confidence"]
    )