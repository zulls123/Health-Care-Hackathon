# database.py - FULL VERSION WITH ALL UPDATE METHODS
import sqlite3
import json
from datetime import datetime, timedelta
from typing import Dict, List, Optional
import hashlib
import secrets
import os
from contextlib import contextmanager

class SQLiteDBManager:
    def __init__(self, db_path: str = "greencare.db"):
        self.db_path = db_path
        self.initialize_database()
    
    @contextmanager
    def get_connection(self):
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        try:
            yield conn
        finally:
            conn.close()
    
    def initialize_database(self):
        with self.get_connection() as conn:
            cursor = conn.cursor()
            
            # Users table
            cursor.execute("""
            CREATE TABLE IF NOT EXISTS Users (
                user_id INTEGER PRIMARY KEY AUTOINCREMENT,
                first_name TEXT NOT NULL,
                last_name TEXT NOT NULL,
                email TEXT UNIQUE NOT NULL,
                phone TEXT,
                date_of_birth DATE,
                gender TEXT,
                province TEXT,
                city TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP,
                last_login TIMESTAMP
            )
            """)
            
            # Login table
            cursor.execute("""
            CREATE TABLE IF NOT EXISTS Login (
                login_id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                username TEXT UNIQUE NOT NULL,
                password_hash TEXT NOT NULL,
                password_salt TEXT NOT NULL,
                last_login_at TIMESTAMP,
                is_active INTEGER DEFAULT 1,
                FOREIGN KEY (user_id) REFERENCES Users(user_id) ON DELETE CASCADE
            )
            """)
            
            # Medical Aid table
            cursor.execute("""
            CREATE TABLE IF NOT EXISTS MedicalAid (
                medical_aid_id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                scheme_name TEXT,
                plan_type TEXT,
                membership_number TEXT,
                is_active INTEGER DEFAULT 1,
                FOREIGN KEY (user_id) REFERENCES Users(user_id) ON DELETE CASCADE
            )
            """)
            
            # Medical History table
            cursor.execute("""
            CREATE TABLE IF NOT EXISTS MedicalHistory (
                history_id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                condition_name TEXT NOT NULL,
                diagnosis_date DATE,
                status TEXT,
                notes TEXT,
                FOREIGN KEY (user_id) REFERENCES Users(user_id) ON DELETE CASCADE
            )
            """)
            
            # Medication table
            cursor.execute("""
            CREATE TABLE IF NOT EXISTS Medication (
                medication_id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                medication_name TEXT NOT NULL,
                dosage TEXT,
                frequency TEXT,
                start_date DATE,
                is_active INTEGER DEFAULT 1,
                FOREIGN KEY (user_id) REFERENCES Users(user_id) ON DELETE CASCADE
            )
            """)
            
            # Allergies table
            cursor.execute("""
            CREATE TABLE IF NOT EXISTS Allergies (
                allergy_id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                allergen TEXT NOT NULL,
                severity TEXT,
                reaction TEXT,
                FOREIGN KEY (user_id) REFERENCES Users(user_id) ON DELETE CASCADE
            )
            """)
            
            # Financial Accounts table
            cursor.execute("""
            CREATE TABLE IF NOT EXISTS FinancialAccounts (
                account_id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                account_type TEXT NOT NULL DEFAULT 'main',
                balance REAL DEFAULT 0,
                currency TEXT DEFAULT 'ZAR',
                monthly_income REAL,
                monthly_budget REAL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES Users(user_id) ON DELETE CASCADE
            )
            """)
            
            # Chat History table
            cursor.execute("""
            CREATE TABLE IF NOT EXISTS ChatHistory (
                chat_id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                agent_type TEXT NOT NULL,
                session_id TEXT,
                role TEXT NOT NULL,
                content TEXT NOT NULL,
                timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES Users(user_id) ON DELETE CASCADE
            )
            """)
            
            # User Sessions table
            cursor.execute("""
            CREATE TABLE IF NOT EXISTS UserSessions (
                session_id TEXT PRIMARY KEY,
                user_id INTEGER NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                expires_at TIMESTAMP,
                is_active INTEGER DEFAULT 1,
                FOREIGN KEY (user_id) REFERENCES Users(user_id) ON DELETE CASCADE
            )
            """)
            
            # Indexes
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_login_username ON Login(username)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_login_user_id ON Login(user_id)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_medical_aid_user_id ON MedicalAid(user_id)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_medical_history_user_id ON MedicalHistory(user_id)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_medication_user_id ON Medication(user_id)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_allergies_user_id ON Allergies(user_id)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_financial_accounts_user_id ON FinancialAccounts(user_id)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_chat_history_user_id ON ChatHistory(user_id)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_chat_history_agent_type ON ChatHistory(agent_type)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_user_sessions_user_id ON UserSessions(user_id)")
            
            conn.commit()

    # ========= USER MANAGEMENT =========

    def create_user(self, username: str, email: str, password: str, 
                   first_name: str, last_name: str, 
                   phone: str = None, date_of_birth: str = None,
                   gender: str = None, province: str = None, 
                   city: str = None) -> Optional[int]:
        """Create new user account with login credentials"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            
            # Generate salt and hash password
            password_salt = secrets.token_hex(32)
            password_hash = hashlib.pbkdf2_hmac('sha256', 
                                               password.encode(), 
                                               password_salt.encode(), 
                                               100000).hex()
            
            try:
                # Insert user
                cursor.execute("""
                    INSERT INTO Users (first_name, last_name, email, phone, 
                                     date_of_birth, gender, province, city)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """, (first_name, last_name, email, phone, 
                      date_of_birth, gender, province, city))
                
                user_id = cursor.lastrowid
                
                # Insert login credentials
                cursor.execute("""
                    INSERT INTO Login (user_id, username, password_hash, password_salt)
                    VALUES (?, ?, ?, ?)
                """, (user_id, username, password_hash, password_salt))
                
                conn.commit()
                return user_id
                
            except sqlite3.IntegrityError as e:
                conn.rollback()
                print(f"Error creating user: {e}")
                return None
    
    def authenticate_user(self, username: str, password: str) -> Optional[Dict]:
        """Authenticate user and return user info"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            
            try:
                cursor.execute("""
                    SELECT 
                        u.user_id, u.first_name, u.last_name, u.email, 
                        u.phone, u.date_of_birth, u.gender, u.province, u.city,
                        l.password_hash, l.password_salt
                    FROM Users u
                    INNER JOIN Login l ON u.user_id = l.user_id
                    WHERE l.username = ? AND l.is_active = 1
                """, (username,))
                row = cursor.fetchone()
                
                if not row:
                    return None
                
                # Verify password
                password_hash = hashlib.pbkdf2_hmac('sha256', 
                                                   password.encode(), 
                                                   row["password_salt"].encode(), 
                                                   100000).hex()
                
                if password_hash != row["password_hash"]:
                    return None
                
                # Update last login
                cursor.execute("""
                    UPDATE Login
                    SET last_login_at = CURRENT_TIMESTAMP
                    WHERE user_id = ?
                """, (row["user_id"],))
                
                cursor.execute("""
                    UPDATE Users
                    SET last_login = CURRENT_TIMESTAMP
                    WHERE user_id = ?
                """, (row["user_id"],))
                
                conn.commit()
                
                return {
                    "user_id": row["user_id"],
                    "first_name": row["first_name"],
                    "last_name": row["last_name"],
                    "email": row["email"],
                    "phone": row["phone"],
                    "date_of_birth": row["date_of_birth"],
                    "gender": row["gender"],
                    "province": row["province"],
                    "city": row["city"]
                }
                
            except Exception as e:
                print(f"Error authenticating user: {e}")
                return None
    
    def get_user_profile(self, user_id: int) -> Dict:
        """Get complete user profile"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            
            try:
                # Get medical aid
                cursor.execute("""
                    SELECT scheme_name, plan_type, membership_number
                    FROM MedicalAid
                    WHERE user_id = ? AND is_active = 1
                """, (user_id,))
                ma = cursor.fetchone()
                medical_aid = {
                    "scheme_name": ma["scheme_name"],
                    "plan_type": ma["plan_type"],
                    "membership_number": ma["membership_number"]
                } if ma else None
                
                # Get medical history
                cursor.execute("""
                    SELECT condition_name as condition, status
                    FROM MedicalHistory
                    WHERE user_id = ?
                """, (user_id,))
                medical_history = [dict(r) for r in cursor.fetchall()]
                
                # Get medications
                cursor.execute("""
                    SELECT medication_name as name, dosage, frequency, is_active
                    FROM Medication
                    WHERE user_id = ?
                """, (user_id,))
                medications = [dict(r) for r in cursor.fetchall()]
                
                # Get allergies
                cursor.execute("""
                    SELECT allergen, severity, reaction
                    FROM Allergies
                    WHERE user_id = ?
                """, (user_id,))
                allergies = [dict(r) for r in cursor.fetchall()]
                
                # Get financial accounts
                cursor.execute("""
                    SELECT account_type, balance, currency, monthly_income, monthly_budget
                    FROM FinancialAccounts
                    WHERE user_id = ?
                """, (user_id,))
                financial_accounts = [dict(r) for r in cursor.fetchall()]
                
                return {
                    "medical_aid": medical_aid,
                    "medical_history": medical_history,
                    "medications": medications,
                    "allergies": allergies,
                    "financial_accounts": financial_accounts
                }
                
            except Exception as e:
                print(f"Error getting profile: {e}")
                return {}

    # ========= PROFILE UPDATE METHODS =========

    def update_medical_aid(self, user_id: int, scheme_name: str, membership_number: str):
        """Update or create medical aid entry"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            try:
                cursor.execute("""
                    SELECT medical_aid_id FROM MedicalAid WHERE user_id = ?
                """, (user_id,))
                exists = cursor.fetchone()
                
                if exists:
                    cursor.execute("""
                        UPDATE MedicalAid
                        SET scheme_name = ?, membership_number = ?, is_active = 1
                        WHERE user_id = ?
                    """, (scheme_name, membership_number, user_id))
                else:
                    cursor.execute("""
                        INSERT INTO MedicalAid (user_id, scheme_name, membership_number)
                        VALUES (?, ?, ?)
                    """, (user_id, scheme_name, membership_number))
                
                conn.commit()
            except Exception as e:
                print(f"Error updating medical aid: {e}")
                conn.rollback()
    
    def update_medical_history(self, user_id: int, conditions: List[str]):
        """Update medical history - delete old and add new"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            try:
                cursor.execute("DELETE FROM MedicalHistory WHERE user_id = ?", (user_id,))
                for cond in conditions:
                    cursor.execute("""
                        INSERT INTO MedicalHistory (user_id, condition_name, status)
                        VALUES (?, ?, 'Active')
                    """, (user_id, cond))
                conn.commit()
            except Exception as e:
                print(f"Error updating medical history: {e}")
                conn.rollback()

    def update_medications(self, user_id: int, medications: List[str]):
        """Update medications - delete old and add new"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            try:
                cursor.execute("DELETE FROM Medication WHERE user_id = ?", (user_id,))
                for med in medications:
                    cursor.execute("""
                        INSERT INTO Medication (user_id, medication_name, is_active)
                        VALUES (?, ?, 1)
                    """, (user_id, med))
                conn.commit()
            except Exception as e:
                print(f"Error updating medications: {e}")
                conn.rollback()
    
    def update_financial_account(self, user_id: int, monthly_income: float, monthly_budget: float):
        """Update or create financial account"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            try:
                cursor.execute("""
                    SELECT account_id FROM FinancialAccounts 
                    WHERE user_id = ? AND account_type = 'main'
                """, (user_id,))
                exists = cursor.fetchone()
                
                if exists:
                    cursor.execute("""
                        UPDATE FinancialAccounts
                        SET monthly_income = ?, monthly_budget = ?, updated_at = CURRENT_TIMESTAMP
                        WHERE user_id = ? AND account_type = 'main'
                    """, (monthly_income, monthly_budget, user_id))
                else:
                    cursor.execute("""
                        INSERT INTO FinancialAccounts 
                        (user_id, account_type, monthly_income, monthly_budget)
                        VALUES (?, 'main', ?, ?)
                    """, (user_id, monthly_income, monthly_budget))
                
                conn.commit()
            except Exception as e:
                print(f"Error updating financial account: {e}")
                conn.rollback()

    # ========= CHAT HISTORY =========
    
    def save_chat_message(self, user_id: int, agent_type: str, role: str, 
                         content: str, session_id: str):
        """Save a chat message to history"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            
            try:
                cursor.execute("""
                    INSERT INTO ChatHistory (user_id, agent_type, session_id, role, content)
                    VALUES (?, ?, ?, ?, ?)
                """, (user_id, agent_type, session_id, role, content))
                
                conn.commit()
            except Exception as e:
                print(f"Error saving chat message: {e}")
                conn.rollback()
    
    def get_chat_history(self, user_id: int, agent_type: str = None, 
                        limit: int = 50) -> List[Dict]:
        """Retrieve chat history for a user"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            
            try:
                if agent_type:
                    cursor.execute("""
                        SELECT agent_type, role, content, timestamp, session_id
                        FROM ChatHistory
                        WHERE user_id = ? AND agent_type = ?
                        ORDER BY timestamp DESC
                        LIMIT ?
                    """, (user_id, agent_type, limit))
                else:
                    cursor.execute("""
                        SELECT agent_type, role, content, timestamp, session_id
                        FROM ChatHistory
                        WHERE user_id = ?
                        ORDER BY timestamp DESC
                        LIMIT ?
                    """, (user_id, limit))
                
                rows = cursor.fetchall()
                
                history = []
                for row in rows:
                    history.append({
                        "agent_type": row[0],
                        "role": row[1],
                        "content": row[2],
                        "timestamp": row[3],
                        "session_id": row[4]
                    })
                
                return list(reversed(history))  # Chronological
                
            except Exception as e:
                print(f"Error fetching chat history: {e}")
                return []
    
    def get_recent_context(self, user_id: int, agent_type: str, 
                          days: int = 7) -> str:
        """Get summarized recent context for agent"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            
            try:
                cursor.execute("""
                    SELECT role, content
                    FROM ChatHistory
                    WHERE user_id = ? 
                      AND agent_type = ?
                      AND timestamp >= datetime('now', '-' || ? || ' days')
                    ORDER BY timestamp ASC
                    LIMIT 10
                """, (user_id, agent_type, days))
                
                rows = cursor.fetchall()
                
                context_parts = []
                for role, content in rows:
                    context_parts.append(f"{role}: {content[:100]}...")
                
                return "\n".join(context_parts) if context_parts else ""
                
            except Exception as e:
                print(f"Error fetching recent context: {e}")
                return ""
    
    # ========= SESSION MANAGEMENT =========
    
    def create_session(self, user_id: int, session_id: str, expires_hours: int = 24):
        """Create a new user session"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            
            try:
                cursor.execute("""
                    INSERT INTO UserSessions (session_id, user_id, expires_at)
                    VALUES (?, ?, datetime('now', '+' || ? || ' hours'))
                """, (session_id, user_id, expires_hours))
                
                conn.commit()
            except Exception as e:
                print(f"Error creating session: {e}")
                conn.rollback()
    
    def validate_session(self, session_id: str) -> Optional[int]:
        """Validate session and return user_id"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            
            try:
                cursor.execute("""
                    SELECT user_id
                    FROM UserSessions
                    WHERE session_id = ? 
                      AND is_active = 1
                      AND expires_at > datetime('now')
                """, (session_id,))
                
                row = cursor.fetchone()
                return row[0] if row else None
                
            except Exception as e:
                print(f"Error validating session: {e}")
                return None
    
    def end_session(self, session_id: str):
        """End a user session"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            
            try:
                cursor.execute("""
                    UPDATE UserSessions
                    SET is_active = 0
                    WHERE session_id = ?
                """, (session_id,))
                
                conn.commit()
            except Exception as e:
                print(f"Error ending session: {e}")
                conn.rollback()
    
    # ========= UTILITY METHODS =========
    
    def build_agent_context(self, user_id: int, agent_type: str) -> str:
        """Build context string from user profile for agent"""
        profile = self.get_user_profile(user_id)
        context_parts = []
        
        if agent_type == "Health Companion":
            # Medical information
            if profile.get("medical_aid"):
                ma = profile["medical_aid"]
                context_parts.append(f"Medical Aid: {ma['scheme_name']} ({ma['plan_type']})")
            
            if profile.get("medical_history"):
                conditions = [h["condition"] for h in profile["medical_history"] 
                            if h["status"] == "Active"]
                if conditions:
                    context_parts.append(f"Active conditions: {', '.join(conditions)}")
            
            if profile.get("medications"):
                meds = [f"{m['name']} ({m['dosage']})" for m in profile["medications"]]
                if meds:
                    context_parts.append(f"Current medications: {', '.join(meds)}")
            
            if profile.get("allergies"):
                allergens = [f"{a['allergen']} ({a['severity']})" 
                           for a in profile["allergies"]]
                if allergens:
                    context_parts.append(f"Allergies: {', '.join(allergens)}")
        
        elif agent_type == "Financial Agent":
            # Financial information
            if profile.get("financial_accounts"):
                for acc in profile["financial_accounts"]:
                    if acc.get("monthly_income"):
                        context_parts.append(
                            f"Monthly income: {acc['currency']} {acc['monthly_income']:,.2f}"
                        )
                    if acc.get("monthly_budget"):
                        context_parts.append(
                            f"Monthly budget: {acc['currency']} {acc['monthly_budget']:,.2f}"
                        )
                    if acc.get("balance"):
                        context_parts.append(
                            f"Account balance: {acc['currency']} {acc['balance']:,.2f}"
                        )
            
            if profile.get("medical_aid"):
                ma = profile["medical_aid"]
                context_parts.append(f"Medical Aid: {ma['scheme_name']}")
        
        # Add recent conversation context
        recent = self.get_recent_context(user_id, agent_type, days=7)
        if recent:
            context_parts.append("\nRecent conversations:")
            context_parts.append(recent)
        
        return "\n".join(context_parts)

# Alias for backward compatibility
AzureDBManager = SQLiteDBManager