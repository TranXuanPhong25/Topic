"""Medical Clinic Chatbot using Google Gemini 2.0 Flash"""
import os
import google.generativeai as genai
from typing import Optional, Dict, Any, List
from datetime import datetime
from sqlalchemy.orm import Session
from configs.config import GOOGLE_API_KEY, MODEL_NAME, SYSTEM_INSTRUCTION
from handlers.appointment import (
    schedule_appointment_function,
    SCHEDULE_APPOINTMENT_DECLARATION
)
from agents.vision.gemini_vision_analyzer import GeminiVisionAnalyzer
from todo_manager import create_todo_function, CREATE_TODO_DECLARATION
from knowledge_base import (
    search_knowledge_base_function,
    SEARCH_KNOWLEDGE_BASE_DECLARATION
)
from database import SessionLocal
from models import Conversation


class ChatBot:
    """
    Main chatbot class that handles conversations using Google Gemini.
    
    This chatbot can:
    - Have natural conversations with patients
    - Schedule appointments (when integrated with function tools)
    - Answer FAQs about the clinic
    - Create tasks for staff follow-ups
    """
    
    def __init__(self, api_key: Optional[str] = None):
        """
        Initialize the chatbot with Google Gemini.
        
        Args:
            api_key: Google API key (defaults to environment variable)
        """
        self.api_key = api_key or GOOGLE_API_KEY
        
        if not self.api_key:
            raise ValueError(
                "Google API key not found! Please set GOOGLE_API_KEY in your .env file.\n"
                "Get your free API key at: https://aistudio.google.com/app/apikey"
            )
        
        # Configure Gemini
        genai.configure(api_key=self.api_key)
        
        # Define function tools for Gemini
        self.tools = [
            {
                "function_declarations": [
                    SCHEDULE_APPOINTMENT_DECLARATION,
                    CREATE_TODO_DECLARATION,
                    SEARCH_KNOWLEDGE_BASE_DECLARATION,
                ]
            }
        ]
        
        # Initialize the model with system instructions and tools
        self.model = genai.GenerativeModel(
            model_name=MODEL_NAME,
            system_instruction=SYSTEM_INSTRUCTION,
            tools=self.tools,
        )
        
        # Store chat sessions (in-memory cache of Gemini chats)
        self.sessions: Dict[str, Any] = {}
        
        # Map function names to actual Python functions
        self.function_handlers = {
            "schedule_appointment": schedule_appointment_function,
            "create_todo": create_todo_function,
            "search_knowledge_base": search_knowledge_base_function,
        }
        
        # Database session for persisting conversations
        self.db: Optional[Session] = None
    
    def set_db(self, db: Session):
        """Set database session for persisting conversations"""
        self.db = db
    
    def save_message_to_db(self, session_id: str, role: str, content: str, patient_name: Optional[str] = None):
        """
        Save a message to the database for conversation history.
        
        Args:
            session_id: Conversation session ID
            role: Message role (user, assistant, system)
            content: Message content
            patient_name: Optional patient name
        """
        if not self.db:
            return  # Skip if no database session
        
        try:
            conversation = Conversation(
                session_id=session_id,
                role=role,
                content=content,
                patient_name=patient_name,
                timestamp=datetime.utcnow()
            )
            self.db.add(conversation)
            self.db.commit()
        except Exception as e:
            print(f"Warning: Could not save message to database: {e}")
            self.db.rollback()
    
    def load_history_from_db(self, session_id: str, limit: int = 20) -> List[Dict[str, Any]]:
        """
        Load conversation history from database.
        
        Args:
            session_id: Conversation session ID
            limit: Maximum number of messages to load (default: 20)
            
        Returns:
            List of conversation messages
        """
        if not self.db:
            return []
        
        try:
            conversations = (
                self.db.query(Conversation)
                .filter(Conversation.session_id == session_id)
                .order_by(Conversation.timestamp.asc())
                .limit(limit)
                .all()
            )
            
            return [
                {
                    "role": conv.role,
                    "content": conv.content,
                    "timestamp": conv.timestamp.isoformat() if conv.timestamp else None,
                }
                for conv in conversations
            ]
        except Exception as e:
            print(f"Warning: Could not load history from database: {e}")
            return []
    
    def restore_session_from_db(self, session_id: str) -> bool:
        """
        Restore a chat session from database history.
        Loads previous messages and initializes Gemini chat with history.
        
        Args:
            session_id: Conversation session ID
            
        Returns:
            True if history was restored, False otherwise
        """
        history = self.load_history_from_db(session_id)
        
        if not history or len(history) == 0:
            return False
        
        # Convert database history to Gemini format
        gemini_history = []
        for msg in history:
            if msg["role"] in ["user", "model"]:  # Only user and model messages
                gemini_history.append({
                    "role": msg["role"],
                    "parts": [{"text": msg["content"]}]
                })
        
        # Start chat with history
        if gemini_history:
            try:
                self.sessions[session_id] = self.model.start_chat(history=gemini_history)
                return True
            except Exception as e:
                print(f"Warning: Could not restore session from history: {e}")
                return False
        
        return False
    
    def start_chat(self, session_id: str) -> Any:
        """
        Start a new chat session or retrieve an existing one.
        Attempts to restore from database history if available.
        
        Args:
            session_id: Unique identifier for this conversation
            
        Returns:
            Chat session object
        """
        if session_id not in self.sessions:
            # Try to restore from database first
            if self.db and not self.restore_session_from_db(session_id):
                # No history found, start fresh
                self.sessions[session_id] = self.model.start_chat(history=[])
            elif not self.db:
                # No database, start fresh
                self.sessions[session_id] = self.model.start_chat(history=[])
        
        return self.sessions[session_id]
    
    def send_message(self, message: str, session_id: str = "default", patient_name: Optional[str] = None) -> str:
        """
        Send a message to the chatbot and get a response.
        Handles function calling and persists conversation to database.
        
        Args:
            message: User's message
            session_id: Conversation session ID (default: "default")
            patient_name: Optional patient name for database tracking
            
        Returns:
            Bot's response as a string
        """
        try:
            # Save user message to database
            self.save_message_to_db(session_id, "user", message, patient_name)
            
            # Get or create chat session
            chat = self.start_chat(session_id)
            
            # Send message and get response
            response = chat.send_message(message)
            
            # Check if Gemini wants to call a function
            if response.candidates[0].content.parts:
                for part in response.candidates[0].content.parts:
                    # Check if this part is a function call
                    if hasattr(part, 'function_call') and part.function_call:
                        function_call = part.function_call
                        function_name = function_call.name
                        
                        # Get the function arguments
                        function_args = {}
                        for key, value in function_call.args.items():
                            function_args[key] = value
                        
                        print(f"🔧 Calling function: {function_name}")
                        print(f"   Arguments: {function_args}")
                        
                        # Call the actual Python function
                        if function_name in self.function_handlers:
                            function_response = self.function_handlers[function_name](**function_args)
                            
                            # Send function response back to Gemini
                            response = chat.send_message(
                                genai.protos.Content(
                                    parts=[genai.protos.Part(
                                        function_response=genai.protos.FunctionResponse(
                                            name=function_name,
                                            response={"result": function_response}
                                        )
                                    )]
                                )
                            )
                            
                            # Save assistant response to database
                            bot_response = response.text
                            self.save_message_to_db(session_id, "model", bot_response, patient_name)
                            return bot_response
                        else:
                            error_msg = f"Function {function_name} not implemented yet."
                            self.save_message_to_db(session_id, "model", error_msg, patient_name)
                            return error_msg
            
            # Return text response if no function call
            bot_response = response.text
            self.save_message_to_db(session_id, "model", bot_response, patient_name)
            return bot_response
            
        except Exception as e:
            # Handle errors gracefully
            print(f"Error in chatbot: {e}")
            import traceback
            traceback.print_exc()
            return (
                "I apologize, but I'm having trouble processing your request right now. "
                "Please try again, or call us at (555) 123-4567 for immediate assistance."
            )
    
    def get_chat_history(self, session_id: str = "default", from_db: bool = True) -> List[Dict[str, str]]:
        """
        Get the conversation history for a session.
        
        Args:
            session_id: Conversation session ID
            from_db: If True, load from database; otherwise use in-memory session
            
        Returns:
            List of messages with roles and content
        """
        # Try database first if requested
        if from_db and self.db:
            db_history = self.load_history_from_db(session_id, limit=100)
            if db_history:
                return db_history
        
        # Fall back to in-memory session
        if session_id not in self.sessions:
            return []
        
        chat = self.sessions[session_id]
        history = []
        
        for message in chat.history:
            history.append({
                "role": message.role,
                "content": message.parts[0].text if message.parts else ""
            })
        
        return history
    
    def clear_session(self, session_id: str = "default"):
        """
        Clear a chat session (start fresh conversation).
        
        Args:
            session_id: Conversation session ID to clear
        """
        if session_id in self.sessions:
            del self.sessions[session_id]
    
    async def handle_image_message(
        self,
        message: str,
        image_data: str,
        session_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Handle chat messages with images using multi-agent analysis.
        
        This method:
        1. Initializes the multi-agent system (LangGraph)
        2. Runs vision analysis (Hugging Face models)
        3. Performs medical assessment (Gemini)
        4. Determines risk level and recommendations
        
        Args:
            message: User's text message (symptoms description)
            image_data: Base64 encoded image
            session_id: Optional session ID for context
        
        Returns:
            {
                "response": "Formatted response for user",
                "analysis": {...},  # Full analysis details
                "type": "image_analysis"
            }
        """
        
        # Initialize MedGemma Vision analyzer (Gemini Vision + MedGemma-4B)
        analyzer = GeminiVisionAnalyzer(
            google_api_key=self.api_key,
        )
        
        # Run analysis
        try:
            analysis = analyzer.analyze_image(
                image_data=image_data,
                symptoms_text=message
            )
            
            # Format response for user
            response = self._format_image_analysis_response(analysis)
            
            # Save to conversation history
            if session_id and self.db:
                self.save_message_to_db(
                    session_id=session_id,
                    role="user",
                    content=f"[IMAGE] {message}"
                )
                self.save_message_to_db(
                    session_id=session_id,
                    role="assistant",
                    content=response
                )
            
            return {
                "response": response,
                "analysis": analysis,
                "type": "image_analysis"
            }
        
        except Exception as e:
            error_response = (
                f"Xin lỗi, tôi gặp lỗi khi phân tích ảnh: {str(e)}. "
                "Vui lòng thử lại hoặc liên hệ bác sĩ trực tiếp tại (555) 123-4567."
            )
            
            return {
                "response": error_response,
                "error": str(e),
                "type": "error"
            }
    
    def _format_image_analysis_response(self, analysis: Dict[str, Any]) -> str:
        """
        Format Gemini vision analysis results into user-friendly response.
        
        Args:
            analysis: Analysis from Gemini Vision
        
        Returns:
            Formatted Vietnamese response
        """
        risk_emoji = {
            "low": "🟢",
            "moderate": "🟡",
            "high": "🟠",
            "urgent": "🔴"
        }
        
        risk = analysis.get("risk_level", "moderate").lower()
        emoji = risk_emoji.get(risk, "⚪")
        # Build response
        response = f"""📸 **Phân Tích Hình Ảnh**

                        🔍 **Những gì tôi thấy:**
                        {analysis.get('visual_description', 'Không xác định được')}

                        🩺 **Đánh giá y tế:**
                        {analysis.get('medical_analysis', 'Cần thêm thông tin')}

                        {emoji} **Mức độ rủi ro:** {risk.upper()}

                        📋 **Khuyến nghị:**
                        """
        
        # Add recommendations
        for i, rec in enumerate(analysis.get('recommendations', []), 1):
            response += f"\n{i}. {rec}"
        
        # Add disclaimer
        confidence_pct = int(analysis.get('confidence', 0.85) * 100)
        response += f"\n\n⚠️ **Lưu ý quan trọng:** Đây chỉ là đánh giá sơ bộ với độ tin cậy {confidence_pct}%. "
        response += "Đây KHÔNG phải là chẩn đoán y khoa chính thức. "
        response += "Vui lòng tham khảo ý kiến bác sĩ chuyên khoa để được chẩn đoán và điều trị chính xác."
        
        # Add emergency warning if urgent
        if risk == 'urgent':
            response += "\n\n🚨 **KHẨN CẤP:** Tình trạng này có thể nghiêm trọng. "
            response += "Vui lòng đến cấp cứu hoặc gọi 115 ngay lập tức!"
        
        return response


def main():
    """
    Simple test function to try out the chatbot.
    Run this file directly to have a conversation!
    """
    print("=" * 60)
    print("Medical Clinic Chatbot - Powered by Google Gemini 2.0 Flash")
    print("=" * 60)
    print("\nWelcome! I'm here to help with appointments and questions.")
    print("Type 'quit' to exit, 'history' to see conversation history.\n")
    
    try:
        bot = ChatBot()
        session_id = "cli-test"
        
        while True:
            # Get user input
            user_input = input("\nYou: ").strip()
            
            if not user_input:
                continue
            
            if user_input.lower() == 'quit':
                print("\nThank you for chatting! Take care! 👋")
                break
            
            if user_input.lower() == 'history':
                print("\n--- Conversation History ---")
                history = bot.get_chat_history(session_id)
                for msg in history:
                    role = "You" if msg["role"] == "user" else "Bot"
                    print(f"{role}: {msg['content'][:100]}...")
                print("--- End History ---\n")
                continue
            
            # Get bot response
            response = bot.send_message(user_input, session_id)
            print(f"\nBot: {response}")
    
    except ValueError as e:
        print(f"\n❌ Error: {e}")
        print("\nTo use this chatbot:")
        print("1. Get a free API key from: https://aistudio.google.com/app/apikey")
        print("2. Add it to your .env file: GOOGLE_API_KEY=your-key-here")
    except KeyboardInterrupt:
        print("\n\nGoodbye! 👋")
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")


if __name__ == "__main__":
    main()
