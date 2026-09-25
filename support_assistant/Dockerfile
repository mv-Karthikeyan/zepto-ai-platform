FROM python:3.10-slim

WORKDIR /app

# Install only the dependencies required by Module 3
COPY support_assistant/requirements.txt ./requirements.txt

RUN pip install --upgrade pip

RUN pip install --no-cache-dir -r requirements.txt

# Copy the complete support assistant package
COPY support_assistant ./support_assistant

# Default graded mode - no external LLM calls
ENV MOCK_LLM=1

# Create embeddings and ChromaDB during image build
RUN python -m support_assistant.ingest

EXPOSE 8000

CMD ["uvicorn", "support_assistant.main:app", "--host", "0.0.0.0", "--port", "8000"]