from backend.services.retriever import Retriever

if __name__ == "__main__":
    engine = Retriever()
    count = engine.build()
    print(f"Knowledge index created successfully with {count} records.")
