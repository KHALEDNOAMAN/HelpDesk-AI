# 🎧 HelpDesk AI — Smart Customer Support Chatbot

![Python](https://img.shields.io/badge/Python-3776AB?style=for-the-badge&logo=python&logoColor=white)
![Flask](https://img.shields.io/badge/Flask-000000?style=for-the-badge&logo=flask&logoColor=white)
![Groq](https://img.shields.io/badge/Groq_AI-000000?style=for-the-badge&logoColor=white)
![License](https://img.shields.io/badge/License-MIT-green?style=for-the-badge)

> **An intelligent customer support chatbot with AI-powered responses, ticket management, FAQ knowledge base, priority routing, and sentiment detection.**

---

## 🎯 Overview

HelpDesk AI is a full-featured customer support chatbot built with Python and Flask. It combines **Groq's Llama 3 70B** model for intelligent responses with a local **FAQ knowledge base**, **ticket management system**, and **smart routing** based on customer priority and sentiment analysis.

## ✨ Key Features

| Feature | Description |
|---------|-------------|
| 🤖 **AI-Powered Responses** | Groq (Llama 3 70B) for smart, contextual support answers |
| 🎫 **Ticket System** | Create, track, and manage support tickets with auto-prioritization |
| 📚 **FAQ Knowledge Base** | 20+ categorized FAQs across billing, account, technical, and features |
| 🚨 **Smart Priority Routing** | Automatic priority detection (High/Medium/Low) from message content |
| 😊 **Sentiment Analysis** | Detects customer emotions (angry, frustrated, happy, neutral) |
| 📂 **Category Detection** | Auto-classifies issues into billing, account, technical, or features |
| 📊 **Live Dashboard** | Real-time stats: ticket count, open issues, message analytics |
| 🔌 **REST API** | JSON endpoints for chat, FAQ, tickets, and statistics |

## 🖥️ Interface

The app features a **3-panel professional layout**:
- **Left** — Stats dashboard, FAQ quick-access menu
- **Center** — Chat interface with priority/category tags on each message
- **Right** — Real-time analysis panel showing priority, category, sentiment, and tickets

## 🛠️ Tech Stack

| Technology | Purpose |
|-----------|---------|
| Python 3.9+ | Core language |
| Flask | Web server & REST API |
| Groq API | Llama 3 70B language model |
| HTML/CSS/JS | Professional support dashboard |

## 🏗️ Architecture

```
┌─────────────────────────────────────────────┐
│              Web Dashboard                   │
│  ┌──────┐  ┌──────────┐  ┌──────────────┐  │
│  │Stats │  │   Chat   │  │  Analysis    │  │
│  │ FAQ  │  │  Window  │  │  Panel       │  │
│  └──────┘  └────┬─────┘  └──────────────┘  │
└─────────────────┼───────────────────────────┘
                  │ REST API
┌─────────────────┼───────────────────────────┐
│           Flask Server                       │
│  ┌──────────────┼──────────────────────┐    │
│  │        Support AI Engine            │    │
│  │  ┌──────────┐ ┌─────────────────┐  │    │
│  │  │ Priority │ │  Sentiment      │  │    │
│  │  │ Detector │ │  Analyzer       │  │    │
│  │  └──────────┘ └─────────────────┘  │    │
│  │  ┌──────────┐ ┌─────────────────┐  │    │
│  │  │ Category │ │  FAQ Search     │  │    │
│  │  │ Router   │ │  Engine         │  │    │
│  │  └──────────┘ └─────────────────┘  │    │
│  └────────────────────────────────────┘    │
│  ┌──────────────┐  ┌──────────────────┐    │
│  │ Ticket System │  │  Groq AI Client │    │
│  │ (CRUD + Stats)│  │  (Llama 3 70B) │    │
│  └──────────────┘  └──────────────────┘    │
└─────────────────────────────────────────────┘
```

## 🚀 Getting Started

### Prerequisites
```bash
Python >= 3.8
Groq API key (free at console.groq.com/keys)
```

### Installation & Run
```bash
# Clone the repository
git clone https://github.com/KHALEDNOAMAN/HelpDesk-AI.git
cd HelpDesk-AI

# Install dependencies
pip install -r requirements.txt

# Add your Groq API key
echo GROQ_API_KEY=your_key_here > .env

# Run the chatbot
python app.py
```

Then open **http://localhost:5001** 🌐

## 📡 API Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/` | GET | Support chat dashboard |
| `/api/chat` | POST | Send message, get AI response |
| `/api/faq` | GET | Get full FAQ database |
| `/api/tickets` | GET | List all support tickets |
| `/api/tickets/stats` | GET | Ticket statistics |

## 📁 Project Structure

```
HelpDesk-AI/
├── app.py              # Main app (server + AI + ticket system + UI)
├── requirements.txt    # Python dependencies
├── .env               # API key (not committed)
├── LICENSE
└── README.md
```

## 📄 License

This project is licensed under the MIT License.

## 👤 Author

**Khaled Noaman** — Computer Engineering Student at Istanbul Arel University

- [GitHub](https://github.com/KhaledNoaman)
- [LinkedIn](https://www.linkedin.com/in/khalednoaman1/)
