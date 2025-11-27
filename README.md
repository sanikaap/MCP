<div align="center">

# 🚀 ContentFlow AI

### From Research to Viral Content in Minutes

[![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![Gradio](https://img.shields.io/badge/Gradio-4.44-orange.svg)](https://gradio.app/)
[![OpenRouter](https://img.shields.io/badge/OpenRouter-API-green.svg)](https://openrouter.ai/)
[![License](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

**AI-powered research, analytics, and content generation platform for social media creators**

</div>

---

## 📋 Overview

ContentFlow AI automates your entire content creation workflow:

| Phase            | What It Does                        | Time Saved |
| ---------------- | ----------------------------------- | ---------- |
| 🔬 **Research**  | Searches ArXiv, Web, YouTube        | ~2 hours   |
| 📊 **Analytics** | AI-powered trend analysis           | ~1 hour    |
| ✨ **Create**    | Generates platform-specific content | ~1.5 hours |
| 📅 **Export**    | Ready-to-post content packages      | ~30 mins   |

---

## ✨ Features

<table>
<tr>
<td width="50%">

### 🔬 Multi-Source Research

- 📄 **ArXiv** - Academic papers
- 🌐 **Web Search** - Latest articles
- 🎥 **YouTube** - Video content
- 🤖 **AI Insights** - Key takeaways

</td>
<td width="50%">

### 📊 Smart Analytics

- 📈 Trend analysis
- 🎯 Performance predictions
- 💡 AI recommendations
- ⏰ Optimal posting times

</td>
</tr>
<tr>
<td>

### ✍️ Content Generation

- 🐦 **Twitter** - Threads & tweets
- 💼 **LinkedIn** - Professional posts
- 📸 **Instagram** - Captions & hashtags
- 📝 **Blog** - Full articles

</td>
<td>

</tr>
</table>

---

## 💻 Usage

### 1. Start the Application

```bash
python app.py
```

Open your browser to: **http://localhost:7860**

### 2. Research Your Topic

<img src="https://img.shields.io/badge/Step_1-Research-3b82f6?style=for-the-badge" />

1. Enter your topic (e.g., "AI trends 2024")
2. Select sources (ArXiv, Web, YouTube)
3. Click **🔍 Start Research**
4. Wait 30-60 seconds for results

### 3. Analyze Trends

<img src="https://img.shields.io/badge/Step_2-Analytics-10b981?style=for-the-badge" />

- View AI-powered trend analysis
- Get platform-specific recommendations
- Understand optimal posting strategies

### 4. Generate Content

<img src="https://img.shields.io/badge/Step_3-Generate-f59e0b?style=for-the-badge" />

- Select target platforms
- Choose tone (Professional, Casual, Technical)
- Generate images automatically
- Get ready-to-post content

### 5. Export & Schedule

<img src="https://img.shields.io/badge/Step_4-Export-8b5cf6?style=for-the-badge" />

- Export as JSON, CSV, or Markdown
- Schedule posts for optimal times
- Download complete content packages

---

## 🎯 Demo

### Research Results

```json
{
  "topic": "Quantum Computing",
  "sources": {
    "arxiv": [
      /* 5 papers */
    ],
    "web": [
      /* 5 articles */
    ]
  },
  "key_insights": [
    "Quantum supremacy achieved in 2024",
    "Error correction breakthrough",
    "Commercial applications emerging"
  ]
}
```

### Generated Content

**Twitter Thread:**

```
🧵 Quantum Computing in 2024: The Breakthrough Year

1/5 Major achievement: Error correction now 99.9% accurate
New algorithms solving previously impossible problems

2/5 Commercial applications are here...
```

**LinkedIn Post:**

```
Excited to share insights on Quantum Computing's evolution! 💡

Key developments this year:
• Error correction breakthrough
• Real-world applications emerging
• Investment reaching $15B+

What are your thoughts? #QuantumComputing #AI
```

---

### Tech Stack

- **Frontend:** Gradio (Python web UI)
- **AI:** OpenRouter (Gemini 2.0 Flash)
- **Research:** ArXiv API, DuckDuckGo
- **Database:** SQLite
- **Image:** PIL/Pillow

---
