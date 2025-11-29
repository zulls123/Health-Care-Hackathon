# orchestrator.py - Multi-Agent System with Legal Compliance & Language Critic
import asyncio
import json
from typing import Dict, List, Optional, Tuple
from datetime import datetime
from database import SQLiteDBManager

class AgentOrchestrator:
    """
    Central orchestrator managing the multi-agent advisory system.
    Enforces strict sequencing and legal compliance for South African context.
    """
    
    def __init__(self, db_manager: SQLiteDBManager, ark_caller):
        self.db = db_manager
        self.ark_caller = ark_caller
        
        # Agent definitions
        self.agents = {
            "health": "health-companion-agent",
            "financial": "financial-coach-agent",
            "legal": "legal-compliance-agent",
            "critic": "language-critic-agent"
        }
    
    async def process_user_request(self, user_id: int, user_prompt: str, 
                                   session_id: str) -> Dict:
        """
        Main orchestration flow - executes all steps in strict sequence.
        
        Steps:
        1. Retrieve user data from database
        2. Run specialist agents in parallel (Health, Financial, Legal)
        3. Legal compliance check
        4. Critic & language agent final pass
        5. Return approved response
        """
        
        # STEP 1: Retrieve complete user profile
        user_data = await self._retrieve_user_data(user_id)
        
        if not user_data:
            return {
                "status": "error",
                "message": "Unable to retrieve user information. Please try again."
            }
        
        # STEP 2 & 3: Execute specialist agents in parallel
        specialist_responses = await self._execute_specialist_agents(
            user_prompt=user_prompt,
            user_data=user_data,
            session_id=session_id
        )
        
        # Check if legal agent blocked the response
        if specialist_responses.get("legal_blocked"):
            return {
                "status": "blocked",
                "message": specialist_responses["legal_message"]
            }
        
        # STEP 4: Run critic & language agent
        final_response = await self._execute_critic_agent(
            user_prompt=user_prompt,
            user_data=user_data,
            specialist_responses=specialist_responses,
            session_id=session_id
        )
        
        # STEP 5: Save to database and return
        self.db.save_chat_message(
            user_id=user_id,
            agent_type="Orchestrator",
            role="assistant",
            content=final_response["content"],
            session_id=session_id
        )
        
        return {
            "status": "success",
            "content": final_response["content"],
            "metadata": {
                "processed_by": ["Health Agent", "Financial Agent", 
                                "Legal Compliance Agent", "Language Critic Agent"],
                "timestamp": datetime.now().isoformat()
            }
        }
    
    async def _retrieve_user_data(self, user_id: int) -> Optional[Dict]:
        """
        STEP 1: Retrieve complete user profile from database.
        Returns structured JSON with all user information.
        """
        try:
            # Get basic user info
            conn = self.db.get_connection()
            cursor = conn.cursor()
            
            cursor.execute("""
                SELECT first_name, last_name, email, phone, date_of_birth, 
                       gender, province, city
                FROM Users
                WHERE user_id = ?
            """, (user_id,))
            
            user_row = cursor.fetchone()
            if not user_row:
                return None
            
            # Get complete profile
            profile = self.db.get_user_profile(user_id)
            
            # Structure user data
            user_data = {
                "user_id": user_id,
                "personal_details": {
                    "first_name": user_row[0],
                    "last_name": user_row[1],
                    "email": user_row[2],
                    "phone": user_row[3],
                    "date_of_birth": user_row[4].isoformat() if user_row[4] else None,
                    "age": self._calculate_age(user_row[4]) if user_row[4] else None,
                    "gender": user_row[5],
                    "location": {
                        "province": user_row[6],
                        "city": user_row[7],
                        "country": "South Africa"
                    }
                },
                "medical_profile": {
                    "medical_aid": profile.get("medical_aid"),
                    "conditions": profile.get("medical_history", []),
                    "medications": profile.get("medications", []),
                    "allergies": profile.get("allergies", [])
                },
                "financial_profile": {
                    "accounts": profile.get("financial_accounts", [])
                },
                "preferences": {
                    "language": "British English",
                    "terminology": "Germanic root preferred"
                }
            }
            
            cursor.close()
            conn.close()
            
            return user_data
            
        except Exception as e:
            print(f"Error retrieving user data: {e}")
            return None
    
    def _calculate_age(self, date_of_birth) -> int:
        """Calculate age from date of birth"""
        from datetime import date
        today = date.today()
        return today.year - date_of_birth.year - (
            (today.month, today.day) < (date_of_birth.month, date_of_birth.day)
        )
    
    async def _execute_specialist_agents(self, user_prompt: str, 
                                        user_data: Dict, 
                                        session_id: str) -> Dict:
        """
        STEP 2 & 3: Execute Health, Financial, and Legal agents in parallel.
        Legal agent reviews all outputs for compliance.
        """
        
        # Build context for specialist agents
        context = self._build_agent_context(user_data)
        
        # Prepare prompts for each agent
        health_prompt = self._build_health_prompt(user_prompt, context)
        financial_prompt = self._build_financial_prompt(user_prompt, context)
        legal_system_prompt = self._build_legal_system_prompt()
        
        # Execute Health and Financial agents in parallel
        health_task = self._call_agent("health", health_prompt, session_id)
        financial_task = self._call_agent("financial", financial_prompt, session_id)
        
        health_response, financial_response = await asyncio.gather(
            health_task, financial_task
        )
        
        # Execute Legal Compliance Agent to review outputs
        combined_output = {
            "user_prompt": user_prompt,
            "health_response": health_response,
            "financial_response": financial_response,
            "user_data_summary": self._summarize_user_data(user_data)
        }
        
        legal_review_prompt = f"""
{legal_system_prompt}

Review the following outputs for legal compliance:

USER PROMPT: {user_prompt}

HEALTH AGENT OUTPUT:
{health_response}

FINANCIAL AGENT OUTPUT:
{financial_response}

INSTRUCTIONS:
1. Identify any violations of South African medical or financial services law
2. If violations exist, respond with: "BLOCKED: [specific violation]"
3. If compliant, respond with: "APPROVED" followed by any required disclaimers
4. Be strict - when in doubt, block it
"""
        
        legal_response = await self._call_agent("legal", legal_review_prompt, session_id)
        
        # Check if legal agent blocked the response
        if "BLOCKED:" in legal_response:
            return {
                "legal_blocked": True,
                "legal_message": "I am not permitted to provide that information or recommendation under South African law.",
                "details": legal_response
            }
        
        return {
            "legal_blocked": False,
            "health": health_response,
            "financial": financial_response,
            "legal_disclaimer": legal_response.replace("APPROVED", "").strip()
        }
    
    def _build_agent_context(self, user_data: Dict) -> str:
        """Build formatted context string from user data"""
        context_parts = []
        
        # Personal details
        personal = user_data["personal_details"]
        context_parts.append(f"User: {personal['first_name']} {personal['last_name']}")
        if personal.get("age"):
            context_parts.append(f"Age: {personal['age']}")
        if personal.get("gender"):
            context_parts.append(f"Gender: {personal['gender']}")
        if personal.get("location"):
            loc = personal["location"]
            context_parts.append(f"Location: {loc['city']}, {loc['province']}, {loc['country']}")
        
        # Medical profile
        medical = user_data["medical_profile"]
        if medical.get("medical_aid"):
            ma = medical["medical_aid"]
            context_parts.append(f"\nMedical Aid: {ma['scheme_name']} ({ma['plan_type']})")
            if ma.get("membership_number"):
                context_parts.append(f"Membership: {ma['membership_number']}")
        
        if medical.get("conditions"):
            active = [c for c in medical["conditions"] if c["status"] == "Active"]
            if active:
                conds = ", ".join([c["condition"] for c in active])
                context_parts.append(f"Active Conditions: {conds}")
        
        if medical.get("medications"):
            meds = ", ".join([f"{m['name']} ({m['dosage']})" for m in medical["medications"]])
            context_parts.append(f"Current Medications: {meds}")
        
        if medical.get("allergies"):
            allergens = ", ".join([f"{a['allergen']} ({a['severity']})" 
                                  for a in medical["allergies"]])
            context_parts.append(f"Allergies: {allergens}")
        
        # Financial profile
        financial = user_data["financial_profile"]
        if financial.get("accounts"):
            for acc in financial["accounts"]:
                if acc.get("monthly_income"):
                    context_parts.append(f"\nMonthly Income: {acc['currency']} {acc['monthly_income']:,.2f}")
                if acc.get("monthly_budget"):
                    context_parts.append(f"Monthly Budget: {acc['currency']} {acc['monthly_budget']:,.2f}")
        
        return "\n".join(context_parts)
    
    def _build_health_prompt(self, user_prompt: str, context: str) -> str:
        """Build prompt for health agent with user context"""
        return f"""You are a Health Companion assistant operating in South Africa.

CRITICAL LEGAL CONSTRAINTS:
- You are NOT a registered medical practitioner
- You CANNOT diagnose conditions
- You CANNOT prescribe medications or treatments
- You CAN provide general health information and wellness guidance
- You MUST recommend users consult registered healthcare professionals for medical advice

USER CONTEXT:
{context}

USER QUERY:
{user_prompt}

Provide supportive, informational guidance while strictly adhering to legal constraints."""
    
    def _build_financial_prompt(self, user_prompt: str, context: str) -> str:
        """Build prompt for financial agent with user context"""
        return f"""You are a Financial Guidance assistant operating in South Africa.

CRITICAL LEGAL CONSTRAINTS:
- You are NOT a registered financial services provider under FAIS
- You CANNOT provide specific investment advice or product recommendations
- You CAN provide general financial literacy and budgeting guidance
- You MUST recommend users consult licensed financial advisors for financial product advice

USER CONTEXT:
{context}

USER QUERY:
{user_prompt}

Provide educational financial guidance while strictly adhering to legal constraints."""
    
    def _build_legal_system_prompt(self) -> str:
        """Build system prompt for legal compliance agent"""
        return """You are a South African Legal Compliance Agent specializing in:
- National Health Act 61 of 2003
- Health Professions Act 56 of 1974
- Allied Health Professions Act
- Medicine and Related Substances Act
- Consumer Protection Act 68 of 2008
- HPCSA and AHPCSA guidelines
- Financial Advisory and Intermediary Services Act (FAIS)

YOUR ROLE:
Block any content that constitutes:
1. Medical diagnosis, prescription, or treatment by non-registered practitioners
2. Financial product advice by non-licensed providers
3. Any practice that violates South African professional registration requirements

Be strict. When uncertain, BLOCK the content."""
    
    def _summarize_user_data(self, user_data: Dict) -> str:
        """Create brief summary of user data for legal review"""
        personal = user_data["personal_details"]
        medical = user_data["medical_profile"]
        
        summary = f"User is {personal.get('age', 'unknown')} years old in {personal['location']['province']}, South Africa."
        
        if medical.get("conditions"):
            summary += f" Has medical history on file."
        
        if medical.get("medical_aid"):
            summary += f" Has medical aid coverage."
        
        return summary
    
    async def _execute_critic_agent(self, user_prompt: str, user_data: Dict,
                                    specialist_responses: Dict, 
                                    session_id: str) -> Dict:
        """
        STEP 4: Execute Language Critic Agent for final review and rewriting.
        Ensures Germanic roots and British English, validates against user prompt.
        """
        
        critic_prompt = f"""You are the Language Critic Agent with two critical responsibilities:

1. LANGUAGE REQUIREMENTS:
   - Rewrite ALL words to Germanic root equivalents where possible
   - Use British English exclusively (organise, behaviour, centre, licence as noun)
   - Examples of required changes:
     * "utilise" → "use"
     * "purchase" → "buy"
     * "commence" → "begin"
     * "assist" → "help"
     * "obtain" → "get"
     * "provide" → "give"
     * "require" → "need"
     * "additional" → "further"
     * "medication" → "medicine" (when contextually appropriate)

2. CONTENT VALIDATION:
   - Critically evaluate every recommendation against the original user prompt
   - Remove any advice not explicitly requested
   - Qualify or remove exaggerations
   - Ensure tone is formal but clear, never patronising
   - Keep response focused and relevant

ORIGINAL USER PROMPT:
{user_prompt}

HEALTH AGENT RESPONSE:
{specialist_responses.get('health', '')}

FINANCIAL AGENT RESPONSE:
{specialist_responses.get('financial', '')}

LEGAL DISCLAIMER:
{specialist_responses.get('legal_disclaimer', '')}

INSTRUCTIONS:
Rewrite the combined response following the language requirements and content validation rules.
Output only the final, approved response that will be shown to the user.
"""
        
        final_response = await self._call_agent("critic", critic_prompt, session_id)
        
        return {
            "content": final_response,
            "processed_by_critic": True
        }
    
    async def _call_agent(self, agent_type: str, prompt: str, 
                         session_id: str) -> str:
        """
        Call individual agent via Ark API.
        This is an async wrapper around the synchronous ark_caller.
        """
        # Run synchronous call in executor to avoid blocking
        loop = asyncio.get_event_loop()
        response = await loop.run_in_executor(
            None,
            self.ark_caller,
            agent_type,
            prompt,
            session_id
        )
        return response if response else ""


# Integration function for existing app.py
def create_orchestrator(db_manager: SQLiteDBManager, ark_base_url: str, 
                       ark_api_key: str, agent_ids: Dict) -> AgentOrchestrator:
    """
    Factory function to create orchestrator with Ark API caller.
    """
    
    def ark_caller(agent_type: str, prompt: str, session_id: str) -> str:
        """
        Synchronous wrapper for calling Ark agents.
        Reuses existing call_ark_agent logic.
        """
        import requests
        import uuid
        import time
        
        agent_id = agent_ids.get(agent_type)
        if not agent_id:
            return f"Error: Unknown agent type: {agent_type}"
        
        headers = {"Content-Type": "application/json"}
        if ark_api_key:
            headers["Authorization"] = f"Bearer {ark_api_key}"
        
        query_id = f"chat-{str(uuid.uuid4())}"
        
        payload = {
            "name": query_id,
            "namespace": "default",
            "type": "messages",
            "input": [{"role": "user", "content": prompt}],
            "sessionId": session_id,
            "targets": [{"name": agent_id, "type": "agent"}],
            "timeout": "5m0s",
            "ttl": "720h0m0s",
        }
        
        try:
            # Create query
            create_url = f"{ark_base_url}/queries/"
            resp = requests.post(create_url, headers=headers, json=payload, timeout=90)
            
            if resp.status_code not in (200, 201):
                return f"Error creating query: {resp.status_code}"
            
            # Poll for result
            result_url = f"{ark_base_url}/queries/{query_id}"
            for attempt in range(40):
                time.sleep(1.0 if attempt < 5 else 1.5)
                poll = requests.get(result_url, headers=headers, timeout=30)
                
                if poll.status_code != 200:
                    continue
                
                data = poll.json()
                status = data.get("status", {})
                
                if status.get("phase") == "done":
                    responses = status.get("responses", [])
                    if not responses:
                        return "No response from agent."
                    
                    raw_content = responses[0].get("raw")
                    if not raw_content:
                        return responses[0].get("content", "Empty response")
                    
                    try:
                        parsed = json.loads(raw_content)
                        for msg in parsed:
                            if msg.get("role") == "assistant":
                                return msg.get("content", "").strip()
                    except:
                        pass
                    
                    return raw_content.strip()
                
                elif status.get("phase") in ("failed", "cancelled"):
                    return "Agent failed to process request."
            
            return "Agent timeout - please try again."
            
        except Exception as e:
            return f"Connection error: {str(e)}"
    
    return AgentOrchestrator(db_manager, ark_caller)