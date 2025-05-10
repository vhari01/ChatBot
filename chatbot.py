import requests
import time
import json
from typing import List, Dict, Tuple, Optional
import sys
import os
from dotenv import load_dotenv
from geopy.geocoders import Nominatim
from geopy.distance import geodesic
import folium
from folium import plugins
from database import Database

# Load environment variables
load_dotenv()

# Get API key and HTTP referer from environment variables
API_KEY = os.getenv("OPENROUTER_API_KEY")
HTTP_REFERER = os.getenv('HTTP_REFERER', 'http://localhost:5000')
GOOGLE_MAPS_API_KEY = os.getenv('GOOGLE_MAPS_API_KEY')

print("Debug - Environment variables loaded:")
print(f"API_KEY length: {len(API_KEY) if API_KEY else 0}")
print(f"HTTP_REFERER: {HTTP_REFERER}")

if not API_KEY:
    raise ValueError("OPENROUTER_API_KEY not found in environment variables")

# Initialize database
db = Database()

# Sample legal resources data
LEGAL_RESOURCES = {
    "legal_aid": [
        {
            "name": "Legal Aid Ontario",
            "address": "20 Dundas Street West, Toronto, ON",
            "type": "legal_aid",
            "services": ["Criminal law", "Family law", "Immigration law"],
            "coordinates": (43.6532, -79.3832)
        },
        {
            "name": "Community Legal Services",
            "address": "123 Main Street, Toronto, ON",
            "type": "legal_aid",
            "services": ["Housing law", "Employment law", "Social assistance"],
            "coordinates": (43.6545, -79.3845)
        }
    ],
    "law_firms": [
        {
            "name": "Smith & Associates",
            "address": "456 Bay Street, Toronto, ON",
            "type": "law_firms",
            "services": ["Corporate law", "Real estate", "Tax law"],
            "coordinates": (43.6520, -79.3820)
        }
    ],
    "legal_clinics": [
        {
            "name": "Downtown Legal Services",
            "address": "789 Queen Street West, Toronto, ON",
            "type": "legal_clinics",
            "services": ["Student legal services", "Community legal education"],
            "coordinates": (43.6510, -79.3810)
        }
    ]
}

# Import initial data if database is empty
if not db.get_all_resources():
    db.import_initial_data(LEGAL_RESOURCES)

# Canadian-specific topics and resources
TOPIC_SUGGESTIONS = [
    "Canadian Workplace Rights",
    "Filing a Discrimination Complaint",
    "Equal Pay Rights in Canada",
    "Human Rights Commission Process",
    "Employment Equity in Canada",
    "Immigration and Equality Rights",
    "Provincial vs Federal Rights",
    "Legal Aid Resources",
    "Workplace Harassment",
    "Wrongful Termination",
    "Employment Standards",
    "Occupational Health and Safety"
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
    "workplace_safety": {
        "name": "Canadian Centre for Occupational Health and Safety",
        "url": "https://www.ccohs.ca/",
        "forms": ["Workplace Harassment Complaint Form", "Safety Concern Report"]
    },
    "provincial_resources": {
        "ontario": "http://www.ohrc.on.ca/",
        "quebec": "https://www.cdpdj.qc.ca/en",
        "british_columbia": "https://bchumanrights.ca/",
        # Add other provinces as needed
    }
}

# Legal resource locations database
LEGAL_RESOURCES = {
    "human_rights_offices": [
        {
            "name": "Canadian Human Rights Commission - Ottawa",
            "address": "344 Slater Street, Ottawa, ON K1A 1E1",
            "type": "human_rights",
            "services": ["Discrimination complaints", "Human rights inquiries"],
            "coordinates": (45.4215, -75.6972)
        },
        {
            "name": "Ontario Human Rights Commission",
            "address": "180 Dundas Street West, Toronto, ON M7A 2R9",
            "type": "human_rights",
            "services": ["Discrimination complaints", "Human rights education"],
            "coordinates": (43.6532, -79.3832)
        }
    ],
    "legal_aid_offices": [
        {
            "name": "Legal Aid Ontario - Toronto",
            "address": "20 Dundas Street West, Toronto, ON M5G 2C2",
            "type": "legal_aid",
            "services": ["Legal representation", "Legal advice"],
            "coordinates": (43.6548, -79.3807)
        }
    ],
    "immigration_centers": [
        {
            "name": "Immigration, Refugees and Citizenship Canada - Vancouver",
            "address": "300 West Georgia Street, Vancouver, BC V6B 6C9",
            "type": "immigration",
            "services": ["Immigration services", "Refugee assistance"],
            "coordinates": (49.2827, -123.1207)
        }
    ],
    "employment_centers": [
        {
            "name": "Employment and Social Development Canada - Montreal",
            "address": "200 René-Lévesque Blvd W, Montreal, QC H2Z 1X4",
            "type": "employment",
            "services": ["Employment rights", "Workplace complaints"],
            "coordinates": (45.5017, -73.5673)
        }
    ]
}

system_message = {
    "role": "system",
    "content": (
        "You are an expert assistant focused on Canadian rights and resources related to "
        "gender equality (SDG-5), reduced inequalities (SDG-10), and workplace rights. "
        "Your expertise includes:\n\n"
        "1. Canadian Rights and Legislation:\n"
        "   - Canadian Human Rights Act\n"
        "   - Employment Equity Act\n"
        "   - Pay Equity Act\n"
        "   - Provincial human rights codes\n"
        "   - Workplace harassment laws\n"
        "   - Occupational Health and Safety laws\n"
        "   - Employment Standards legislation\n\n"
        "2. Legal Rights and Workplace Issues:\n"
        "   - Workplace harassment and bullying\n"
        "   - Constructive dismissal\n"
        "   - Wrongful termination\n"
        "   - Employment contracts\n"
        "   - Workplace safety\n"
        "   - Legal remedies and options\n\n"
        "3. Filing Complaints and Forms:\n"
        "   - How to file discrimination complaints\n"
        "   - Required documentation and evidence\n"
        "   - Timeline and process expectations\n"
        "   - Appeals procedures\n"
        "   - Legal aid options\n\n"
        "4. Available Resources:\n"
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
        "8. Include contact information for relevant agencies\n"
        "9. For legal questions, explain both the legal framework and practical steps\n"
        "10. Always clarify when legal advice should be sought from a qualified lawyer"
    )
}

class Chatbot:
    def __init__(self):
        self.conversation_history: List[Dict] = [system_message]
        self.max_history = 10
        self.current_topic = None
        self.geolocator = Nominatim(user_agent="canadian_rights_chatbot")
        self.db = Database()
        
    def create_map(self, user_location: tuple, resources: List[Dict]) -> str:
        """Create an interactive map with user location and nearby resources"""
        try:
            # Create a map centered at user's location
            m = folium.Map(location=user_location, zoom_start=12)
            
            # Add user location marker
            folium.Marker(
                user_location,
                popup="Your Location",
                icon=folium.Icon(color='blue', icon='info-sign')
            ).add_to(m)
            
            # Add resource markers
            for resource in resources:
                folium.Marker(
                    resource["coordinates"],
                    popup=f"{resource['name']}<br>{resource['address']}<br>Distance: {resource['distance']}km",
                    icon=folium.Icon(color='red', icon='info-sign')
                ).add_to(m)
                
                # Add a line from user to resource
                folium.PolyLine(
                    locations=[user_location, resource["coordinates"]],
                    color='gray',
                    weight=2,
                    opacity=0.8
                ).add_to(m)
            
            # Ensure templates directory exists
            os.makedirs('templates', exist_ok=True)
            
            # Save the map
            map_file = "templates/map.html"
            m.save(map_file)
            print(f"Map saved to {map_file}")  # Debug print
            return map_file
        except Exception as e:
            print(f"Error creating map: {str(e)}")  # Debug print
            return None
        
    def find_nearby_resources(self, location: str, resource_type: str = None, max_distance: float = 50.0) -> List[Dict]:
        """Find legal resources near a given location"""
        try:
            # Geocode the location
            location_data = self.geolocator.geocode(location)
            if not location_data:
                return []
                
            user_coords = (location_data.latitude, location_data.longitude)
            nearby_resources = []
            
            # Get resources from database
            resources = self.db.get_resources_by_type(resource_type) if resource_type else self.db.get_all_resources()
            
            # Calculate distances and filter
            for resource in resources:
                distance = geodesic(user_coords, resource["coordinates"]).kilometers
                if distance <= max_distance:
                    resource_copy = resource.copy()
                    resource_copy["distance"] = round(distance, 1)
                    nearby_resources.append(resource_copy)
            
            # Sort by distance
            return sorted(nearby_resources, key=lambda x: x["distance"])
            
        except Exception as e:
            print(f"Error finding nearby resources: {str(e)}")
            return []
            
    def format_location_response(self, resources: List[Dict], user_location: tuple) -> str:
        """Format location-based response"""
        if not resources:
            return "I couldn't find any legal resources in that area. Please try a different location or check the resources online."
            
        response = "Here are the legal resources near you:\n\n"
        
        for resource in resources:
            response += f"📍 {resource['name']}\n"
            response += f"📌 Address: {resource['address']}\n"
            response += f"📏 Distance: {resource['distance']} km\n"
            response += f"🛠️ Services: {', '.join(resource['services'])}\n"
            response += "\n"
            
        # Create and save the map
        map_file = self.create_map(user_location, resources)
        response += f"\n🗺️ View the interactive map: {map_file}"
            
        return response

    def get_relevant_resources(self, topic: str, location: str = None) -> dict:
        """Get relevant Canadian resources based on the topic and location"""
        resources = {}
        
        # Get topic-based resources
        if "discrimination" in topic.lower() or "rights" in topic.lower():
            resources["main"] = CANADIAN_RESOURCES["human_rights"]
        if "employment" in topic.lower() or "workplace" in topic.lower():
            resources["employment"] = CANADIAN_RESOURCES["employment"]
        if "legal" in topic.lower() or "law" in topic.lower():
            resources["legal"] = CANADIAN_RESOURCES["legal_aid"]
            
        # Add location-based resources if location is provided
        if location:
            location_data = self.geolocator.geocode(location)
            if location_data:
                user_coords = (location_data.latitude, location_data.longitude)
                nearby_resources = self.find_nearby_resources(location)
                if nearby_resources:
                    resources["nearby"] = self.format_location_response(nearby_resources, user_coords)
                
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
            # Check if the prompt is a location query
            location_keywords = ['where', 'near', 'close to', 'in', 'at']
            is_location_query = any(keyword in prompt.lower() for keyword in location_keywords)
            
            # Add user message to history
            self.conversation_history.append({"role": "user", "content": prompt})
            
            # Show typing indicator
            self.show_typing_indicator()
            
            # If it's a location query, extract the location
            location = None
            if is_location_query:
                # Try to extract location from the prompt
                words = prompt.lower().split()
                for i, word in enumerate(words):
                    if word in location_keywords and i + 1 < len(words):
                        location = ' '.join(words[i+1:])
                        break
            
            # Make API request
            response = requests.post(
                "https://openrouter.ai/api/v1/chat/completions",
                headers={
                    "Authorization": f"Bearer {API_KEY}",
                    "HTTP-Referer": HTTP_REFERER,
                    "X-Title": "Canadian Rights Chatbot",
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
            
            # Check if the response was successful
            if response.status_code != 200:
                error_msg = f"API request failed with status code {response.status_code}"
                try:
                    error_details = response.json()
                    if "error" in error_details:
                        error_msg += f": {error_details['error']}"
                except:
                    pass
                raise Exception(error_msg)
                
            # Get response content
            data = response.json()
            
            # Check if the response has the expected structure
            if "choices" not in data or not data["choices"]:
                raise Exception("Invalid API response format")
                
            bot_response = data["choices"][0]["message"]["content"]
            
            # Validate response
            if not self.validate_response(bot_response):
                raise Exception("Invalid response from API")
            
            # Get relevant resources
            resources = self.get_relevant_resources(prompt, location)
            
            # Format response with resources
            formatted_response = self.format_response(bot_response, resources)
            
            # Add bot response to history
            self.conversation_history.append({"role": "assistant", "content": formatted_response})
            
            # Keep conversation history manageable
            if len(self.conversation_history) > self.max_history:
                self.conversation_history = [system_message] + self.conversation_history[-self.max_history:]
            
            return formatted_response
            
        except requests.exceptions.RequestException as e:
            return f"I apologize, but I encountered a network error: {str(e)}"
        except json.JSONDecodeError:
            return "I apologize, but I received an invalid response from the server."
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
