# agents/mock_email_services.py
"""
Mock email services infrastructure for evaluation scenarios.
Simulates SirFixAlotV2 email system without touching real directories.
"""

import os
import random
import sqlite3
import hashlib
from datetime import datetime, timedelta
from dataclasses import dataclass
from typing import List, Dict, Any, Optional, Tuple
import json


@dataclass
class MockEmailRecord:
    """Mock email record matching SirFixAlotV2 schema."""
    id: int
    email_id: str
    account_name: str
    thread_id: Optional[str]
    subject: Optional[str]
    sender_email: Optional[str]
    sender_name: Optional[str]
    recipient_to: Optional[str]
    recipient_cc: Optional[str]
    reply_to: Optional[str]
    date_sent: Optional[str]
    date_received: Optional[str]
    full_body_text: Optional[str]
    full_body_html: Optional[str]
    snippet: Optional[str]
    body_preview: Optional[str]
    has_attachments: Optional[bool]
    attachment_count: Optional[int]
    attachment_names: Optional[str]
    attachment_types: Optional[str]
    message_size: Optional[int]
    is_reply: Optional[bool]
    is_forward: Optional[bool]
    in_reply_to: Optional[str]
    message_references: Optional[str]
    llm_decision: Optional[str]
    llm_confidence: Optional[float]
    llm_reasoning: Optional[str]
    llm_processing_time_ms: Optional[int]
    urgency_score: Optional[int]
    business_category: Optional[str]
    action_taken: Optional[str]
    action_success: Optional[bool]


class MockAuthenticationService:
    """Mock authentication service for different email providers."""

    def __init__(self):
        self.accounts = {
            "adotob_primary": {"type": "microsoft", "auth": "device_code", "status": "active"},
            "hotmail_fabian_williams": {"type": "microsoft", "auth": "device_code", "status": "active"},
            "gmail_fabsgwill": {"type": "gmail", "auth": "oauth", "status": "active"},
            "gmail_jahmekyanbwoy": {"type": "gmail", "auth": "oauth", "status": "active"},
        }

    def authenticate_account(self, account_name: str) -> Dict[str, Any]:
        """Mock authentication for an account."""
        if account_name not in self.accounts:
            return {"success": False, "error": f"Account {account_name} not found"}

        account = self.accounts[account_name]

        # Simulate occasional auth failures for realism
        if random.random() < 0.05:  # 5% failure rate
            return {"success": False, "error": "Token expired"}

        return {
            "success": True,
            "account": account_name,
            "type": account["type"],
            "auth_method": account["auth"],
            "expires_in": 3600
        }


class MockEmailDatabase:
    """Mock SQLite database for email storage and retrieval."""

    def __init__(self, db_path: str = ":memory:"):
        self.db_path = db_path
        self.conn = sqlite3.connect(db_path)
        self._setup_schema()
        self._populate_mock_data()

    def _setup_schema(self):
        """Create the email table schema matching SirFixAlotV2."""
        self.conn.execute("""
            CREATE TABLE IF NOT EXISTS emails (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                email_id TEXT NOT NULL UNIQUE,
                account_name TEXT NOT NULL,
                thread_id TEXT,
                subject TEXT,
                sender_email TEXT,
                sender_name TEXT,
                recipient_to TEXT,
                recipient_cc TEXT,
                reply_to TEXT,
                date_sent TEXT,
                date_received TEXT,
                full_body_text TEXT,
                full_body_html TEXT,
                snippet TEXT,
                body_preview TEXT,
                has_attachments BOOLEAN DEFAULT 0,
                attachment_count INTEGER DEFAULT 0,
                attachment_names TEXT,
                attachment_types TEXT,
                message_size INTEGER,
                is_reply BOOLEAN DEFAULT 0,
                is_forward BOOLEAN DEFAULT 0,
                in_reply_to TEXT,
                message_references TEXT,
                llm_decision TEXT,
                llm_confidence REAL,
                llm_reasoning TEXT,
                llm_processing_time_ms INTEGER,
                urgency_score INTEGER,
                business_category TEXT,
                action_taken TEXT,
                action_success BOOLEAN,
                email_hash TEXT UNIQUE,
                auto_classified BOOLEAN DEFAULT 0,
                pattern_matched BOOLEAN DEFAULT 0,
                email_type TEXT DEFAULT 'inbox',
                writing_tone TEXT,
                recipient_relationship TEXT,
                word_count INTEGER,
                sentence_count INTEGER,
                avg_sentence_length REAL,
                formality_score REAL,
                response_time_hours REAL,
                contact_frequency TEXT,
                is_vip_contact BOOLEAN DEFAULT 0,
                conversation_starter BOOLEAN DEFAULT 0,
                conversation_ender BOOLEAN DEFAULT 0,
                received_date TEXT DEFAULT '',
                body_content TEXT DEFAULT ''
            )
        """)
        self.conn.commit()

    def _populate_mock_data(self):
        """Populate with realistic mock email data."""
        sample_emails = [
            # Business emails (adotob_primary)
            {
                "account_name": "adotob_primary",
                "subject": "Quarterly Planning Meeting - Action Items",
                "sender_email": "manager@company.com",
                "sender_name": "Sarah Manager",
                "body_text": "Hi Fabian, Following up on our quarterly planning session. Please review the attached action items and provide feedback by EOW. Key priorities: 1) Finalize Q4 budget 2) Review team performance metrics 3) Plan resource allocation for next quarter.",
                "business_category": "planning",
                "urgency_score": 7,
                "has_attachments": True,
                "attachment_count": 2
            },
            {
                "account_name": "adotob_primary",
                "subject": "Aidvantage Student Loan - Payment Reminder",
                "sender_email": "noreply@aidvantage.com",
                "sender_name": "Aidvantage Support",
                "body_text": "Your student loan payment of $387.50 is due on December 15, 2024. Please log into your account to make a payment or set up autopay to avoid late fees.",
                "business_category": "finance",
                "urgency_score": 8,
                "has_attachments": False
            },
            {
                "account_name": "adotob_primary",
                "subject": "Microsoft 365 Security Alert",
                "sender_email": "security@microsoft.com",
                "sender_name": "Microsoft Security",
                "body_text": "We've detected a sign-in attempt from an unrecognized device. If this was you, no action is needed. If not, please secure your account immediately.",
                "business_category": "security",
                "urgency_score": 9,
                "has_attachments": False
            },

            # Personal emails (gmail accounts)
            {
                "account_name": "gmail_fabsgwill",
                "subject": "Weekend Plans - Let's Catch Up!",
                "sender_email": "friend@gmail.com",
                "sender_name": "Close Friend",
                "body_text": "Hey Fabian! Hope you're doing well. Want to grab coffee this weekend? I heard about a new place downtown that has amazing espresso. Let me know if Saturday afternoon works!",
                "business_category": "personal",
                "urgency_score": 3,
                "has_attachments": False
            },
            {
                "account_name": "gmail_fabsgwill",
                "subject": "Flight Confirmation - Madrid Trip",
                "sender_email": "confirmations@airline.com",
                "sender_name": "Airline Confirmations",
                "body_text": "Your flight to Madrid is confirmed! Flight AA1234 departing December 20, 2024 at 6:30 PM. Please arrive at the airport 3 hours early for international flights.",
                "business_category": "travel",
                "urgency_score": 6,
                "has_attachments": True,
                "attachment_count": 1
            },

            # Newsletter/promotional
            {
                "account_name": "gmail_jahmekyanbwoy",
                "subject": "Weekly Tech Newsletter - AI Developments",
                "sender_email": "newsletter@techblog.com",
                "sender_name": "Tech Weekly",
                "body_text": "This week in AI: OpenAI releases new features, Google announces Gemini updates, and Microsoft expands Copilot capabilities. Plus: 5 emerging AI startups to watch.",
                "business_category": "newsletter",
                "urgency_score": 2,
                "has_attachments": False
            },

            # Customer inquiry (business)
            {
                "account_name": "adotob_primary",
                "subject": "Question about Consulting Services",
                "sender_email": "potential.client@company.com",
                "sender_name": "Potential Client",
                "body_text": "Hi Fabian, I found your consulting profile and I'm interested in discussing a cloud migration project. Our company has 200+ employees and we're looking to move our on-premises infrastructure to Azure. Could we schedule a brief call to discuss your approach and pricing?",
                "business_category": "consulting",
                "urgency_score": 8,
                "has_attachments": False
            }
        ]

        for i, email_data in enumerate(sample_emails, 1):
            email_id = f"mock_email_{i}_{hashlib.md5(email_data['subject'].encode()).hexdigest()[:8]}"
            date_received = (datetime.now() - timedelta(days=random.randint(0, 30))).isoformat()

            self.conn.execute("""
                INSERT INTO emails (
                    email_id, account_name, subject, sender_email, sender_name,
                    full_body_text, date_received, business_category, urgency_score,
                    has_attachments, attachment_count, email_hash
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                email_id, email_data["account_name"], email_data["subject"],
                email_data["sender_email"], email_data["sender_name"],
                email_data["body_text"], date_received, email_data["business_category"],
                email_data["urgency_score"], email_data["has_attachments"],
                email_data.get("attachment_count", 0), email_id
            ))

        self.conn.commit()

    def get_inbox_emails(self, account_name: str, limit: int = 50) -> List[MockEmailRecord]:
        """Get inbox emails for an account."""
        cursor = self.conn.execute("""
            SELECT
                id, email_id, account_name, thread_id, subject, sender_email, sender_name,
                recipient_to, recipient_cc, reply_to, date_sent, date_received,
                full_body_text, full_body_html, snippet, body_preview, has_attachments,
                attachment_count, attachment_names, attachment_types, message_size,
                is_reply, is_forward, in_reply_to, message_references, llm_decision,
                llm_confidence, llm_reasoning, llm_processing_time_ms, urgency_score,
                business_category, action_taken, action_success
            FROM emails
            WHERE account_name = ?
            ORDER BY date_received DESC
            LIMIT ?
        """, (account_name, limit))

        emails = []
        for row in cursor.fetchall():
            emails.append(MockEmailRecord(*row))
        return emails

    def search_emails(self, query: str, account_filter: Optional[str] = None) -> List[MockEmailRecord]:
        """Search emails by text content."""
        base_query = """
            SELECT
                id, email_id, account_name, thread_id, subject, sender_email, sender_name,
                recipient_to, recipient_cc, reply_to, date_sent, date_received,
                full_body_text, full_body_html, snippet, body_preview, has_attachments,
                attachment_count, attachment_names, attachment_types, message_size,
                is_reply, is_forward, in_reply_to, message_references, llm_decision,
                llm_confidence, llm_reasoning, llm_processing_time_ms, urgency_score,
                business_category, action_taken, action_success
            FROM emails
            WHERE (subject LIKE ? OR full_body_text LIKE ?)
        """
        params = [f"%{query}%", f"%{query}%"]

        if account_filter:
            base_query += " AND account_name = ?"
            params.append(account_filter)

        base_query += " ORDER BY date_received DESC"

        cursor = self.conn.execute(base_query, params)
        emails = []
        for row in cursor.fetchall():
            emails.append(MockEmailRecord(*row))
        return emails

    def get_email_count_by_account(self) -> Dict[str, int]:
        """Get email count per account."""
        cursor = self.conn.execute("""
            SELECT account_name, COUNT(*) as count
            FROM emails
            GROUP BY account_name
        """)
        return dict(cursor.fetchall())

    def categorize_email(self, email_id: str, category: str, confidence: float) -> bool:
        """Mock email categorization."""
        cursor = self.conn.execute("""
            UPDATE emails
            SET business_category = ?, llm_confidence = ?, llm_decision = ?
            WHERE email_id = ?
        """, (category, confidence, "categorized", email_id))
        self.conn.commit()
        return cursor.rowcount > 0


class MockVectorService:
    """Mock Qdrant-style vector search service."""

    def __init__(self):
        self.vectors = {}
        self.collection_name = "email_embeddings"

    def create_vector(self, email_id: str, text: str) -> Dict[str, Any]:
        """Mock vector creation."""
        # Simulate vector embedding (768 dimensions like nomic-embed-text)
        vector = [random.random() for _ in range(768)]
        self.vectors[email_id] = {
            "vector": vector,
            "text": text,
            "created_at": datetime.now().isoformat()
        }
        return {"success": True, "vector_id": email_id}

    def search_vectors(self, query: str, limit: int = 10) -> List[Dict[str, Any]]:
        """Mock semantic search."""
        # Return mock search results with relevance scores
        results = []
        email_keywords = {
            "aidvantage": ["student", "loan", "payment"],
            "planning": ["quarterly", "meeting", "action"],
            "madrid": ["flight", "travel", "spain"],
            "consulting": ["client", "cloud", "migration"]
        }

        query_lower = query.lower()
        for email_id, vector_data in self.vectors.items():
            score = 0.3  # Base score

            # Simple keyword matching for mock relevance
            for keyword, related_words in email_keywords.items():
                if keyword in query_lower:
                    for word in related_words:
                        if word in vector_data["text"].lower():
                            score += 0.2

            if score > 0.4:  # Threshold for relevance
                results.append({
                    "email_id": email_id,
                    "score": min(score, 1.0),
                    "text_snippet": vector_data["text"][:200] + "..."
                })

        # Sort by score and limit results
        results.sort(key=lambda x: x["score"], reverse=True)
        return results[:limit]

    def get_collection_info(self) -> Dict[str, Any]:
        """Get vector collection statistics."""
        return {
            "collection_name": self.collection_name,
            "vectors_count": len(self.vectors),
            "dimension": 768,
            "status": "active"
        }


class MockEmailService:
    """Main mock email service orchestrating all components."""

    def __init__(self):
        self.auth_service = MockAuthenticationService()
        self.database = MockEmailDatabase()
        self.vector_service = MockVectorService()
        self._initialize_vectors()

    def _initialize_vectors(self):
        """Create vectors for existing emails."""
        for account in ["adotob_primary", "gmail_fabsgwill", "gmail_jahmekyanbwoy"]:
            emails = self.database.get_inbox_emails(account, 10)
            for email in emails:
                if email.full_body_text:
                    self.vector_service.create_vector(email.email_id, email.full_body_text)

    def process_inbox(self, account_name: str, limit: int = 50) -> Dict[str, Any]:
        """Mock inbox processing."""
        # Authenticate
        auth_result = self.auth_service.authenticate_account(account_name)
        if not auth_result["success"]:
            return auth_result

        # Get emails
        emails = self.database.get_inbox_emails(account_name, limit)

        # Mock processing statistics
        return {
            "success": True,
            "account": account_name,
            "type": auth_result["type"],
            "stats": {
                "emails_processed": len(emails),
                "emails_found": len(emails),
                "authentication_errors": 0,
                "api_errors": 0
            },
            "emails": [
                {
                    "email_id": email.email_id,
                    "subject": email.subject,
                    "sender": email.sender_email,
                    "urgency": email.urgency_score,
                    "category": email.business_category
                }
                for email in emails[:5]  # Return summary of first 5
            ]
        }

    def hybrid_search(self, query: str, account_filter: Optional[str] = None) -> Dict[str, Any]:
        """Mock hybrid search combining vector and SQL."""
        # Vector search
        vector_results = self.vector_service.search_vectors(query, 5)

        # SQL search
        sql_results = self.database.search_emails(query, account_filter)

        # Combine results
        combined_results = []

        # Add vector results with scores
        for result in vector_results:
            combined_results.append({
                "email_id": result["email_id"],
                "source": "vector",
                "score": result["score"],
                "snippet": result["text_snippet"]
            })

        # Add SQL results
        for email in sql_results[:3]:
            if not any(r["email_id"] == email.email_id for r in combined_results):
                combined_results.append({
                    "email_id": email.email_id,
                    "source": "sql",
                    "score": 0.8,  # Fixed score for SQL matches
                    "snippet": (email.full_body_text or "")[:200] + "..."
                })

        return {
            "success": True,
            "query": query,
            "total_results": len(combined_results),
            "vector_results": len(vector_results),
            "sql_results": len(sql_results),
            "results": combined_results
        }

    def get_system_status(self) -> Dict[str, Any]:
        """Get overall system status."""
        email_counts = self.database.get_email_count_by_account()
        vector_info = self.vector_service.get_collection_info()

        return {
            "success": True,
            "email_counts": email_counts,
            "total_emails": sum(email_counts.values()),
            "vector_status": vector_info,
            "accounts_configured": len(self.auth_service.accounts),
            "system_status": "operational"
        }