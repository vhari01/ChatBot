from chatbot import Chatbot

def test_chatbot():
    print("Initializing chatbot...")
    chatbot = Chatbot()
    
    test_message = "What are my rights regarding workplace harassment in Canada?"
    print(f"\nTesting with message: {test_message}")
    
    try:
        response = chatbot.ask_bot(test_message)
        print("\nChatbot response:")
        print(response)
        
        print("\nTopic suggestions:")
        suggestions = chatbot.show_topic_suggestions()
        for suggestion in suggestions:
            print(f"- {suggestion}")
            
    except Exception as e:
        print(f"\nError: {str(e)}")

if __name__ == "__main__":
    test_chatbot() 