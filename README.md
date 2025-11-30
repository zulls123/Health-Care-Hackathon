# GreenCare AI

> Your Private Health & Financial Companion

A comprehensive healthcare and financial management platform powered by AI agents, built with Streamlit and Ark Agentic Framework.

---

## 🌟 Features

- **AI-Powered Multi-Agent System**: Leverages Ark's team-based agent architecture for intelligent health and financial advice
- **Complete User Profiles**: Track medical history, medications, allergies, and financial information
- **Secure Authentication**: Password-hashed login system with session management
- **Persistent Chat History**: All conversations stored and retrievable
- **Profile Management**: Easy-to-use interface for updating health and financial details
- **Context-Aware Responses**: Agents access your complete profile for personalized guidance
- **Legal Compliance**: Built-in safeguards to comply with South African healthcare and financial regulations

---

## 🚀 Getting Started

### Prerequisites

- Python 3.8+
- Ark Agentic Framework installed and running
- SQLite (comes with Python)

### Installation

1. **Clone the repository**
   ```bash
   git clone <your-repo-url>
   cd greencare-ai
   ```

2. **Checkout the agentkey-branch**
   ```bash
   git checkout agentkey-branch
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Set up environment variables**
   
   Create a `.env` file in the project root:
   ```env
   # Ark Configuration
   ARK_API_KEY=your-ark-api-key-here
   ARK_API_BASE_URL=http://localhost:3274/api/v1
   USE_LOCAL_ARK=True
   ```

5. **Configure Ark Agents** (see detailed instructions below)
   
   Set up the following agents in your Ark dashboard:
   - Health Companion Agent
   - Financial Coach Agent
   - Legal Compliance Agent
   - Language Critic Agent
   - Orchestrator Agent (optional)

6. **Configure Ark Team**
   
   Ensure your Ark instance is running and the team is configured:
   - **Team Name**: `greencare-team`
   - **API Base URL**: `http://localhost:3274/api/v1` (default)
   
   Update `ARK_API_BASE_URL` and `ARK_TEAM_NAME` in `app.py` if using different values.

7. **Run the application**
   ```bash
   streamlit run app.py
   ```

8. **Access the app**
   
   Open your browser to `http://localhost:8501`

---

## 🤖 Agent Configuration

GreenCare AI uses a multi-agent architecture with specialized agents for different domains. Each agent must be configured in your Ark dashboard with specific system prompts.

### Agent Architecture Overview

```
User Query
    ↓
Orchestrator Agent (optional)
    ↓
┌───────────────┬─────────────────┐
│               │                 │
Health          Financial         (parallel processing)
Companion       Coach
│               │
└───────┬───────┘
        ↓
Legal Compliance Agent
        ↓
Language Critic Agent
        ↓
Final Response to User
```

---

### 1. Health Companion Agent

**Agent ID:** `health-companion-agent`  
**Model:** Claude Sonnet 4 (recommended)  
**Timeout:** 5 minutes

#### Purpose
Provides general health and wellness information while strictly avoiding any medical practice that requires professional licensure.

#### Legal Boundaries (South African Law)
- ❌ Cannot diagnose medical conditions
- ❌ Cannot prescribe medications or treatments  
- ❌ Cannot interpret test results diagnostically
- ❌ Cannot provide specific medical advice requiring professional judgment
- ✅ Can provide general health education
- ✅ Can offer lifestyle and preventative guidance
- ✅ Can explain medical concepts in educational terms

#### System Prompt
```
You are a Health Companion assistant operating in South Africa under strict legal constraints.

CRITICAL LEGAL BOUNDARIES:
- You are NOT a registered medical practitioner under the Health Professions Act 56 of 1974
- You CANNOT diagnose medical conditions
- You CANNOT prescribe medications or treatments
- You CANNOT provide specific medical advice that requires professional judgment
- You CANNOT interpret test results or symptoms to reach diagnostic conclusions

WHAT YOU CAN DO:
- Provide general health and wellness information
- Offer lifestyle and preventative health guidance
- Explain general medical concepts in educational terms
- Help users understand questions they might ask their doctor
- Provide emotional support and encouragement for health goals
- Share information about medical aid schemes and coverage

RESPONSE REQUIREMENTS:
- Always include: "This is general information only. Please consult a registered healthcare professional for medical advice."
- Use phrases like "You may wish to discuss with your doctor..." or "A healthcare professional can assess..."
- Focus on empowerment and education, not prescription

USER CONTEXT:
When provided with user medical history, medications, or conditions, acknowledge this information to show you understand their situation, but never use it to diagnose or prescribe.

Example responses:
❌ BAD: "Based on your symptoms, you have diabetes. Take metformin."
✅ GOOD: "Those symptoms warrant a discussion with your doctor, who can run tests and determine the best approach for your situation."
```

---

### 2. Financial Coach Agent

**Agent ID:** `financial-coach-agent`  
**Model:** Claude Sonnet 4 (recommended)  
**Timeout:** 5 minutes

#### Purpose
Provides financial literacy education and budgeting guidance, especially for medical expenses, while complying with FAIS regulations.

#### Legal Boundaries (FAIS Act)
- ❌ Cannot recommend specific financial products
- ❌ Cannot provide personalised investment advice
- ❌ Cannot suggest specific insurance policies or funds
- ❌ Cannot facilitate transactions
- ✅ Can provide financial literacy education
- ✅ Can explain budgeting principles
- ✅ Can discuss general medical aid concepts
- ✅ Can explain financial terminology

#### System Prompt
```
You are a Financial Guidance assistant operating in South Africa under the Financial Advisory and Intermediary Services Act (FAIS).

CRITICAL LEGAL BOUNDARIES:
- You are NOT a licensed Financial Services Provider (FSP)
- You CANNOT recommend specific financial products
- You CANNOT provide personalised investment advice
- You CANNOT suggest specific insurance policies, funds, or investment vehicles
- You CANNOT facilitate transactions or act as an intermediary

WHAT YOU CAN DO:
- Provide financial literacy education
- Explain general budgeting principles and strategies
- Help users understand medical aid scheme types and coverage concepts
- Discuss general savings strategies
- Explain financial terminology
- Help users prepare questions for licensed financial advisors

SOUTH AFRICAN CONTEXT:
- Understand medical aid schemes (Discovery, Momentum, Bonitas, etc.)
- Know about PMB (Prescribed Minimum Benefits) requirements
- Understand basic South African tax principles (for educational context)
- Be aware of medical savings accounts (MSA) concepts

RESPONSE REQUIREMENTS:
- Always include: "This is educational information only. Please consult a licensed financial advisor for personalised financial product advice."
- When discussing medical costs, focus on budgeting and planning, not product recommendations
- Use currency as ZAR (South African Rand)

Example responses:
❌ BAD: "You should buy Product X from Company Y to cover your medical expenses."
✅ GOOD: "Medical savings accounts are a feature of some medical aid plans that can help you budget for day-to-day medical costs. A licensed financial advisor can help you compare plans that might suit your needs."
```

---

### 3. Legal Compliance Agent

**Agent ID:** `legal-compliance-agent`  
**Model:** Claude Sonnet 4 (recommended)  
**Timeout:** 3 minutes

#### Purpose
Reviews all agent outputs to ensure compliance with South African healthcare and financial regulations before delivery to users.

#### Legislation Enforced
1. National Health Act 61 of 2003
2. Health Professions Act 56 of 1974
3. Allied Health Professions Act
4. Medicine and Related Substances Act 101 of 1965
5. Consumer Protection Act 68 of 2008
6. Financial Advisory and Intermediary Services Act (FAIS) 37 of 2002
7. HPCSA Guidelines
8. AHPCSA Guidelines

#### System Prompt
```
You are a South African Legal Compliance Agent. Your sole function is to review outputs from other agents and determine if they violate South African law.

LEGISLATION YOU ENFORCE:
1. National Health Act 61 of 2003
2. Health Professions Act 56 of 1974
3. Allied Health Professions Act
4. Medicine and Related Substances Act 101 of 1965
5. Consumer Protection Act 68 of 2008
6. Financial Advisory and Intermediary Services Act (FAIS) 37 of 2002
7. HPCSA (Health Professions Council of SA) guidelines
8. AHPCSA (Allied Health Professions Council of SA) guidelines

YOUR ROLE:
Review agent outputs and determine if they constitute:
1. **Medical Practice Violations:**
   - Diagnosing conditions
   - Prescribing medication or treatments
   - Interpreting test results in a diagnostic manner
   - Providing specific medical advice requiring professional judgment
   - Any activity reserved for registered medical practitioners

2. **Financial Services Violations:**
   - Recommending specific financial products
   - Providing personalised investment advice
   - Acting as a financial intermediary
   - Soliciting financial product sales
   - Any activity requiring FSP licensure

RESPONSE FORMAT:
If violations found, respond: "BLOCKED: [specific violation and legal reference]"
If compliant, respond: "APPROVED" followed by any required disclaimers

STRICTNESS LEVEL: Maximum
When in doubt, BLOCK the content. It is better to be overly cautious than to permit illegal practice.

EXAMPLES:
❌ BLOCK: "You should take paracetamol for your headache" → Prescribing
❌ BLOCK: "Buy Discovery Health's Comprehensive Plan" → Specific product recommendation
✅ APPROVE: "Headache relief options are something to discuss with a pharmacist or doctor"
✅ APPROVE: "Comprehensive medical aid plans typically offer wider coverage than hospital plans"
```

---

### 4. Language Critic Agent

**Agent ID:** `language-critic-agent`  
**Model:** Claude Sonnet 4 (recommended)  
**Timeout:** 3 minutes

#### Purpose
Ensures all responses use clear, accessible British English with Germanic-rooted words, while validating content quality and tone.

#### Responsibilities
1. **Germanic Root Replacement**: Replace Latin/Romance words with Germanic equivalents
2. **British English Enforcement**: Use British spellings and vocabulary
3. **Content Validation**: Remove unsolicited advice and verify relevance
4. **Tone Quality**: Ensure respectful, non-patronising communication

#### System Prompt
```
You are the Language Critic Agent with two critical responsibilities:

1. GERMANIC ROOT REPLACEMENT
You must rewrite responses using Germanic-rooted English words instead of Latin/Romance words.

Common replacements (non-exhaustive list):
- "utilise" → "use"
- "purchase" → "buy"
- "commence" → "begin" or "start"
- "assist" → "help"
- "obtain" → "get"
- "provide" → "give"
- "require" → "need"
- "additional" → "further" or "more"
- "medication" → "medicine" (context-dependent)
- "sufficient" → "enough"
- "approximately" → "about" or "roughly"
- "demonstrate" → "show"
- "indicate" → "show" or "point to"
- "consider" → "think about"
- "recommend" → "suggest"
- "important" → "key" or "weighty"
- "continue" → "carry on" or "keep going"
- "complete" → "finish"
- "create" → "make"
- "receive" → "get"
- "maintain" → "keep" or "uphold"
- "consume" → "eat" or "drink" (context-dependent)

2. BRITISH ENGLISH ENFORCEMENT
- Use British spellings exclusively:
  * "organise" not "organize"
  * "behaviour" not "behavior"
  * "centre" not "center"
  * "colour" not "color"
  * "licence" (noun) / "license" (verb)
  * "practise" (verb) / "practice" (noun)
- Use British vocabulary:
  * "lift" not "elevator"
  * "chemist" not "pharmacy" (where appropriate)
  * "whilst" is acceptable (though "while" is also British)

3. CONTENT VALIDATION
Critically evaluate responses against the original user prompt:
- Remove any advice NOT explicitly requested
- Qualify or remove exaggerations
- Ensure responses directly address what was asked
- Remove unnecessary elaboration or tangents
- Flag any content that seems patronising or condescending

4. TONE REQUIREMENTS
- Formal but clear
- Never patronising
- Respectful and direct
- Assumes user intelligence

YOUR PROCESS:
1. Read the original user prompt carefully
2. Review all agent outputs
3. Rewrite using Germanic roots and British English
4. Validate all recommendations against the original question
5. Ensure tone is appropriate
6. Output ONLY the final approved response

DO NOT:
- Add information not in the specialist agent responses
- Change the fundamental meaning or advice
- Remove critical disclaimers or warnings
- Be overly wordy or academic

OUTPUT FORMAT:
Provide only the final, user-ready response. No preamble, no meta-commentary.
```

---

### 5. Orchestrator Agent (Optional)

**Agent ID:** `orchestrator-agent`  
**Model:** Claude Sonnet 4 (recommended)  
**Timeout:** 5 minutes

#### Purpose
Coordinates between specialist agents for complex queries requiring multiple domains of expertise.

#### System Prompt
```
You are the Orchestrator for a multi-agent health and financial guidance system operating in South Africa.

Your role is to coordinate between agents, not to provide advice directly.

When a user query arrives:
1. Determine which specialist agents are needed (Health, Financial, or both)
2. Route the query appropriately
3. Collect responses
4. Ensure legal compliance has been checked
5. Ensure language critic has reviewed
6. Return the final approved response

You do not generate medical or financial content yourself - you only coordinate the specialist agents.
```

---

## ⚙️ Agent Setup Checklist

### In Ark Dashboard:

- [ ] Create **Health Companion Agent** (`health-companion-agent`)
- [ ] Create **Financial Coach Agent** (`financial-coach-agent`)
- [ ] Create **Legal Compliance Agent** (`legal-compliance-agent`)
- [ ] Create **Language Critic Agent** (`language-critic-agent`)
- [ ] Create **Orchestrator Agent** (`orchestrator-agent`) - optional
- [ ] Copy system prompts into each agent's configuration
- [ ] Set model to Claude Sonnet 4 for all agents
- [ ] Configure timeout: 5 minutes for main agents, 3 minutes for review agents
- [ ] Enable conversation memory for context
- [ ] Create team: `greencare-team` with all agents
- [ ] Configure agent orchestration/routing logic
- [ ] Test each agent individually

### Testing Sequence:

1. **Test Legal Compliance Agent:**
   ```
   Input: "You should take aspirin for your headache"
   Expected: "BLOCKED: Prescribing medication..."
   ```

2. **Test Language Critic Agent:**
   ```
   Input: "You should utilise this medication to commence treatment"
   Expected: "You should use this medicine to begin treatment"
   ```

3. **Test Health Agent:**
   ```
   Input: "What can I do to improve my sleep?"
   Expected: General wellness advice with disclaimer
   ```

4. **Test Financial Agent:**
   ```
   Input: "How can I budget for medical expenses?"
   Expected: Budgeting principles with disclaimer
   ```

5. **Test Full Orchestration:**
   ```
   Input: "I have diabetes and need help managing costs"
   Expected: Coordinated response from all agents with proper disclaimers
   ```

---

## 📁 Project Structure

```
greencare-ai/
├── app.py              # Main Streamlit application
├── database.py         # SQLite database manager with all CRUD operations
├── requirements.txt    # Python dependencies
├── .env               # Environment variables (create this)
└── README.md          # This file
```

---

## 🗄️ Database Schema

The application uses SQLite with the following tables:

- **Users**: Core user information (name, email, contact details)
- **Login**: Authentication credentials (hashed passwords)
- **MedicalAid**: Medical scheme information
- **MedicalHistory**: Active and past medical conditions
- **Medication**: Current and past medications
- **Allergies**: Documented allergies with severity
- **FinancialAccounts**: Income, budget, and balance tracking
- **ChatHistory**: All conversations with timestamps
- **UserSessions**: Active session management

The database is automatically created at:
- **Windows**: `%LOCALAPPDATA%\GreenCare\greencare.db`
- **Linux/Mac**: `~/AppData/Local/GreenCare/greencare.db`

---

## 🔧 Configuration

### Ark Integration

The app connects to Ark's team-based query system:

```python
ARK_API_BASE_URL = "http://localhost:3274/api/v1"
ARK_TEAM_NAME = "greencare-team"
```

Modify these in `app.py` if your Ark setup differs.

### Profile Context

User profiles are automatically passed to agents as context:

- Medical aid scheme and plan
- Active medical conditions
- Current medications
- Documented allergies
- Monthly income and expenses
- Recent conversation history

---

## 📝 Usage

### First Time Setup

1. **Register**: Create an account with your details
2. **Login**: Access your personalized dashboard
3. **Edit Profile**: Add medical and financial information
4. **Start Chatting**: Ask the GreenCare Team anything!

### Profile Management

Click **"Edit My Profile"** in the sidebar to update:

- Medical aid scheme and membership number
- Active medical conditions (one per line)
- Current medications (one per line)
- Monthly income and expenses

All changes are saved to the database and immediately available to AI agents.

### Chat Features

- **New Chat**: Start fresh conversations
- **Persistent History**: All chats auto-saved
- **Context-Aware**: Agents remember your profile
- **Multi-Turn**: Natural back-and-forth conversations

---

## 🔐 Security Features

- **Password Hashing**: PBKDF2-HMAC-SHA256 with random salts
- **Session Management**: Time-limited session tokens
- **SQL Injection Protection**: Parameterized queries throughout
- **Local Storage**: All data stored locally in SQLite

---

## ⚠️ Important Notes

### Legal Disclaimers

**GreenCare AI is not a substitute for professional medical or financial advice.**

The system automatically includes these disclaimers:

**Health Content:**
> This is general information only. Please consult a registered healthcare professional for medical advice.

**Financial Content:**
> This is educational information only. Please consult a licensed financial advisor for personalised financial product advice.

**System-wide:**
> This system is NOT a registered medical practitioner or financial services provider. All advice is for informational purposes only.

### Regulatory Compliance

GreenCare AI is designed to comply with:
- **Health Professions Act 56 of 1974**
- **National Health Act 61 of 2003**
- **Financial Advisory and Intermediary Services Act (FAIS) 37 of 2002**
- **Consumer Protection Act 68 of 2008**

The built-in Legal Compliance Agent actively monitors all responses to prevent violations.

### Data Privacy

- All data stored locally on your machine
- No cloud storage or external data sharing
- Database location: `%LOCALAPPDATA%\GreenCare\greencare.db`

---

## 🛠️ Development

### Database Management

The `SQLiteDBManager` class provides comprehensive methods:

```python
# User management
db.create_user(username, email, password, first_name, last_name, ...)
db.authenticate_user(username, password)
db.get_user_profile(user_id)

# Profile updates
db.update_medical_aid(user_id, scheme_name, membership_number)
db.update_medical_history(user_id, conditions_list)
db.update_medications(user_id, medications_list)
db.update_financial_account(user_id, income, budget)

# Chat history
db.save_chat_message(user_id, agent_type, role, content, session_id)
db.get_chat_history(user_id, agent_type, limit)
```

### Adding New Features

1. Update database schema in `database.py` `initialize_database()`
2. Add CRUD methods as needed
3. Update UI in `app.py`
4. Modify agent context in `build_agent_context()` if needed
5. Update agent system prompts in Ark dashboard if new context is needed

---

## 📦 Dependencies

```txt
streamlit>=1.28.0
python-dotenv>=1.0.0
requests>=2.31.0
```

Install all at once:
```bash
pip install -r requirements.txt
```

---

## 🐛 Troubleshooting

### "Connection issue" Error
- Verify Ark is running at `http://localhost:3274`
- Check team name matches: `greencare-team`
- Ensure all 5 agents are properly configured in Ark
- Verify agents are added to the team
- Check API key in `.env` file

### Agent Not Responding
- Check agent ID matches exactly (case-sensitive)
- Verify system prompt is properly configured
- Check agent timeout settings (5 minutes recommended)
- Review Ark logs for errors

### Database Errors
- Check database path is writable
- Verify SQLite installation: `python -c "import sqlite3; print(sqlite3.version)"`
- Check for database file corruption

### Login Issues
- Verify username/password are correct
- Check database file exists and isn't corrupted
- Try creating a new account

### Legal Compliance Blocks
- Review blocked content in logs
- Adjust phrasing to avoid prescriptive language
- Check agent system prompts for updates
- Ensure Legal Compliance Agent is properly configured

---

## 🤝 Contributing

Contributions welcome! Please:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit changes (`git commit -m 'Add AmazingFeature'`)
4. Push to branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

When contributing agent improvements:
- Update system prompts in this README
- Test thoroughly with the testing sequence
- Document any new legal considerations
- Ensure British English compliance

---

## 📄 License

This project is provided as-is for educational and personal use.

---

## 🙏 Acknowledgments

- Built with [Streamlit](https://streamlit.io/)
- Powered by [Ark Agentic Framework](https://github.com/arkohq/ark)
- AI models by [Anthropic Claude](https://www.anthropic.com/)
- Designed for South African healthcare and financial context
- Legal compliance framework based on South African legislation

---

## 📧 Support

For issues or questions:
- Open an issue on GitHub
- Check existing documentation
- Review Ark framework documentation
- Consult agent configuration examples

---

**Made with 💚 for better health and financial wellness in South Africa**
