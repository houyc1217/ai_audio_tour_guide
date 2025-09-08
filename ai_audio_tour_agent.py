import streamlit as st
import asyncio
from manager import TourManager
from netmind_config import setup_netmind_api, get_netmind_config, create_tts_audio, get_netmind_model
import json

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
    """Run async function in Streamlit environment safely"""
    import concurrent.futures
    import threading
    
    def run_in_thread():
        # Create a new event loop in a separate thread
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        try:
            return loop.run_until_complete(func(*args, **kwargs))
        finally:
            loop.close()
    
    # Always use thread executor for Streamlit compatibility
    with concurrent.futures.ThreadPoolExecutor() as executor:
        future = executor.submit(run_in_thread)
        return future.result()

# Set page config for a better UI
st.set_page_config(
    page_title="AI Audio Tour Agent",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Sidebar for API key
with st.sidebar:
    st.title("Settings")
    
    # NetMind API Key input
    st.markdown("### NetMind API Configuration")
    netmind_api_key = st.text_input(
        "NetMind API Key",
        type="password",
        placeholder="Enter your NetMind API key...",
        help="Get your API key from NetMind platform"
    )
    
    if netmind_api_key:
        try:
            # Setup NetMind API configuration
            setup_netmind_api(netmind_api_key)
            st.session_state["NETMIND_API_KEY"] = netmind_api_key
            st.success("✅ NetMind API configured successfully")
            
            # Display current model information
            st.info("Currently using NetMind gpt-oss-20b model for content generation and TTS voice synthesis")
        except Exception as e:
            st.error(f"❌ API configuration failed: {str(e)}")
            st.session_state["NETMIND_API_KEY"] = None
    else:
        st.warning("⚠️ Please enter your NetMind API key to use the service")
        st.session_state["NETMIND_API_KEY"] = None

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
    if not st.session_state.get("NETMIND_API_KEY"):
        st.error("Please enter your NetMind API key in the sidebar first.")
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
            
            # Enhanced audio generation with better UX
            if st.session_state.get("NETMIND_API_KEY"):
                import time
                start_time = time.time()
                
                # Create containers for better layout
                audio_container = st.container()
                progress_container = st.container()
                
                with progress_container:
                    st.markdown("### 🎵 Generating Audio Tour")
                    progress_bar = st.progress(0)
                    status_text = st.empty()
                    time_text = st.empty()
                    
                # Enhanced progress callback with time estimation
                def update_progress(message, progress):
                    elapsed_time = time.time() - start_time
                    progress_val = min(max(progress, 0), 1.0)  # Ensure 0-1 range
                    progress_bar.progress(progress_val)
                    
                    # Dynamic time estimation based on progress
                    if progress_val > 0.1:
                        estimated_total = elapsed_time / progress_val
                        remaining_time = max(0, estimated_total - elapsed_time)
                        time_str = f"⏱️ Estimated remaining: {int(remaining_time//60)}m {int(remaining_time%60)}s"
                    else:
                        time_str = "⏱️ Initializing audio generation..."
                    
                    # Progress stages with emojis
                    stage_emojis = {
                        "TTS attempt": "🔄",
                        "Calling TTS API": "📡",
                        "Downloading audio": "⬇️",
                        "Audio generation completed": "✅"
                    }
                    
                    emoji = "🎵"
                    for stage, stage_emoji in stage_emojis.items():
                        if stage.lower() in message.lower():
                            emoji = stage_emoji
                            break
                    
                    status_text.markdown(f"**{emoji} {message}**")
                    time_text.markdown(f"*{time_str}*")
                
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
                    # Import TTS exceptions for specific error handling
                    from netmind_config import TTSConnectionError, TTSTimeoutError, TTSAPIError, TTSQuotaError, TTSError
                    
                    # Provide user-friendly error messages based on exception type
                    if isinstance(e, TTSConnectionError):
                        st.error("🌐 **Network Connection Issue**")
                        st.info("Unable to connect to the audio generation service. Please check your internet connection and try again.")
                    elif isinstance(e, TTSTimeoutError):
                        st.error("⏱️ **Request Timeout**")
                        st.info("The audio generation is taking longer than expected. This might be due to high server load. Please try again in a few minutes.")
                    elif isinstance(e, TTSQuotaError):
                        st.error("📊 **API Quota Exceeded**")
                        st.info("The daily limit for audio generation has been reached. Please try again tomorrow or contact support for increased limits.")
                    elif isinstance(e, TTSAPIError):
                        st.error("🔧 **Service Temporarily Unavailable**")
                        st.info("The audio generation service is experiencing technical difficulties. Please try again later.")
                    else:
                        st.error("❌ **Audio Generation Failed**")
                        st.info(f"An unexpected error occurred: {str(e)}. Please try again or contact support if the issue persists.")
                    
                    # Always show the fallback message
                    st.success("✅ **Your text tour is ready above!** You can still enjoy the complete written tour content.")
                    tour_audio = None
                finally:
                    # Graceful cleanup with completion message
                    if tour_audio:
                        progress_bar.progress(1.0)
                        status_text.markdown("**✅ Audio generation completed successfully!**")
                        time_text.markdown("*Ready to play*")
                        time.sleep(1)  # Brief pause to show completion
                    
                    # Clean up progress indicators
                    progress_container.empty()
                
                # Display audio results in the audio container
                with audio_container:
                    if tour_audio:
                        # Success state with enhanced UI
                        st.markdown("### 🎧 Your Audio Tour is Ready!")
                        
                        # Audio player with custom styling
                        st.audio(tour_audio, format="audio/mp3")
                        
                        # Enhanced download section
                        col1, col2 = st.columns([2, 1])
                        with col1:
                            st.download_button(
                                label="📥 Download Audio Tour",
                                data=tour_audio,
                                file_name=f"{location.lower().replace(' ', '_')}_tour.mp3",
                                mime="audio/mp3",
                                use_container_width=True
                            )
                        with col2:
                            audio_size_mb = len(tour_audio) / (1024 * 1024)
                            st.metric("File Size", f"{audio_size_mb:.1f} MB")
                        
                        # Success message with model info
                        st.success("🎉 Audio tour generated successfully using NetMind Chatterbox TTS model!")
                        
                        # Usage tips
                        with st.expander("🎵 Audio Tips", expanded=False):
                            st.markdown("""
                            - **Best Experience**: Use headphones for immersive audio
                            - **Playback Speed**: Most browsers allow speed adjustment (0.5x - 2x)
                            - **Download**: Save the audio file for offline listening
                            - **Share**: The downloaded file can be shared with others
                            """)
                    else:
                        # Enhanced failure state (only shown if no specific error was displayed)
                        if 'tour_audio' in locals():
                            st.markdown("### 📝 Text Tour Available")
                            st.info("💡 **Tip**: While audio generation wasn't successful this time, your complete text tour is ready above. You can try generating audio again or enjoy reading the tour content.")
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