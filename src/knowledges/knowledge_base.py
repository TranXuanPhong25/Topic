"""FAQ Knowledge Base for Medical Clinic"""
from typing import List, Dict, Any, Optional
from src.configs.config import CLINIC_CONFIG


class FAQKnowledgeBase:
    """
    Knowledge base for clinic information and frequently asked questions.
    
    This class stores and retrieves:
    - Clinic hours and contact information
    - Insurance and payment policies
    - Services offered
    - Common medical questions
    - Appointment policies
    """
    
    def __init__(self):
        """Initialize the knowledge base with clinic FAQs"""
        
        # Clinic Information
        self.clinic_info = {
            "name": CLINIC_CONFIG["name"],
            "phone": CLINIC_CONFIG["phone"],
            "address": CLINIC_CONFIG["address"],
            "hours": CLINIC_CONFIG["hours"],
            "providers": CLINIC_CONFIG["providers"],
        }
        
        # FAQ Categories
        self.faqs = {
            "hours_and_location": [
                {
                    "question": "What are your hours?",
                    "answer": f"We're open {CLINIC_CONFIG['hours']}. We're closed on Sundays and major holidays.",
                    "keywords": ["hours", "open", "close", "schedule", "time", "when"],
                },
                {
                    "question": "Where are you located?",
                    "answer": f"We're located at {CLINIC_CONFIG['address']}. We have free parking available for patients.",
                    "keywords": ["location", "address", "where", "directions", "parking"],
                },
                {
                    "question": "How do I get to the clinic?",
                    "answer": f"Our clinic is at {CLINIC_CONFIG['address']}. We're easily accessible by car with free parking, and also near public transit stops.",
                    "keywords": ["directions", "how to get", "transit", "parking", "location"],
                },
            ],
            
            "appointments": [
                {
                    "question": "How do I schedule an appointment?",
                    "answer": "You can schedule an appointment by calling us at (555) 123-4567, or by chatting with me here! Just let me know your preferred date, time, and reason for visit.",
                    "keywords": ["schedule", "appointment", "book", "make appointment", "set up"],
                },
                {
                    "question": "Do I need an appointment?",
                    "answer": "Yes, we operate by appointment only to ensure quality care and minimal wait times. However, we do accommodate same-day appointments for urgent matters when available.",
                    "keywords": ["need appointment", "walk-in", "without appointment"],
                },
                {
                    "question": "How far in advance should I book?",
                    "answer": "We recommend booking at least 1-2 weeks in advance for routine visits. For urgent concerns, we often have same-day or next-day availability. You can book up to 6 months in advance.",
                    "keywords": ["advance", "how far", "when to book", "early"],
                },
                {
                    "question": "Can I cancel or reschedule my appointment?",
                    "answer": "Yes, you can cancel or reschedule anytime. We just ask that you give us at least 24 hours notice so we can offer the slot to another patient. Call us at (555) 123-4567 to make changes.",
                    "keywords": ["cancel", "reschedule", "change appointment", "modify"],
                },
                {
                    "question": "What should I bring to my appointment?",
                    "answer": "Please bring: 1) Photo ID, 2) Insurance card, 3) List of current medications, 4) Any relevant medical records, 5) Payment method for copay. Arrive 10-15 minutes early for paperwork.",
                    "keywords": ["bring", "need", "what to bring", "paperwork", "documents"],
                },
            ],
            
            "insurance_and_payment": [
                {
                    "question": "Do you accept insurance?",
                    "answer": "Yes! We accept most major insurance plans including Blue Cross, Aetna, UnitedHealthcare, Cigna, and Medicare. Please call us to verify your specific plan.",
                    "keywords": ["insurance", "accept", "coverage", "plan", "medicare", "medicaid"],
                },
                {
                    "question": "What forms of payment do you accept?",
                    "answer": "We accept cash, credit cards (Visa, Mastercard, Discover, Amex), debit cards, HSA/FSA cards, and checks. Payment is due at time of service.",
                    "keywords": ["payment", "pay", "cost", "credit card", "cash", "hsa", "fsa"],
                },
                {
                    "question": "Do you offer payment plans?",
                    "answer": "Yes, we offer flexible payment plans for patients without insurance or for services not covered by insurance. Please speak with our billing department to set up a plan.",
                    "keywords": ["payment plan", "installment", "financing", "afford"],
                },
                {
                    "question": "How much does a visit cost?",
                    "answer": "Costs vary by service and insurance coverage. With insurance, you'll typically pay your copay ($20-50). Without insurance, a standard visit is $150-200. We'll discuss costs before any major procedures.",
                    "keywords": ["cost", "price", "how much", "expensive", "fee"],
                },
            ],
            
            "services": [
                {
                    "question": "What services do you offer?",
                    "answer": "We offer comprehensive primary care including: annual checkups, sick visits, chronic disease management, immunizations, lab tests, minor procedures, women's health, pediatric care, and preventive care.",
                    "keywords": ["services", "offer", "do you do", "what can", "treatment"],
                },
                {
                    "question": "Do you do lab tests?",
                    "answer": "Yes! We have an on-site lab for common tests (blood work, urinalysis, etc.). Results are typically available within 24-48 hours. We'll call you with results or discuss them at a follow-up visit.",
                    "keywords": ["lab", "blood work", "test", "results", "bloodwork"],
                },
                {
                    "question": "Do you see children?",
                    "answer": "Yes, we provide pediatric care for children of all ages, from newborns to adolescents. We offer well-child visits, immunizations, and treatment for common childhood illnesses.",
                    "keywords": ["children", "kids", "pediatric", "baby", "infant"],
                },
                {
                    "question": "Do you prescribe medications?",
                    "answer": "Yes, our providers can prescribe medications when medically necessary. We send prescriptions electronically to your preferred pharmacy. We also offer prescription refills for established patients.",
                    "keywords": ["medication", "prescription", "medicine", "prescribe", "refill"],
                },
                {
                    "question": "Do you do vaccinations?",
                    "answer": "Yes, we provide all routine vaccinations including flu shots, COVID-19 vaccines, childhood immunizations, and travel vaccines. Walk-ins welcome for flu shots during flu season!",
                    "keywords": ["vaccine", "vaccination", "immunization", "flu shot", "covid"],
                },
            ],
            
            "providers": [
                {
                    "question": "Who are your providers?",
                    "answer": f"Our medical team includes: {', '.join(CLINIC_CONFIG['providers'])}. All our providers are board-certified and have years of experience in family medicine.",
                    "keywords": ["provider", "doctor", "physician", "who", "staff"],
                },
                {
                    "question": "Can I choose my provider?",
                    "answer": "Absolutely! When scheduling, just let us know which provider you'd like to see. If you're a new patient, we can also help match you with a provider based on your needs.",
                    "keywords": ["choose", "select", "pick", "prefer", "specific doctor"],
                },
                {
                    "question": "Are your doctors accepting new patients?",
                    "answer": "Yes! All our providers are currently accepting new patients. We'd love to welcome you to our practice. Would you like to schedule a new patient visit?",
                    "keywords": ["new patient", "accepting", "taking new"],
                },
            ],
            
            "emergency": [
                {
                    "question": "Is this an emergency?",
                    "answer": "For life-threatening emergencies (chest pain, difficulty breathing, severe bleeding, etc.), call 911 or go to the nearest emergency room immediately. For urgent but non-emergency care, we offer same-day appointments.",
                    "keywords": ["emergency", "urgent", "911", "er", "immediate"],
                },
                {
                    "question": "What should I do after hours?",
                    "answer": "For urgent medical concerns after hours, call our main number (555) 123-4567 - you'll reach our answering service who can connect you with the on-call provider. For emergencies, call 911.",
                    "keywords": ["after hours", "night", "weekend", "closed", "on-call"],
                },
            ],
            
            "covid": [
                {
                    "question": "Do you test for COVID-19?",
                    "answer": "Yes, we offer both rapid and PCR COVID-19 testing. Rapid tests give results in 15 minutes, PCR tests in 24-48 hours. Please call ahead to schedule a testing appointment.",
                    "keywords": ["covid", "coronavirus", "covid-19", "test", "pcr"],
                },
                {
                    "question": "What are your COVID safety measures?",
                    "answer": "We follow all CDC guidelines: enhanced cleaning, air filtration, hand sanitizer stations, and social distancing in waiting areas. Masks are available if needed.",
                    "keywords": ["covid", "safety", "mask", "precaution", "protocol"],
                },
            ],
        }
        
        # Build a flat list of all FAQs for searching
        self.all_faqs = []
        for category, questions in self.faqs.items():
            for faq in questions:
                faq["category"] = category
                self.all_faqs.append(faq)
    
    def search_faqs(self, query: str, limit: int = 5) -> List[Dict[str, Any]]:
        """
        Search FAQs by keyword matching.
        
        Args:
            query: Search query from user
            limit: Maximum number of results to return
            
        Returns:
            List of matching FAQ dictionaries with relevance scores
        """
        query_lower = query.lower()
        results = []
        
        for faq in self.all_faqs:
            score = 0
            
            # Check if query matches keywords
            for keyword in faq["keywords"]:
                if keyword in query_lower:
                    score += 10
            
            # Check if query words appear in question
            question_lower = faq["question"].lower()
            for word in query_lower.split():
                if len(word) > 3 and word in question_lower:
                    score += 5
            
            # Check if query words appear in answer
            answer_lower = faq["answer"].lower()
            for word in query_lower.split():
                if len(word) > 3 and word in answer_lower:
                    score += 2
            
            if score > 0:
                results.append({
                    "faq": faq,
                    "score": score,
                })
        
        # Sort by score (highest first) and return top results
        results.sort(key=lambda x: x["score"], reverse=True)
        return [r["faq"] for r in results[:limit]]
    
    def get_faq_by_category(self, category: str) -> List[Dict[str, str]]:
        """
        Get all FAQs in a specific category.
        
        Args:
            category: Category name (e.g., "appointments", "insurance_and_payment")
            
        Returns:
            List of FAQ dictionaries in that category
        """
        return self.faqs.get(category, [])
    
    def get_all_categories(self) -> List[str]:
        """Get list of all FAQ categories."""
        return list(self.faqs.keys())
    
    def get_clinic_info(self) -> Dict[str, Any]:
        """Get basic clinic information."""
        return self.clinic_info
    
    def answer_question(self, query: str) -> Optional[str]:
        """
        Get a direct answer to a question.
        Returns the best matching FAQ answer or None if no good match.
        
        Args:
            query: User's question
            
        Returns:
            Answer string or None
        """
        results = self.search_faqs(query, limit=1)
        
        if results and len(results) > 0:
            # Return answer if we found a good match
            return results[0]["answer"]
        
        return None
    
    def format_search_results(self, results: List[Dict[str, Any]]) -> str:
        """
        Format search results into a readable string.
        
        Args:
            results: List of FAQ dictionaries
            
        Returns:
            Formatted string with questions and answers
        """
        if not results:
            return "I couldn't find any information about that. Please call us at (555) 123-4567 for assistance."
        
        output = []
        for i, faq in enumerate(results, 1):
            output.append(f"{i}. **{faq['question']}**")
            output.append(f"   {faq['answer']}")
            output.append("")  # Blank line
        
        return "\n".join(output)


# Create singleton instance
knowledge_base = FAQKnowledgeBase()


# Function calling wrapper for Gemini
def search_knowledge_base_function(query: str) -> str:
    """
    Wrapper function for Gemini function calling.
    Searches the knowledge base and returns formatted results.
    """
    results = knowledge_base.search_faqs(query, limit=3)
    
    if results:
        # Return the best match answer directly
        best_match = results[0]
        response = f"**{best_match['question']}**\n\n{best_match['answer']}"
        
        # If there are other relevant FAQs, mention them
        if len(results) > 1:
            response += "\n\nRelated questions:\n"
            for faq in results[1:]:
                response += f"- {faq['question']}\n"
        
        return response
    else:
        return f"I don't have specific information about that. You can call us at {CLINIC_CONFIG['phone']} for more details, or I can help you schedule an appointment to discuss this with a provider."


# Gemini function calling declaration
SEARCH_KNOWLEDGE_BASE_DECLARATION = {
    "name": "search_knowledge_base",
    "description": "Search the clinic's knowledge base for information about hours, services, insurance, appointments, and other common questions",
    "parameters": {
        "type": "object",
        "properties": {
            "query": {
                "type": "string",
                "description": "The user's question or search query (e.g., 'what are your hours', 'do you accept insurance')",
            },
        },
        "required": ["query"],
    },
}
