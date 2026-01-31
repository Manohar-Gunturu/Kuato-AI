from python.RAG.ChatOllamaRAGPipeline import ChatOllamaRAGPipeline

rag = ChatOllamaRAGPipeline()
rag.build_index(["mahu_balance.txt", "dosa_recipe.txt"])
answer  = rag.answer("To make dosa batter with 1 and half cup of lentils, can you give me the recipe?")
print(answer)