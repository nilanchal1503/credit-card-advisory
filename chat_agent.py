from serpapi import GoogleSearch
from langchain.chains import ConversationChain
from langchain.memory import ConversationBufferMemory
import os

# Set the SERP API key
os.environ["SERP_API_KEY"] = "fcc806f328affde082149cf0609a6fb346003bf3da079de728e7d1588d9b06ce"

# Function to fetch search results using SERP API
def fetch_search_results(query):
    """
    Fetch search results using the SERP API.
    """
    api_key = os.getenv("SERP_API_KEY")
    if not api_key:
        raise ValueError("SERP API Key not found. Set it as an environment variable.")

    params = {
        "q": query,
        "location": "India",
        "hl": "en",
        "gl": "in",
        "api_key": api_key
    }

    try:
        search = GoogleSearch(params)
        results = search.get_dict()
        return results.get("organic_results", [])
    except Exception as e:
        print(f"Error fetching search results: {e}")
        return []

# Memory and conversation setup
memory = ConversationBufferMemory()
conversation = ConversationChain(memory=memory, verbose=True)

# Terminal chat loop
print("Chat Agent initialized. Type 'exit' or 'quit' to stop the chat.")
while True:
    user_input = input("You: ")
    if user_input.lower() in ["exit", "quit"]:
        print("Goodbye!")
        break

    # Use SERP API to fetch results
    search_results = fetch_search_results(user_input)
    if search_results:
        response = "Here are the top search results:\n"
        for result in search_results[:5]:  # Display the top 5 results
            response += f"- {result['title']}: {result['link']}\n"
    else:
        response = "I couldn't find any results. Please try rephrasing your query."

    # Append to conversation memory
    memory.save_context({"user": user_input}, {"response": response})
    
    # Print the response
    print("Advisor:", response)
