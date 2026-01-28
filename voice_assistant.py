#miss& mr.siri.Voice Assistant

# Voice assistant using streamlit and groq 

import streamlit as st 

st.set_page_config(
    page_title = "Miss_Mr_Siri",
    layout = 'wide'
)

# Libraries 
import os 
import time
import pyttsx3 #text to speech
import speech_recognition as sr # convert speech to text
from groq import Groq # Groq is API to connect with LLM
from dotenv import load_dotenv

# load the GROQ API Key
load_dotenv()
GROQ_API_KEY = os.getenv("GROQ_API_KEY")

if not GROQ_API_KEY:
    st.error("Missing key, please rune the $env command")
    st.stop()
    
#Connecting with LLM using API Key 
client = Groq(api_key = GROQ_API_KEY)
MODEL = 'llama-3.3-70b-versatile'

# intializing speech recognizer
@st.cache_resource 
def get_recognizer():
    return sr.Recognizer()
recog = get_recognizer()


# funtion to convert text to speech (intializing)
def get_tts_engine():
    try:
        engine = pyttsx3.init()
        return engine
    except Exception  as e:
        st.error(f"Failed to n=initalize TTS engine:{e}")
        return None 
    

# funtion to speak to text 
def speak(text, voice_gender = 'siri'):
    try: 
        engine = get_tts_engine()
        if engine is None:
            return 
        voices = engine.getProperty('voices')
        if voices: 
            if voice_gender == 'boy':
                for voice in voices:
                    if "male" in voice.name.lower():
                      engine.setProperty('voice',voice.id)
                      break 
            else:
                for voice in voices:
                    if 'female' in voice.name.lower() or 'zira' in voice.name.lower():
                        engine.setProperty('voice', voice.id)
                        break
        engine.setProperty('rate', 200) #speed of speech
        engine.setProperty('volumn',0.8) # volumn level
        engine.say(text)
        engine.runAndWait()
        engine.stop()
    except Exception as e :
        st.error(f"TTS related Error")
        
        
# funtion for speech to text 
def listen():
    try:
        with sr.Microphone() as source:
            recog.adjust_for_ambient_noise(source, duration = 1)
            audio = recog.listen(source, phrase_time_limit=10)
            
        text = recog.recognize_google(audio) #using Google API function to covert speech to text 
        return text.lower()
    except sr.UnknownValueError:
        return "Sorry, i don't get you , Please repeat again "
    except sr.RequestError:
        return "Speech services not available"
    except Exception as e:
        return f"Error:{e}"
    
    
# Funtion to get AI response from Groq LLM

def ai_response(messages):
    try:
        completion = client.chat.completions.create(
            model=MODEL,
            messages=messages,
            temperature=0.7,
            max_tokens=150
        )

        if completion and completion.choices:
            reply = completion.choices[0].message.content
            return reply.strip()

        return "Sorry, I couldn't generate a response."

    except Exception as e:
        return f"LLM Error: {e}"

    
    
# Driver code (main())
def main():
    st.title("Voice Assistant")
    st.markdown("---")

    # Intialize the session state
    if "chat_history" not in st.session_state:
        st.session_state.chat_history = [
            {"role" : "system", 
             "content" : "You are a helpful voice assistant. Reply just one line."
             }
        ]

    # Intitalize the message you want to pass
    if "messages" not in st.session_state:
        st.session_state.messages = []

    # Side front end
    with st.sidebar:
        st.header("Controls")

        # If disable then no voice just text reply from voice assistant
        tts_enabled = st.checkbox("Enable Text to Speech", value = True)

        # selecting Gender
        voice_gender = st.selectbox(
            "Voice Gender",
            options = ["girl", "boy"],
            index = 0,
            help = "Choose type of voice for your assistant"
        )

        # voice input button
        if st.button("Start Voice input", type = "primary", use_container_width = True):
            with st.spinner("Listening..."):
                user_input = listen()

                if user_input and user_input not in ["Sorry, i don't get you, Please repeat again", "Speech service not available"]:
                    st.session_state.messages.append({"role" : "user", "content" :  user_input})
                    st.session_state.chat_history.append({"role": "user", "content" :user_input})

                    # get AI reply
                    with st.spinner("Thinking..."):
                        response = ai_response(st.session_state.chat_history)
                        st.session_state.messages.append({"role" : "assistant", "content" : response })
                        st.session_state.chat_history.append({"role" : "assistant", "content" : response })

                    # speak the reply
                    if tts_enabled:
                        speak(response, voice_gender )

                    # refresh UI to display response
                    st.rerun()
        
        st.markdown("---")
        #  Giving instructions by Text
        st.subheader("Text Input")
        user_input = st.text_input("Type your message:", key = "text_input")
        if user_input and user_input not in ["Sorry, i don't get you, Please repeat again", "Speech service not available"]:
                    st.session_state.messages.append({"role" : "user", "content" :  user_input})
                    st.session_state.chat_history.append({"role": "user", "content" :user_input})

                    # get AI reply
                    with st.spinner("Thinking..."):
                        response = ai_response(st.session_state.chat_history)
                        st.session_state.messages.append({"role" : "assistant", "content" : response })
                        st.session_state.chat_history.append({"role" : "assistant", "content" : response })

                    # speak the reply
                    if tts_enabled:
                        speak(response, voice_gender )

                    # refresh UI to display response
                    st.rerun()
            
        st.markdown("---")

        # button to clear the conversation
        if st.button("Clear Chat", use_container_width=True):
            st.session_state.messages = []
            st.session_state.chat_history = [
            {"role" : "system", 
             "content" : "You are a helpful voice assistant. Reply just one line. "
             }
            ]
            st.rerun()
    
    # add the chat conversation to right side
    st.subheader("Conversation")
    for message in st.session_state.messages:
        if message["role"] == "user":
            with st.chat_message("user"):
                st.write(message["content"])
        else:
            with st.chat_message("assistant"):
                st.write(message["content"])

    # Putting welocome in the start
    if not st.session_state.messages:
        st.info("Welcome: Use voice inout button or Type message to start chatting")

    st.markdown("---")
    st.markdown(
        """
        <div style = 'text-align: center; color: #666;'>
        <p> Voice Assistant Project * Copy right to vikram </p>
        </div>
        """,
        unsafe_allow_html= True
    )
if __name__ == "__main__":
    main()