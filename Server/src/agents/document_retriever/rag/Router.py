
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from enum import Enum


class QueryType(Enum):
    SEMANTIC = "semantic"      # Complex medical questions, symptom descriptions
    KEYWORD = "keyword"        # Specific term lookups, definitions
    HYBRID = "hybrid"          # Mixed queries requiring both approaches


class QueryRouter:
    """
    Routes queries to appropriate retrieval strategies based on query characteristics.
    
    Uses an LLM to intelligently classify the type of query and determine
    the best retrieval strategy (semantic, keyword, or hybrid).
    """
    
    def __init__(self, llm: ChatGoogleGenerativeAI):
        """
        Initialize the query router.
        
        Args:
            llm: Language model for query classification
        """
        self.llm = llm
        self.router_prompt = ChatPromptTemplate.from_template(
            """You are a medical query classification specialist. Your task is to analyze questions and determine the most appropriate search type.

SEARCH TYPES:
1. **semantic** - Use for complex questions, symptom descriptions, questions about causes/mechanisms
   Example: "Why does my skin itch and get red rashes when it's hot?"
   
2. **keyword** - Use for terminology lookup, definitions, specific disease names
   Example: "What is Psoriasis?", "Define herpes zoster"
   
3. **hybrid** - Use for questions combining terminology lookup and explanation
   Example: "What is atopic dermatitis and how is it treated?"

TASK: Analyze the question below and answer with EXACTLY ONE OF THREE WORDS: semantic, keyword, or hybrid

Question: {question}

Search type (answer one word only):"""
        )
        
        self.router_chain = self.router_prompt | self.llm | StrOutputParser()
    
    def route(self, question: str) -> QueryType:
        """
        Route a query to the appropriate retrieval strategy.
        
        Args:
            question: The user's question to route
            
        Returns:
            QueryType enum indicating the routing decision
        """
        try:
            result = self.router_chain.invoke({"question": question}).strip().lower()
            
            # Parse the result and map to QueryType
            if "semantic" in result:
                return QueryType.SEMANTIC
            elif "keyword" in result:
                return QueryType.KEYWORD
            elif "hybrid" in result:
                return QueryType.HYBRID
            else:
                # Default to semantic if unclear
                print(f"WARNING: Router output unclear: '{result}', defaulting to semantic")
                return QueryType.SEMANTIC
                
        except Exception as e:
            print(f"WARNING: Router error: {e}, defaulting to semantic")
            return QueryType.SEMANTIC
    
    def route_with_explanation(self, question: str) -> tuple[QueryType, str]:
        """
        Route a query and provide explanation for the routing decision.
        
        Args:
            question: The user's question to route
            
        Returns:
            Tuple of (QueryType, explanation string)
        """
        query_type = self.route(question)
        
        explanations = {
            QueryType.SEMANTIC: "Tìm kiếm ngữ nghĩa - Phù hợp với câu hỏi phức tạp và mô tả triệu chứng",
            QueryType.KEYWORD: "Tìm kiếm từ khóa - Phù hợp với tra cứu thuật ngữ và định nghĩa",
            QueryType.HYBRID: "Tìm kiếm kết hợp - Phù hợp với câu hỏi cần cả thuật ngữ và giải thích"
        }
        
        return query_type, explanations.get(query_type, "")


def create_router(llm: ChatGoogleGenerativeAI) -> QueryRouter:
    """
    Factory function to create a QueryRouter instance.
    
    Args:
        llm: Language model for query classification
        
    Returns:
        Configured QueryRouter instance
    """
    return QueryRouter(llm)

