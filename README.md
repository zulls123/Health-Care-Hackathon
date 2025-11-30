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
   # Optional: Add any API keys or configuration here
   ```

5. **Configure Ark Team**
   
   Ensure your Ark instance is running and the team is configured:
   - **Team Name**: `greencare-team`
   - **API Base URL**: `http://localhost:3274/api/v1` (default)
   
   Update `ARK_API_BASE_URL` and `ARK_TEAM_NAME` in `app.py` if using different values.

6. **Run the application**
   ```bash
   streamlit run app.py
   ```

7. **Access the app**
   
   Open your browser to `http://localhost:8501`

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

### Legal Disclaimer

**GreenCare AI is not a substitute for professional medical or financial advice.**

- Always consult qualified healthcare providers for medical decisions
- Consult certified financial advisors for financial planning
- This tool provides information and guidance only

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
- Ensure team is properly configured in Ark

### Database Errors
- Check database path is writable
- Verify SQLite installation: `python -c "import sqlite3; print(sqlite3.version)"`

### Login Issues
- Verify username/password are correct
- Check database file exists and isn't corrupted
- Try creating a new account

---

## 🤝 Contributing

Contributions welcome! Please:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit changes (`git commit -m 'Add AmazingFeature'`)
4. Push to branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

---

## 📄 License

This project is provided as-is for educational and personal use.

---

## 🙏 Acknowledgments

- Built with [Streamlit](https://streamlit.io/)
- Powered by [Ark Agentic Framework](https://github.com/arkohq/ark)
- Designed for South African healthcare context

---

## 📧 Support

For issues or questions:
- Open an issue on GitHub
- Check existing documentation
- Review Ark framework documentation

---

**Made with 💚 for better health and financial wellness**
