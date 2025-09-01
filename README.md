# 🎧 Self-Guided AI Audio Tour Agent

A conversational voice agent system that generates immersive, self-guided audio tours based on the user's **location**, **areas of interest**, and **tour duration**. Built on a multi-agent architecture using NetMind API, real-time information retrieval, and expressive TTS for natural speech output.

---

## 🚀 Features

### 🎙️ Multi-Agent Architecture

- **Orchestrator Agent**  
  Coordinates the overall tour flow, manages transitions, and assembles content from all expert agents.

- **History Agent**  
  Delivers insightful historical narratives with an authoritative voice.

- **Architecture Agent**  
  Highlights architectural details, styles, and design elements using a descriptive and technical tone.

- **Culture Agent**  
  Explores local customs, traditions, and artistic heritage with an enthusiastic voice.

- **Culinary Agent**  
  Describes iconic dishes and food culture in a passionate and engaging tone.

---

### 📍 Location-Aware Content Generation

- Dynamic content generation based on user-input **location**
- Real-time **web search integration** to fetch relevant, up-to-date details
- Personalized content delivery filtered by user **interest categories**

---

### ⏱️ Customizable Tour Duration

- Selectable tour length: **15, 30, or 60 minutes**
- Time allocations adapt to user interest weights and location relevance
- Ensures well-paced and proportioned narratives across sections

---

### 🔊 Expressive Speech Output

- High-quality audio generated using **NetMind TTS API (ResembleAI/Chatterbox)**
- Robust retry mechanism with optimized network configuration
- Progress tracking with estimated completion time (5-10 minutes)
- Multiple voice styles: friendly, professional, enthusiastic

### How to get Started?

1. Install the required dependencies:

```bash
pip install -r requirements.txt
```

2. Get your NetMind API Key

- Sign up for a [NetMind account](https://api.netmind.ai/) and obtain your API key.
- The application will prompt you to enter your API key in the Streamlit interface.

3. Run the Streamlit App
```bash
streamlit run ai_audio_tour_agent.py
```

4. Using the Application

- Enter your NetMind API key when prompted
- Specify your desired location for the tour
- Select your areas of interest (History, Architecture, Culture, Culinary)
- Choose tour duration (1.5, 3, or 5 minutes)
- Select voice style (friendly, professional, enthusiastic)
- Generate and listen to your personalized audio tour

---

## 🛠️ Technical Architecture

### Core Components

- **ai_audio_tour_agent.py**: Main Streamlit application with user interface
- **manager.py**: Tour orchestration and multi-agent coordination
- **agent.py**: Individual specialized agents (History, Architecture, Culture, Culinary, Planner, Orchestrator)
- **netmind_config.py**: NetMind API configuration and TTS functionality
- **printer.py**: Rich console output for status updates

### API Integration

- **NetMind Chat API**: Powers all text generation agents
- **NetMind TTS API**: Converts text to high-quality speech
- **Web Search**: Real-time information retrieval for location-specific content

### Features

- ✅ Multi-agent architecture for specialized content generation
- ✅ Real-time web search integration
- ✅ Customizable tour duration and interests
- ✅ Multiple voice styles
- ✅ Progress tracking with time estimation
- ✅ Robust error handling and retry mechanisms
- ✅ Clean, icon-free user interface

