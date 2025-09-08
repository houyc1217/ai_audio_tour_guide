# 🎧 AI Audio Tour Agent

An intelligent audio tour generator that creates personalized, immersive tours based on your **location**, **interests**, and **preferred duration**. Powered by NetMind's AI models and featuring a sophisticated multi-agent architecture for specialized content generation.

---

## ✨ Key Features

### 🤖 Multi-Agent Architecture

- **Planner Agent**: Analyzes user preferences and creates optimal time allocation plans
- **Architecture Agent**: Provides detailed architectural insights and visual descriptions
- **History Agent**: Delivers engaging historical narratives and stories
- **Culture Agent**: Explores local traditions, arts, and cultural significance
- **Culinary Agent**: Describes local cuisine, specialties, and food culture
- **Orchestrator Agent**: Assembles all content into a cohesive, natural-sounding tour

### 🎯 Personalized Experience

- **Location-based**: Enter any city, landmark, or location worldwide
- **Interest-driven**: Select from History, Architecture, Culture, and Culinary topics
- **Duration control**: Choose tour length from 1-20 minutes with intelligent content scaling
- **Voice styles**: Friendly & Casual, Professional & Detailed, or Enthusiastic & Energetic

### 🔊 High-Quality Audio Generation

- **NetMind TTS**: Powered by ResembleAI/Chatterbox model for natural speech
- **Progress tracking**: Real-time generation progress with time estimates
- **Error resilience**: Robust retry mechanisms and graceful fallback handling
- **Download support**: Save audio tours as MP3 files for offline listening

---

## 🚀 Quick Start

### 1. Installation

```bash
# Clone or download the project
cd ai_audio_tour_agent

# Install dependencies
pip install -r requirements.txt
```

### 2. Get NetMind API Access

- Visit [NetMind API Platform](https://api.netmind.ai/)
- Sign up for an account and obtain your API key
- The application will prompt you to enter the key in the sidebar

### 3. Launch the Application

```bash
# Set your API key (optional - can be entered in UI)
export NETMIND_API_KEY="your_api_key_here"

# Start the Streamlit app
streamlit run ai_audio_tour_agent.py
```

### 4. Create Your Tour

1. **Enter API Key**: Paste your NetMind API key in the sidebar
2. **Choose Location**: Enter any city, landmark, or destination
3. **Select Interests**: Pick from History, Architecture, Culture, Culinary
4. **Set Duration**: Choose tour length (1-20 minutes)
5. **Pick Voice Style**: Select your preferred guide personality
6. **Generate**: Click "Generate Tour" and wait for your personalized audio experience

---

## 🛠️ Technical Architecture

### Core Components

- **`ai_audio_tour_agent.py`**: Main Streamlit application with responsive UI and audio generation
- **`manager.py`**: Tour orchestration engine coordinating all agents with retry logic
- **`agent.py`**: Six specialized AI agents built on pydantic-ai framework
- **`netmind_config.py`**: NetMind API integration with robust TTS functionality
- **`printer.py`**: Rich console progress tracking and status updates

### AI Agent Workflow

1. **Planner Agent** → Analyzes inputs and creates time allocation strategy
2. **Content Agents** → Generate specialized content (Architecture, History, Culture, Culinary)
3. **Orchestrator Agent** → Assembles content with natural transitions and flow
4. **TTS Engine** → Converts final text to high-quality audio with progress tracking

### Technology Stack

- **Framework**: Streamlit for web interface
- **AI Engine**: pydantic-ai with NetMind's gpt-oss-20b model
- **TTS**: NetMind ResembleAI/Chatterbox for speech synthesis
- **Error Handling**: Multi-layer retry mechanisms with exponential backoff
- **UI**: Rich console output with real-time progress indicators

### Key Features

- ✅ **Intelligent Planning**: Dynamic time allocation based on user preferences
- ✅ **Specialized Content**: Domain-expert agents for each topic area
- ✅ **Natural Flow**: Seamless transitions between topics with conversational tone
- ✅ **Robust Audio**: Advanced TTS with retry logic and progress tracking
- ✅ **Error Recovery**: Graceful fallbacks and user-friendly error messages
- ✅ **Responsive UI**: Clean interface with real-time status updates

---

## 📋 Requirements

- Python 3.8+
- NetMind API key (free tier available)
- Internet connection for content generation and TTS

## 🤝 Contributing

Contributions are welcome! Please feel free to submit issues, feature requests, or pull requests.

## 📄 License

This project is open source. Please check the license file for details.

