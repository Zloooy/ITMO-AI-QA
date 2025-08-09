import dspy
from config import LLM_API_BASE, LLM_API_KEY
from data.ydb_adapter import YDBAdapter
from embeddings import encode_query

lm = dspy.LM(
    "openai/gemini-2.5-flash",
    api_base=LLM_API_BASE,
    api_key=LLM_API_KEY,
    model_type="chat",
)

class GenerateAnswer(dspy.Signature):
    """Answer questions with the help of retrieved contexts."""

    engineer_context = dspy.InputField(desc="relevant context from AI engineer articles")
    manager_context = dspy.InputField(desc="relevant context from AI product manager articles")
    question = dspy.InputField(desc="question to answer")
    answer = dspy.OutputField(desc="answer to the question")

class RAG(dspy.Module):
    def __init__(self, num_passages=3):
        super().__init__()
        self.retrieve = dspy.Retrieve(k=num_passages)
        self.generate_answer = dspy.ChainOfThought(GenerateAnswer)
        self.ydb_adapter = YDBAdapter()

    def forward(self, question):
        query_embedding = encode_query(question)
        
        # Perform two searches by different specialization_sources
        retrieved_articles_engineer = self.ydb_adapter.extract_top_simular_by_specialization(
            query_embedding, "ai_engineer"
        )
        retrieved_articles_manager = self.ydb_adapter.extract_top_simular_by_specialization(
            query_embedding, "ai_product_manager"
        )

        # Combine results from both searches
        all_retrieved_articles = retrieved_articles_engineer + retrieved_articles_manager
        
        context = [article.article_text for article in all_retrieved_articles]
        context = "\n".join(context)

        prediction = self.generate_answer(context=context, question=question)
        return prediction
