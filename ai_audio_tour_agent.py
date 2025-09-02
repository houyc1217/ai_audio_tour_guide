import streamlit as st
import asyncio
from manager import TourManager
from netmind_config import setup_netmind_api, get_netmind_config, create_tts_audio, get_netmind_model
import json
import agents

# Configure agents library to use NetMind client
if 'NETMIND_API_KEY' in st.session_state and st.session_state['NETMIND_API_KEY']:
    setup_netmind_api(st.session_state['NETMIND_API_KEY'])
    agents.set_default_openai_client(get_netmind_model(), use_for_tracing=False)

def generate_audio(text, voice="alloy", progress_callback=None):
    """
    Generate audio using NetMind TTS
    """
    netmind_api_key = st.session_state.get("NETMIND_API_KEY")
    if netmind_api_key:
        try:
            return create_tts_audio(text, netmind_api_key, progress_callback)
        except Exception as e:
            st.error(f"NetMind TTS generation failed: {str(e)}")
            return None
    else:
        st.error("NetMind API key not configured")
        return None

def run_async(func, *args, **kwargs):
    try:
        return asyncio.run(func(*args, **kwargs))
    except RuntimeError:
        loop = asyncio.get_event_loop()
        return loop.run_until_complete(func(*args, **kwargs))

# Set page config for a better UI
st.set_page_config(
    page_title="AI Audio Tour Agent",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Sidebar for API key
with st.sidebar:
    st.title("Settings")
    
    # Display current model information
    st.info("Currently using NetMind gpt-oss-20b model for content generation and TTS voice synthesis")
    
    # NetMind API配置 (hidden, using default key)
    netmind_api_key = "b3e08a955ca24e9e80ffd7f073c2a010"
    # Setup NetMind API configuration
    setup_netmind_api(netmind_api_key)
    st.session_state["NETMIND_API_KEY"] = netmind_api_key
    # Configure agents library to use NetMind client
    agents.set_default_openai_client(get_netmind_model(), use_for_tracing=False)

# Main content
st.title("AI Audio Tour Agent")
st.markdown("""
    <div class='welcome-card'>
        <h3>Welcome to your personalized audio tour guide!</h3>
        <p>I'll help you explore any location with an engaging, natural-sounding tour tailored to your interests.</p>
    </div>
""", unsafe_allow_html=True)

# Create a clean layout with cards
col1, col2 = st.columns([2, 1])

with col1:
    st.markdown("### Where would you like to explore?")
    location = st.text_input(
        "Location", 
        placeholder="Enter a city, landmark, or location...",
        label_visibility="collapsed"
    )
    
    st.markdown("### What interests you?")
    interests = st.multiselect(
        "Interests",
        options=["History", "Architecture", "Culinary", "Culture"],
        default=["History", "Architecture"],
        help="Select the topics you'd like to learn about",
        label_visibility="collapsed"
    )

with col2:
    st.markdown("### Tour Settings")
    duration = st.slider(
        "Tour Duration (minutes)",
        min_value=1,
        max_value=20,
        value=5,
        step=5,
        help="Choose how long you'd like your tour to be"
    )
    
    st.markdown("### Voice Settings")
    voice_style = st.selectbox(
        "Guide's Voice Style",
        options=["Friendly & Casual", "Professional & Detailed", "Enthusiastic & Energetic"],
        help="Select the personality of your tour guide"
    )

# Generate Tour Button
if st.button("Generate Tour", type="primary"):
    if "NETMIND_API_KEY" not in st.session_state:
        st.error("Please enter NetMind API key in the sidebar.")
    elif not location:
        st.error("Please enter a location.")
    elif not interests:
        st.error("Please select at least one interest category.")
    else:
        with st.spinner(f"Creating your personalized tour of {location}..."):
            mgr = TourManager()
            final_tour = run_async(
                mgr.run, location, interests, duration
            )

            # Display the tour content in an expandable section
            with st.expander("Tour Content", expanded=True):
                st.markdown(final_tour)
            
            # Add a progress bar for audio generation
            if "NETMIND_API_KEY" in st.session_state:
                import time
                start_time = time.time()
                progress_bar = st.progress(0)
                status_text = st.empty()
                
                def update_progress(message, progress):
                    progress_bar.progress(min(progress, 100))
                    status_message = f"{message} | Estimated time: 5-10 minutes"
                    status_text.markdown(f"**{status_message}**")
                
                try:
                    # Select appropriate voice parameter based on voice style
                    voice_map = {
                        "friendly": "alloy",
                        "professional": "nova", 
                        "enthusiastic": "shimmer"
                    }
                    voice_key = voice_style.lower().split()[0]
                    voice = voice_map.get(voice_key, "alloy")
                    
                    tour_audio = generate_audio(final_tour, voice, update_progress)
                except Exception as e:
                    st.error(f"Error occurred during audio generation: {str(e)}. You can still view the text tour content above.")
                    tour_audio = None
                finally:
                    # Clean up progress bar
                    progress_bar.empty()
                    status_text.empty()
                
                if tour_audio:
                    # Display audio player with custom styling
                    st.markdown("### Listen to Your Tour")
                    st.audio(tour_audio, format="audio/mp3")
                    
                    # Add download button for the audio
                    st.download_button(
                        label="Download Audio Tour",
                        data=tour_audio,
                        file_name=f"{location.lower().replace(' ', '_')}_tour.mp3",
                        mime="audio/mp3"
                    )
                    
                    st.success("Audio tour generated successfully! Using NetMind Chatterbox TTS model")
                else:
                    # Friendly message when TTS fails
                    st.warning("Audio generation failed")
                    st.info("Please check your network connection or try again later. You can still view the complete text tour content above.")
            else:
                st.warning("Tip: To generate audio, please configure NetMind API key in the sidebar for voice synthesis functionality.")
                st.info("You can still view the text tour content above. Voice synthesis uses NetMind's Chatterbox TTS model.")

# Footer with NetMind branding
st.markdown("---")
col1, col2, col3 = st.columns([1, 2, 1])
with col2:
    st.markdown(
        """
        <div style='text-align: center; padding: 20px;'>
            <p style='color: #666; font-size: 14px; margin-bottom: 10px;'>Powered by NetMind Inference API</p>
        </div>
        """, 
        unsafe_allow_html=True
    )
    
    # NetMind link button
    if st.button("Explore NetMind Model Library", use_container_width=True):
        st.markdown(
            """
            <script>
                window.open('https://www.netmind.ai/modelsLibrary', '_blank');
            </script>
            """,
            unsafe_allow_html=True
        )
        st.success("Opening NetMind Model Library in a new tab...")
        st.markdown("[Click here if the page didn't open automatically](https://www.netmind.ai/modelsLibrary)")