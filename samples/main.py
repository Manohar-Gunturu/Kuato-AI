from python.RAG.ChatOllamaRAGPipeline import ChatOllamaRAGPipeline

rag = ChatOllamaRAGPipeline(chunk_size=1024, chunk_overlap=100, model="llama3")
rag.build_index(["mahu_balance.txt", "dosa_recipe.txt"])
answer  = rag.answer("How much balance Mahu has?")
print(answer)