"""Topic taxonomy for AI tutorial classification."""

from __future__ import annotations

TOPIC_TAXONOMY: dict[str, list[str]] = {
    "large-language-models": [
        "GPT", "Claude", "Gemini", "Llama", "Mistral", "prompt engineering",
        "fine-tuning", "RLHF", "DPO", "tokenization", "context window",
        "function calling", "tool use", "structured output",
    ],
    "agents": [
        "AI agents", "agentic AI", "agent framework", "MCP", "tool use",
        "ReAct", "chain of thought", "planning", "multi-agent",
        "agent SDK", "computer use", "autonomous agents",
    ],
    "rag": [
        "retrieval augmented generation", "RAG", "vector database",
        "embeddings", "chunking", "hybrid search", "reranking",
        "knowledge base", "semantic search",
    ],
    "computer-vision": [
        "image recognition", "object detection", "segmentation",
        "diffusion models", "Stable Diffusion", "DALL-E", "Midjourney",
        "image generation", "video generation", "Sora", "ControlNet",
    ],
    "mlops": [
        "model deployment", "inference optimization", "quantization",
        "ONNX", "TensorRT", "model serving", "MLflow", "Weights & Biases",
        "monitoring", "A/B testing", "feature store",
    ],
    "frameworks": [
        "LangChain", "LlamaIndex", "Hugging Face", "PyTorch", "TensorFlow",
        "JAX", "vLLM", "Ollama", "LiteLLM", "CrewAI", "AutoGen",
    ],
    "data": [
        "data engineering", "data pipeline", "synthetic data",
        "data labeling", "annotation", "dataset curation",
        "data quality", "preprocessing",
    ],
    "ethics-safety": [
        "AI safety", "alignment", "red teaming", "guardrails",
        "bias", "fairness", "explainability", "interpretability",
        "responsible AI", "AI governance",
    ],
}

DIFFICULTY_LEVELS = ["beginner", "intermediate", "advanced"]

CONTENT_TYPES = ["video", "article", "repository", "course", "paper", "notebook"]
