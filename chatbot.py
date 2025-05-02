import requests
import time
import json
from typing import List, Dict
import sys

# Replace with your actual OpenRouter API key
API_KEY = "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"

# Canadian-specific topics and resources
TOPIC_SUGGESTIONS = [
    "Canadian Workplace Rights",
    "Filing a Discrimination Complaint",
    "Equal Pay Rights in Canada",
    "Human Rights Commission Process",
    "Employment Equity in Canada",
    "Immigration and Equality Rights",
    "Provincial vs Federal Rights",
    "Legal Aid Resources"
]

# Canadian resources and forms
CANADIAN_RESOURCES = {
    "human_rights": {
        "name": "Canadian Human Rights Commission",
        "url": "https://www.chrc-ccdp.gc.ca/en",
        "forms": ["Individual Complaint Form", "Employment Equity Report"]
    },
    "employment": {
        "name": "Employment and Social Development Canada",
        "url": "https://www.canada.ca/en/employment-social-development.html",
        "forms": ["Labour Standards Complaint Form", "Pay Equity Report"]
    },
    "legal_aid": {
        "name": "Provincial Legal Aid Offices",
        "url": "https://www.justice.gc.ca/eng/contact/aid-aide.html",
        "forms": ["Legal Aid Application"]
    },
    "provincial_resources": {
        "ontario": "http://www.ohrc.on.ca/",
        "quebec": "https://www.cdpdj.qc.ca/en",
        "british_columbia": "https://bchumanrights.ca/",
        # Add other provinces as needed
    }
}

system_message = {
    "role": "system",
    "content": (
        "You are an expert assistant focused on Canadian rights and resources related to "
        "gender equality (SDG-5) and reduced inequalities (SDG-10). "
        "Your expertise includes:\n\n"
        "1. Canadian Rights and Legislation:\n"
        "   - Canadian Human Rights Act\n"
        "   - Employment Equity Act\n"
        "   - Pay Equity Act\n"
        "   - Provincial human rights codes\n"
        "   - Workplace harassment laws\n\n"
        "2. Filing Complaints and Forms:\n"
        "   - How to file discrimination complaints\n"
        "   - Required documentation and evidence\n"
        "   - Timeline and process expectations\n"
        "   - Appeals procedures\n"
        "   - Legal aid options\n\n"
        "3. Available Resources:\n"
        "   - Government agencies and contacts\n"
        "   - Legal aid services\n"
        "   - Advocacy organizations\n"
        "   - Support services\n"
        "   - Provincial vs federal jurisdiction\n\n"
        "When responding to questions:\n"
        "1. Provide specific Canadian legal references\n"
        "2. Include relevant forms and submission processes\n"
        "3. Link to official government resources\n"
        "4. Explain step-by-step procedures\n"
        "5. Maintain context from previous questions\n"
        "6. Format responses with clear sections\n"
        "7. Specify provincial vs federal jurisdiction\n"
        "8. Include contact information for relevant agencies"
    )
}

class Chatbot:
    def __init__(self):
        self.conversation_history: List[Dict] = [system_message]
        self.max_history = 10  # Keep last 10 messages for context
        self.current_topic = None
        
    def get_relevant_resources(self, topic: str) -> dict:
        """Get relevant Canadian resources based on the topic"""
        resources = {}
        if "discrimination" in topic.lower() or "rights" in topic.lower():
            resources["main"] = CANADIAN_RESOURCES["human_rights"]
        if "employment" in topic.lower() or "workplace" in topic.lower():
            resources["employment"] = CANADIAN_RESOURCES["employment"]
        if "legal" in topic.lower() or "law" in topic.lower():
            resources["legal"] = CANADIAN_RESOURCES["legal_aid"]
        return resources
        
    def format_resources(self, resources: dict) -> str:
        """Format resource information into a readable string"""
        if not resources:
            return ""
            
        formatted = "\n\nRelevant Resources:\n"
        for category, info in resources.items():
            formatted += f"\n{info['name']}:\n"
            formatted += f"• Website: {info['url']}\n"
            if 'forms' in info:
                formatted += "• Available Forms:\n"
                for form in info['forms']:
                    formatted += f"  - {form}\n"
        return formatted
        
    def show_typing_indicator(self):
        """Show a typing indicator animation"""
        for _ in range(3):
            sys.stdout.write("\rBot is thinking" + "." * (_ % 4) + "   ")
            sys.stdout.flush()
            time.sleep(0.5)
        print("\r" + " " * 20 + "\r", end="")
        
    def format_response(self, response: str, resources: dict = None) -> str:
        """Format the response for better readability"""
        # Split response into sections
        sections = response.split('\n\n')
        formatted_sections = []
        
        for section in sections:
            # Format lists
            if section.strip().startswith(('1.', '2.', '3.', '4.', '5.', '6.', '7.', '8.', '9.', '0.')):
                lines = section.split('\n')
                formatted_lines = []
                for line in lines:
                    if line.strip().startswith(('-', '*', '•')):
                        formatted_lines.append(f"• {line.strip()[1:].strip()}")
                    else:
                        formatted_lines.append(line)
                section = '\n'.join(formatted_lines)
            
            # Add spacing between sections
            formatted_sections.append(section.strip())
        
        formatted_response = '\n\n'.join(formatted_sections)
        
        # Add relevant resources if available
        if resources:
            formatted_response += self.format_resources(resources)
            
        return formatted_response
        
    def validate_response(self, response: str) -> bool:
        """Basic validation of the response"""
        return len(response.strip()) > 0 and not response.startswith("I apologize")
        
    def ask_bot(self, prompt: str) -> str:
        """Get response from the API with error handling and rate limiting"""
        try:
            # Add user message to history
            self.conversation_history.append({"role": "user", "content": prompt})
            
            # Show typing indicator
            self.show_typing_indicator()
            
            # Make API request
            response = requests.post(
                "https://openrouter.ai/api/v1/chat/completions",
                headers={
                    "Authorization": f"Bearer {API_KEY}",
                    "Content-Type": "application/json"
                },
                json={
                    "model": "mistralai/mixtral-8x7b-instruct",
                    "messages": self.conversation_history
                }
            )
            
            # Handle rate limiting
            if response.status_code == 429:
                print("\nBot: I'm getting too many requests. Please wait a moment and try again.")
                time.sleep(2)
                return self.ask_bot(prompt)
                
            # Get response content
            data = response.json()
            bot_response = data["choices"][0]["message"]["content"]
            
            # Validate response
            if not self.validate_response(bot_response):
                raise Exception("Invalid response from API")
            
            # Get relevant resources
            resources = self.get_relevant_resources(prompt)
            
            # Format response with resources
            formatted_response = self.format_response(bot_response, resources)
            
            # Add bot response to history
            self.conversation_history.append({"role": "assistant", "content": formatted_response})
            
            # Keep conversation history manageable
            if len(self.conversation_history) > self.max_history:
                self.conversation_history = [system_message] + self.conversation_history[-self.max_history:]
            
            return formatted_response
            
        except Exception as e:
            error_msg = f"I apologize, but I encountered an error: {str(e)}"
            if "rate limit" in str(e).lower():
                error_msg += "\nPlease wait a moment and try again."
            return error_msg
            
    def show_topic_suggestions(self):
        """Display topic suggestions to the user"""
        print("\n💡 Here are some topics you can ask about:")
        for i, topic in enumerate(TOPIC_SUGGESTIONS, 1):
            print(f"{i}. {topic}")
        print()

def main():
    chatbot = Chatbot()
    
    print("🌍 Canadian Rights & Resources Chatbot")
    print("Ask about your rights, how to file complaints, or access resources for gender equality and reduced inequalities.")
    print("Type 'exit' to stop the conversation or 'topics' to see suggested topics.\n")
    
    chatbot.show_topic_suggestions()
    
    while True:
        user_input = input("You: ").strip()
        
        if user_input.lower() == "exit":
            print("Bot: Goodbye! Remember, you have rights and resources available to help you.")
            break
        elif user_input.lower() == "topics":
            chatbot.show_topic_suggestions()
            continue
        elif not user_input:
            print("Bot: Please enter a question or type 'exit' to stop.")
            continue
            
        response = chatbot.ask_bot(user_input)
        print(f"Bot: {response}\n")

if __name__ == "__main__":
    main()
