# Main Quest: AI External Memory System
The primary goal of this quest is to create an automated script that allows a user to efficiently manage their conversation history with an AI.
The script should be able to quickly and accurately retrieve key points from old conversations through semantic search, enabling the user to seamlessly continue a topic in a new conversation.
# Side Quests
To complete the main quest, you must successfully complete two key stages, which will serve as your side quests.
## Side Quest 1: Information Storage
This quest focuses on the process of saving conversation data. When a conversation with the AI ends, the script must perform the following tasks:
* Summarize and Extract Keywords: The script should automatically capture the key content of the current conversation. You can choose to use the AI to generate a concise summary or have the script automatically extract keywords.
* Vectorize the Document (Embedding): The script will use an embedding model, such as Sentence-Transformers or OpenAI Embeddings API, to convert the summary text into a high-dimensional vector that represents its meaning.
* Store in a Vector Database: The generated vector, along with the original summary text, topic tags, and timestamps, will be saved into a vector database like ChromaDB or Pinecone
