"""
HelpDesk AI — Smart Customer Support Chatbot
==============================================
An intelligent customer support chatbot with ticket management,
FAQ knowledge base, smart query routing, and a professional dashboard.

Features:
  - Groq AI (Llama 3) for intelligent response generation
  - Ticket creation, tracking, and status management
  - FAQ knowledge base with category-based search
  - Customer sentiment detection and priority routing
  - Professional support dashboard with analytics
  - Conversation history and context awareness

Author: Khaled Noaman
Technologies: Python, Flask, Groq API, HTML/CSS/JS
"""

import os
import re
import json
import random
import hashlib
from datetime import datetime, timedelta

import requests as http_requests
from flask import Flask, render_template_string, request, jsonify, session

app = Flask(__name__)
app.secret_key = os.urandom(24)

# ============================================
# Groq API Configuration
# ============================================
def load_api_key():
    env_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), '.env')
    if os.path.exists(env_path):
        with open(env_path, 'r') as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#') and '=' in line:
                    key, value = line.split('=', 1)
                    if key.strip() == 'GROQ_API_KEY':
                        return value.strip()
    return os.environ.get("GROQ_API_KEY", "")

GROQ_API_KEY = load_api_key()
GROQ_MODEL = "llama-3.3-70b-versatile"
GROQ_URL = "https://api.groq.com/openai/v1/chat/completions"

SYSTEM_PROMPT = """You are HelpDesk AI, a professional and friendly customer support assistant for a technology company.

Your responsibilities:
- Answer customer questions about products, services, billing, and technical issues
- Help troubleshoot common problems step by step
- Create support tickets when issues need escalation
- Provide clear, empathetic, and solution-oriented responses
- Direct users to appropriate resources when needed

Guidelines:
- Always be polite, professional, and empathetic
- Acknowledge the customer's frustration when they express dissatisfaction
- Provide step-by-step solutions when possible
- If you can't solve something, offer to escalate it
- Use simple language, avoid jargon
- Keep responses concise but complete (2-5 sentences for simple queries)
- Use emojis sparingly for friendliness

You were created by Khaled Noaman, a Computer Engineering student."""


# ============================================
# FAQ Knowledge Base
# ============================================
FAQ_DATABASE = {
    "billing": {
        "icon": "💳",
        "questions": {
            "How do I update my payment method?": "You can update your payment method by going to Settings > Billing > Payment Methods. Click 'Add New' or 'Edit' next to your existing payment method. We accept Visa, Mastercard, and PayPal.",
            "Where can I find my invoices?": "Your invoices are available under Settings > Billing > Invoice History. You can download them as PDF or have them sent to your email automatically each month.",
            "How do I cancel my subscription?": "To cancel, go to Settings > Subscription > Cancel Plan. Your access will continue until the end of your current billing period. You can reactivate anytime.",
            "Can I get a refund?": "We offer a 30-day money-back guarantee for all plans. To request a refund, please contact our billing team or create a support ticket with your order details.",
            "What payment methods do you accept?": "We accept Visa, Mastercard, American Express, PayPal, and bank transfers for annual plans. All payments are processed securely through Stripe."
        }
    },
    "account": {
        "icon": "👤",
        "questions": {
            "How do I reset my password?": "Click 'Forgot Password' on the login page, enter your email, and we'll send a reset link. The link expires in 24 hours. Check your spam folder if you don't see the email.",
            "How do I change my email address?": "Go to Settings > Account > Email. Enter your new email and verify it through the confirmation link we'll send. Your old email will remain active for 48 hours.",
            "How do I enable two-factor authentication?": "Navigate to Settings > Security > Two-Factor Authentication. You can use an authenticator app (recommended) or SMS verification. We support Google Authenticator and Authy.",
            "How do I delete my account?": "Go to Settings > Account > Delete Account. Please note this action is permanent and all your data will be removed after 30 days. Consider exporting your data first.",
            "I can't log into my account": "Try resetting your password first. If that doesn't work, clear your browser cache and cookies, then try again. If you're still locked out, contact support with your registered email."
        }
    },
    "technical": {
        "icon": "🔧",
        "questions": {
            "The app is running slow": "Try these steps: 1) Clear your browser cache, 2) Disable browser extensions, 3) Check your internet speed at speedtest.net, 4) Try a different browser. If the issue persists, our team will investigate.",
            "I'm getting an error message": "Please provide the exact error message or error code. Common fixes include: clearing cache, updating your browser, disabling extensions, or trying incognito mode.",
            "How do I export my data?": "Go to Settings > Data > Export. Choose your preferred format (CSV, JSON, or PDF). Large exports may take a few minutes and will be sent to your email when ready.",
            "Is there a mobile app?": "Yes! Our mobile app is available on both iOS (App Store) and Android (Google Play). Search for our company name, or visit our website for direct download links.",
            "What browsers are supported?": "We support the latest versions of Chrome, Firefox, Safari, and Edge. We recommend Chrome or Firefox for the best experience. Internet Explorer is not supported."
        }
    },
    "features": {
        "icon": "✨",
        "questions": {
            "What's included in the free plan?": "The free plan includes: 5 projects, 1GB storage, basic analytics, email support, and access to core features. Upgrade to Pro for unlimited projects and premium features.",
            "What are the differences between plans?": "Free: 5 projects, 1GB. Pro ($9/mo): Unlimited projects, 50GB, priority support. Enterprise ($29/mo): Everything in Pro + custom integrations, SLA, and dedicated account manager.",
            "Do you offer team collaboration?": "Yes! Team features are available on Pro and Enterprise plans. You can invite team members, set permissions, share projects, and collaborate in real-time.",
            "Can I integrate with other tools?": "We integrate with Slack, Jira, GitHub, Trello, Google Workspace, and Microsoft 365. API access is available on Pro plans and above for custom integrations.",
            "Is there an API available?": "Yes! Our REST API is available for Pro and Enterprise users. Full documentation is at docs.example.com/api. Rate limits vary by plan."
        }
    }
}


# ============================================
# Ticket System
# ============================================
class TicketSystem:
    def __init__(self):
        self.tickets = {}
        self.ticket_counter = 1000
    
    def create_ticket(self, subject, description, priority="medium", category="general"):
        self.ticket_counter += 1
        ticket_id = f"HD-{self.ticket_counter}"
        ticket = {
            "id": ticket_id,
            "subject": subject,
            "description": description,
            "priority": priority,
            "category": category,
            "status": "open",
            "created_at": datetime.now().isoformat(),
            "updated_at": datetime.now().isoformat(),
            "messages": []
        }
        self.tickets[ticket_id] = ticket
        return ticket
    
    def get_ticket(self, ticket_id):
        return self.tickets.get(ticket_id.upper())
    
    def update_status(self, ticket_id, status):
        ticket = self.tickets.get(ticket_id.upper())
        if ticket:
            ticket["status"] = status
            ticket["updated_at"] = datetime.now().isoformat()
            return ticket
        return None
    
    def get_all_tickets(self):
        return list(self.tickets.values())
    
    def get_stats(self):
        tickets = list(self.tickets.values())
        return {
            "total": len(tickets),
            "open": sum(1 for t in tickets if t["status"] == "open"),
            "in_progress": sum(1 for t in tickets if t["status"] == "in_progress"),
            "resolved": sum(1 for t in tickets if t["status"] == "resolved"),
            "high_priority": sum(1 for t in tickets if t["priority"] == "high")
        }


# ============================================
# AI Response Engine
# ============================================
class SupportAI:
    def __init__(self, api_key):
        self.api_key = api_key
        self.conversations = {}
        self.ticket_system = TicketSystem()
    
    def is_available(self):
        return bool(self.api_key) and len(self.api_key) > 10
    
    def detect_priority(self, message):
        msg = message.lower()
        high_keywords = ['urgent', 'emergency', 'down', 'broken', 'critical', 'asap', 'immediately', 'not working', 'crashed', 'data loss', 'security', 'hacked', 'breach']
        medium_keywords = ['issue', 'problem', 'error', 'bug', 'slow', 'help', 'trouble', 'unable', 'cannot', 'wrong']
        
        if any(kw in msg for kw in high_keywords):
            return "high"
        elif any(kw in msg for kw in medium_keywords):
            return "medium"
        return "low"
    
    def detect_category(self, message):
        msg = message.lower()
        if any(w in msg for w in ['bill', 'pay', 'invoice', 'charge', 'refund', 'price', 'cost', 'subscription', 'plan', 'upgrade']):
            return "billing"
        elif any(w in msg for w in ['password', 'login', 'account', 'email', 'profile', 'sign', '2fa', 'security', 'delete account']):
            return "account"
        elif any(w in msg for w in ['error', 'bug', 'slow', 'crash', 'broken', 'fix', 'update', 'install', 'browser', 'app']):
            return "technical"
        elif any(w in msg for w in ['feature', 'plan', 'api', 'integrate', 'team', 'collaboration']):
            return "features"
        return "general"
    
    def detect_sentiment(self, message):
        msg = message.lower()
        angry = ['angry', 'furious', 'terrible', 'worst', 'hate', 'ridiculous', 'unacceptable', 'disgusting', 'scam', 'fraud', 'horrible']
        frustrated = ['frustrated', 'annoying', 'disappointed', 'unhappy', 'still', 'again', 'keeps', 'already tried', 'nothing works']
        happy = ['thanks', 'thank', 'great', 'awesome', 'love', 'perfect', 'excellent', 'wonderful', 'appreciate', 'helpful', 'solved']
        
        if any(w in msg for w in angry):
            return "angry", "high"
        elif any(w in msg for w in frustrated):
            return "frustrated", "medium"  
        elif any(w in msg for w in happy):
            return "happy", "low"
        return "neutral", "normal"
    
    def search_faq(self, message):
        msg = message.lower()
        best_match = None
        best_score = 0
        
        for category, data in FAQ_DATABASE.items():
            for question, answer in data["questions"].items():
                q_words = set(question.lower().split())
                m_words = set(msg.split())
                overlap = len(q_words & m_words)
                score = overlap / max(len(q_words), 1)
                if score > best_score and score > 0.25:
                    best_score = score
                    best_match = {"question": question, "answer": answer, "category": category, "score": score}
        
        return best_match
    
    def get_response(self, user_message, session_id="default"):
        if session_id not in self.conversations:
            self.conversations[session_id] = {"history": [], "message_count": 0}
        
        ctx = self.conversations[session_id]
        ctx["message_count"] += 1
        
        priority = self.detect_priority(user_message)
        category = self.detect_category(user_message)
        sentiment, urgency = self.detect_sentiment(user_message)
        faq_match = self.search_faq(user_message)
        
        # Check for ticket commands
        msg_lower = user_message.lower().strip()
        ticket_created = None
        
        if msg_lower.startswith("create ticket") or msg_lower.startswith("new ticket") or "open a ticket" in msg_lower:
            subject = user_message.split(":", 1)[1].strip() if ":" in user_message else user_message
            ticket = self.ticket_system.create_ticket(subject, user_message, priority, category)
            ticket_created = ticket
        
        # Try AI response
        response = None
        source = "local"
        
        if self.is_available():
            ai_response = self._call_groq(user_message, session_id, faq_match, ticket_created)
            if ai_response:
                response = ai_response
                source = "groq"
        
        if not response:
            if faq_match and faq_match["score"] > 0.3:
                response = f"📋 **FAQ Match:**\n\n{faq_match['answer']}\n\nDoes this answer your question? If not, I can create a support ticket for you."
            elif ticket_created:
                response = f"✅ I've created ticket **{ticket_created['id']}** for you!\n\n• **Priority:** {priority.upper()}\n• **Category:** {category}\n• **Status:** Open\n\nOur team will get back to you shortly."
            else:
                response = "I'd be happy to help! Could you provide more details about your issue? I can assist with billing, account, technical problems, or feature questions. 😊"
        
        ctx["history"].append({
            "user": user_message, "bot": response,
            "priority": priority, "category": category,
            "sentiment": sentiment, "source": source,
            "ticket": ticket_created["id"] if ticket_created else None,
            "timestamp": datetime.now().isoformat()
        })
        
        return {
            "response": response,
            "priority": priority,
            "category": category,
            "sentiment": sentiment,
            "faq_match": faq_match is not None,
            "ticket": ticket_created,
            "source": source,
            "message_count": ctx["message_count"]
        }
    
    def _call_groq(self, user_message, session_id, faq_match, ticket):
        history = self.conversations.get(session_id, {}).get("history", [])
        
        messages = [{"role": "system", "content": SYSTEM_PROMPT}]
        
        # Add context about FAQ match or ticket
        context = ""
        if faq_match:
            context += f"\n\n[CONTEXT: A relevant FAQ was found - Q: '{faq_match['question']}' A: '{faq_match['answer']}'. Use this to inform your response but rephrase naturally.]"
        if ticket:
            context += f"\n\n[CONTEXT: A support ticket {ticket['id']} was just created for this issue. Acknowledge the ticket in your response.]"
        
        if context:
            messages[0]["content"] += context
        
        for exchange in history[-8:]:
            messages.append({"role": "user", "content": exchange["user"]})
            messages.append({"role": "assistant", "content": exchange["bot"]})
        
        messages.append({"role": "user", "content": user_message})
        
        try:
            resp = http_requests.post(
                GROQ_URL,
                json={"model": GROQ_MODEL, "messages": messages, "temperature": 0.7, "max_tokens": 400},
                headers={"Authorization": f"Bearer {self.api_key}", "Content-Type": "application/json"},
                timeout=15
            )
            if resp.status_code == 200:
                return resp.json()["choices"][0]["message"]["content"]
        except Exception as e:
            print(f"[Groq Error] {e}")
        return None


# ============================================
# Initialize
# ============================================
support_ai = SupportAI(GROQ_API_KEY)


# ============================================
# HTML Template
# ============================================
HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>HelpDesk AI — Customer Support</title>
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap" rel="stylesheet">
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        :root {
            --bg: #f0f4f8; --bg-dark: #1a1a2e; --card: #ffffff;
            --primary: #0066ff; --primary-light: #e8f0fe;
            --success: #10b981; --warning: #f59e0b; --danger: #ef4444;
            --text: #1e293b; --text-light: #64748b; --border: #e2e8f0;
            --shadow: 0 4px 20px rgba(0,0,0,0.08);
        }
        body { font-family: 'Inter', sans-serif; background: var(--bg); color: var(--text); height: 100vh; overflow: hidden; }

        .app { display: flex; height: 100vh; }

        /* Sidebar */
        .sidebar { width: 300px; background: var(--bg-dark); color: white; display: flex; flex-direction: column; padding: 20px; }
        .logo { display: flex; align-items: center; gap: 12px; margin-bottom: 24px; padding-bottom: 16px; border-bottom: 1px solid rgba(255,255,255,0.1); }
        .logo-icon { width: 42px; height: 42px; background: linear-gradient(135deg, var(--primary), #00c6ff); border-radius: 12px; display: flex; align-items: center; justify-content: center; font-size: 20px; }
        .logo h1 { font-size: 18px; font-weight: 700; }
        .logo span { font-size: 11px; color: #94a3b8; display: block; }

        .stats-grid { display: grid; grid-template-columns: 1fr 1fr; gap: 10px; margin-bottom: 20px; }
        .stat-box { background: rgba(255,255,255,0.06); border-radius: 10px; padding: 12px; text-align: center; border: 1px solid rgba(255,255,255,0.08); }
        .stat-box .num { font-size: 22px; font-weight: 700; color: #60a5fa; }
        .stat-box .label { font-size: 10px; color: #94a3b8; text-transform: uppercase; letter-spacing: 0.5px; margin-top: 2px; }

        .faq-section { flex: 1; overflow-y: auto; }
        .faq-section h3 { font-size: 12px; text-transform: uppercase; letter-spacing: 1px; color: #94a3b8; margin-bottom: 10px; }
        .faq-category { margin-bottom: 12px; }
        .faq-cat-title { font-size: 13px; font-weight: 600; margin-bottom: 6px; color: #cbd5e1; cursor: pointer; }
        .faq-cat-title:hover { color: #60a5fa; }
        .faq-item { font-size: 12px; color: #94a3b8; padding: 5px 0 5px 12px; cursor: pointer; border-left: 2px solid transparent; transition: all 0.2s; }
        .faq-item:hover { color: white; border-left-color: var(--primary); }

        /* Main */
        .main { flex: 1; display: flex; flex-direction: column; }
        .header { padding: 14px 24px; background: var(--card); border-bottom: 1px solid var(--border); display: flex; align-items: center; justify-content: space-between; }
        .header h2 { font-size: 16px; font-weight: 600; }
        .status { display: flex; align-items: center; gap: 6px; font-size: 13px; color: var(--success); }
        .status-dot { width: 8px; height: 8px; background: var(--success); border-radius: 50%; animation: pulse 2s infinite; }
        @keyframes pulse { 0%,100%{opacity:1} 50%{opacity:0.4} }

        .messages { flex: 1; overflow-y: auto; padding: 20px 24px; background: var(--bg); }
        .messages::-webkit-scrollbar { width: 5px; }
        .messages::-webkit-scrollbar-thumb { background: #cbd5e1; border-radius: 3px; }

        .msg { display: flex; margin-bottom: 14px; animation: slideIn 0.3s ease; }
        @keyframes slideIn { from{opacity:0;transform:translateY(8px)} to{opacity:1;transform:translateY(0)} }
        .msg-user { justify-content: flex-end; }
        .msg-bubble { max-width: 65%; padding: 12px 16px; border-radius: 14px; font-size: 14px; line-height: 1.6; }
        .msg-user .msg-bubble { background: var(--primary); color: white; border-bottom-right-radius: 4px; }
        .msg-bot .msg-bubble { background: var(--card); border: 1px solid var(--border); border-bottom-left-radius: 4px; box-shadow: var(--shadow); }
        .msg-bot .msg-bubble strong { color: var(--primary); }

        .bot-avatar { width: 32px; height: 32px; background: linear-gradient(135deg, var(--primary), #00c6ff); border-radius: 10px; display: flex; align-items: center; justify-content: center; font-size: 14px; margin-right: 10px; flex-shrink: 0; }
        .msg-meta { display: flex; gap: 6px; margin-top: 4px; flex-wrap: wrap; }
        .tag { font-size: 10px; padding: 2px 6px; border-radius: 4px; font-weight: 500; }
        .tag-priority-high { background: #fef2f2; color: var(--danger); }
        .tag-priority-medium { background: #fffbeb; color: var(--warning); }
        .tag-priority-low { background: #f0fdf4; color: var(--success); }
        .tag-category { background: var(--primary-light); color: var(--primary); }
        .tag-ticket { background: #f3e8ff; color: #7c3aed; }

        .typing { display: none; margin-left: 42px; }
        .typing.active { display: block; }
        .typing-dots { display: flex; gap: 3px; background: var(--card); border: 1px solid var(--border); border-radius: 14px; padding: 10px 16px; width: fit-content; box-shadow: var(--shadow); }
        .typing-dots span { width: 6px; height: 6px; background: #94a3b8; border-radius: 50%; animation: bounce 1.4s infinite; }
        .typing-dots span:nth-child(2){animation-delay:.2s}
        .typing-dots span:nth-child(3){animation-delay:.4s}
        @keyframes bounce { 0%,60%,100%{transform:translateY(0)} 30%{transform:translateY(-5px)} }

        .welcome { text-align: center; padding: 60px 40px; }
        .welcome-icon { font-size: 56px; margin-bottom: 16px; }
        .welcome h2 { font-size: 24px; font-weight: 700; color: var(--text); margin-bottom: 6px; }
        .welcome p { color: var(--text-light); font-size: 14px; margin-bottom: 24px; }
        .chips { display: flex; gap: 8px; flex-wrap: wrap; justify-content: center; }
        .chip { padding: 8px 14px; background: var(--card); border: 1px solid var(--border); border-radius: 20px; font-size: 13px; cursor: pointer; transition: all 0.2s; box-shadow: 0 2px 8px rgba(0,0,0,0.04); }
        .chip:hover { border-color: var(--primary); background: var(--primary-light); transform: translateY(-2px); }

        .input-area { padding: 14px 24px; background: var(--card); border-top: 1px solid var(--border); }
        .input-wrap { display: flex; gap: 10px; }
        #msgInput { flex: 1; background: var(--bg); border: 1px solid var(--border); border-radius: 12px; padding: 12px 16px; font-size: 14px; font-family: 'Inter',sans-serif; outline: none; transition: border 0.3s; }
        #msgInput:focus { border-color: var(--primary); }
        .send-btn { width: 44px; height: 44px; background: var(--primary); border: none; border-radius: 12px; color: white; font-size: 16px; cursor: pointer; transition: all 0.2s; }
        .send-btn:hover { transform: scale(1.05); box-shadow: 0 4px 12px rgba(0,102,255,0.3); }

        /* Analysis Panel */
        .panel { width: 260px; background: var(--card); border-left: 1px solid var(--border); padding: 20px; overflow-y: auto; }
        .panel h3 { font-size: 12px; text-transform: uppercase; letter-spacing: 1px; color: var(--text-light); margin-bottom: 12px; }
        .panel-card { background: var(--bg); border-radius: 10px; padding: 12px; margin-bottom: 10px; }
        .panel-card .lbl { font-size: 11px; color: var(--text-light); text-transform: uppercase; letter-spacing: 0.5px; }
        .panel-card .val { font-size: 16px; font-weight: 600; color: var(--primary); margin-top: 2px; }
        .priority-bar { height: 6px; background: var(--border); border-radius: 3px; margin-top: 6px; overflow: hidden; }
        .priority-fill { height: 100%; border-radius: 3px; transition: width 0.5s; }
        .priority-fill.high { background: var(--danger); }
        .priority-fill.medium { background: var(--warning); }
        .priority-fill.low { background: var(--success); }

        .ticket-list { margin-top: 8px; }
        .ticket-item { font-size: 12px; padding: 6px 8px; background: var(--card); border: 1px solid var(--border); border-radius: 6px; margin-bottom: 4px; display: flex; justify-content: space-between; }
        .ticket-item .tid { font-weight: 600; color: #7c3aed; }
        .ticket-status { font-size: 10px; padding: 2px 6px; border-radius: 3px; font-weight: 500; }
        .ticket-status.open { background: #fef2f2; color: var(--danger); }
        .ticket-status.resolved { background: #f0fdf4; color: var(--success); }

        @media(max-width:1024px) { .sidebar,.panel { display:none; } }
        @media(max-width:768px) { .msg-bubble { max-width: 85%; } }
    </style>
</head>
<body>
<div class="app">
    <aside class="sidebar">
        <div class="logo">
            <div class="logo-icon">🎧</div>
            <div><h1>HelpDesk AI</h1><span>Smart Support v1.0</span></div>
        </div>
        <div class="stats-grid">
            <div class="stat-box"><div class="num" id="statTotal">0</div><div class="label">Tickets</div></div>
            <div class="stat-box"><div class="num" id="statOpen">0</div><div class="label">Open</div></div>
            <div class="stat-box"><div class="num" id="statResolved">0</div><div class="label">Resolved</div></div>
            <div class="stat-box"><div class="num" id="statMsgs">0</div><div class="label">Messages</div></div>
        </div>
        <div class="faq-section">
            <h3>📚 Quick Help</h3>
            <div class="faq-category"><div class="faq-cat-title">💳 Billing</div>
                <div class="faq-item" onclick="ask('How do I update my payment method?')">Update payment method</div>
                <div class="faq-item" onclick="ask('How do I cancel my subscription?')">Cancel subscription</div>
                <div class="faq-item" onclick="ask('Can I get a refund?')">Request a refund</div>
            </div>
            <div class="faq-category"><div class="faq-cat-title">👤 Account</div>
                <div class="faq-item" onclick="ask('How do I reset my password?')">Reset password</div>
                <div class="faq-item" onclick="ask('How do I enable two-factor authentication?')">Enable 2FA</div>
                <div class="faq-item" onclick="ask('I cannot log into my account')">Login issues</div>
            </div>
            <div class="faq-category"><div class="faq-cat-title">🔧 Technical</div>
                <div class="faq-item" onclick="ask('The app is running slow')">App is slow</div>
                <div class="faq-item" onclick="ask('I am getting an error message')">Error messages</div>
                <div class="faq-item" onclick="ask('How do I export my data?')">Export data</div>
            </div>
            <div class="faq-category"><div class="faq-cat-title">✨ Features</div>
                <div class="faq-item" onclick="ask('What is included in the free plan?')">Free plan details</div>
                <div class="faq-item" onclick="ask('Do you offer team collaboration?')">Team collaboration</div>
                <div class="faq-item" onclick="ask('Is there an API available?')">API access</div>
            </div>
        </div>
    </aside>

    <main class="main">
        <div class="header">
            <h2>🎧 Customer Support Chat</h2>
            <div class="status"><div class="status-dot"></div>Support Online</div>
        </div>
        <div class="messages" id="messages">
            <div class="welcome" id="welcome">
                <div class="welcome-icon">🎧</div>
                <h2>Welcome to HelpDesk AI</h2>
                <p>How can we help you today?</p>
                <div class="chips">
                    <div class="chip" onclick="ask('I need help with my billing')">💳 Billing Help</div>
                    <div class="chip" onclick="ask('I cannot log into my account')">🔐 Login Issue</div>
                    <div class="chip" onclick="ask('The app is running slow')">🐌 App is Slow</div>
                    <div class="chip" onclick="ask('I want to know about your pricing plans')">💰 Pricing</div>
                    <div class="chip" onclick="ask('Create ticket: I need help with a technical issue')">🎫 Create Ticket</div>
                </div>
            </div>
            <div class="typing" id="typing"><div class="typing-dots"><span></span><span></span><span></span></div></div>
        </div>
        <div class="input-area">
            <div class="input-wrap">
                <input type="text" id="msgInput" placeholder="Describe your issue..." autocomplete="off" autofocus>
                <button class="send-btn" onclick="sendMsg()">➤</button>
            </div>
        </div>
    </main>

    <aside class="panel">
        <h3>📊 Analysis</h3>
        <div class="panel-card"><div class="lbl">Priority</div><div class="val" id="pPriority">—</div>
            <div class="priority-bar"><div class="priority-fill low" id="pBar" style="width:0%"></div></div></div>
        <div class="panel-card"><div class="lbl">Category</div><div class="val" id="pCategory">—</div></div>
        <div class="panel-card"><div class="lbl">Sentiment</div><div class="val" id="pSentiment">—</div></div>
        <div class="panel-card"><div class="lbl">FAQ Match</div><div class="val" id="pFaq">—</div></div>
        <h3 style="margin-top:16px">🎫 Recent Tickets</h3>
        <div class="ticket-list" id="ticketList"><p style="font-size:12px;color:var(--text-light)">No tickets yet</p></div>
    </aside>
</div>
<script>
const msgs = document.getElementById('messages');
const input = document.getElementById('msgInput');
const welcome = document.getElementById('welcome');
const typing = document.getElementById('typing');
let totalMsgs = 0;
let tickets = [];

input.addEventListener('keypress', e => { if(e.key==='Enter') sendMsg(); });
function ask(t) { input.value = t; sendMsg(); }

async function sendMsg() {
    const m = input.value.trim(); if(!m) return;
    if(welcome) welcome.style.display='none';
    addMsg(m,'user'); input.value='';
    typing.classList.add('active');
    msgs.scrollTop = msgs.scrollHeight;
    try {
        const r = await fetch('/api/chat',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({message:m})});
        const d = await r.json();
        setTimeout(() => {
            typing.classList.remove('active');
            addMsg(d.response,'bot',d);
            updatePanel(d);
            totalMsgs++;
            document.getElementById('statMsgs').textContent = totalMsgs;
            if(d.ticket) { tickets.push(d.ticket); updateTickets(); }
        }, 400+Math.random()*400);
    } catch(e) { typing.classList.remove('active'); addMsg('Sorry, something went wrong. Please try again.','bot'); }
}

function addMsg(text,sender,data=null) {
    const d = document.createElement('div'); d.className = `msg msg-${sender}`;
    let formatted = text.replace(/\\*\\*(.*?)\\*\\*/g,'<strong>$1</strong>').replace(/\\n/g,'<br>');
    if(sender==='bot') {
        let meta = '';
        if(data) {
            meta = '<div class="msg-meta">';
            meta += `<span class="tag tag-priority-${data.priority}">${data.priority.toUpperCase()}</span>`;
            meta += `<span class="tag tag-category">${data.category}</span>`;
            if(data.ticket) meta += `<span class="tag tag-ticket">🎫 ${data.ticket.id}</span>`;
            meta += '</div>';
        }
        d.innerHTML = `<div class="bot-avatar">🎧</div><div><div class="msg-bubble">${formatted}</div>${meta}</div>`;
    } else {
        d.innerHTML = `<div class="msg-bubble">${formatted}</div>`;
    }
    msgs.insertBefore(d, typing);
    msgs.scrollTop = msgs.scrollHeight;
}

function updatePanel(d) {
    const pMap = {high:'🔴 High',medium:'🟡 Medium',low:'🟢 Low'};
    const sMap = {angry:'😠 Angry',frustrated:'😤 Frustrated',happy:'😊 Happy',neutral:'😐 Neutral'};
    document.getElementById('pPriority').textContent = pMap[d.priority]||d.priority;
    document.getElementById('pCategory').textContent = d.category.charAt(0).toUpperCase()+d.category.slice(1);
    document.getElementById('pSentiment').textContent = sMap[d.sentiment]||d.sentiment;
    document.getElementById('pFaq').textContent = d.faq_match?'✅ Found':'❌ None';
    const bar = document.getElementById('pBar');
    bar.className = `priority-fill ${d.priority}`;
    bar.style.width = d.priority==='high'?'100%':d.priority==='medium'?'60%':'30%';
}

function updateTickets() {
    const tl = document.getElementById('ticketList');
    const stats = {total:tickets.length, open:tickets.filter(t=>t.status==='open').length, resolved:0};
    document.getElementById('statTotal').textContent = stats.total;
    document.getElementById('statOpen').textContent = stats.open;
    document.getElementById('statResolved').textContent = stats.resolved;
    tl.innerHTML = tickets.map(t => `<div class="ticket-item"><span class="tid">${t.id}</span><span class="ticket-status open">${t.status}</span></div>`).join('');
}
</script>
</body>
</html>
"""


# ============================================
# Routes
# ============================================
@app.route('/')
def home():
    return render_template_string(HTML_TEMPLATE)

@app.route('/api/chat', methods=['POST'])
def chat():
    data = request.json
    msg = data.get('message', '').strip()
    if not msg:
        return jsonify({"error": "Empty message"}), 400
    sid = session.get('sid', 'default')
    if 'sid' not in session:
        session['sid'] = os.urandom(8).hex()
        sid = session['sid']
    return jsonify(support_ai.get_response(msg, sid))

@app.route('/api/faq', methods=['GET'])
def faq():
    return jsonify(FAQ_DATABASE)

@app.route('/api/tickets', methods=['GET'])
def get_tickets():
    return jsonify(support_ai.ticket_system.get_all_tickets())

@app.route('/api/tickets/stats', methods=['GET'])
def ticket_stats():
    return jsonify(support_ai.ticket_system.get_stats())

if __name__ == '__main__':
    print("=" * 50)
    print("  HelpDesk AI — Customer Support Chatbot")
    print("  Powered by Groq (Llama 3)")
    print("=" * 50)
    mode = "Groq AI" if support_ai.is_available() else "Local FAQ"
    print(f"  Mode: {mode}")
    print("  Open: http://localhost:5001")
    print("=" * 50)
    app.run(debug=True, port=5001)
