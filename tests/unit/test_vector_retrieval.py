from app.bootstrap import build_seed_knowledge_documents, build_seed_rubrics
from app.infrastructure.vector_store.simple_tfidf_vector_repository import SimpleTfidfVectorRepository


def test_vector_retrieval_returns_relevant_consumo_context() -> None:
    retriever = SimpleTfidfVectorRepository(build_seed_rubrics(), documents=build_seed_knowledge_documents())
    contexts = retriever.retrieve("guardar parte do dinheiro e comprar só o necessário", top_k=3)
    assert len(contexts) >= 1
    assert any(context.context_id == "rub_consumo_001" for context in contexts)
    assert all(context.similarity >= 0 for context in contexts)


def test_vector_retrieval_indexes_bncc_bloom_and_concept_docs() -> None:
    retriever = SimpleTfidfVectorRepository(build_seed_rubrics(), documents=build_seed_knowledge_documents())
    contexts = retriever.retrieve("avaliar juros compostos crescimento acumulado tempo", top_k=6)
    source_types = {context.source_type for context in contexts}
    assert {"rubric", "bncc_seed", "bloom_seed", "financial_concept"} & source_types
