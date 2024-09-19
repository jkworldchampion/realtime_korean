import streamlit as st
from langchain_community.llms import Ollama
import streamlit.components.v1 as components
from flask import Flask, request, jsonify
from flask_cors import CORS
from threading import Thread

# Ollama language model server's base URL
CUSTOM_URL = "http://localhost:11434"

# Initialize the LLM for translation
llm = Ollama(
    model="llama3.1:8b",
    base_url=CUSTOM_URL,
    temperature=0,
    num_predict=200
)

# Translation function using the LLM
def translate_text(text):
    map_prompt_template = """
    - you are a professional translator
    - translate the provided content into English
    - only respond with the translation, Do not use any Korean 
    {text}
    """
    prompt_text = map_prompt_template.format(text=text)
    stream_generator = llm.stream(prompt_text)
    
    translation_result = ""
    for chunk in stream_generator:
        translation_result += chunk
    return translation_result

# Create Flask app
app = Flask(__name__)
CORS(app)  # Enable CORS

# Endpoint to handle translation requests
@app.route('/translate_text', methods=['POST'])
def translate_text_endpoint():
    data = request.get_json()
    text_to_translate = data.get('text', '')
    # Call the translation function
    translated_text = translate_text(text_to_translate)
    return jsonify({'translatedText': translated_text})

def run_flask():
    app.run(port=9020, threaded=True)

def main():
    st.title("🦜앵무 Say🦜")

    # Start the Flask app
    flask_thread = Thread(target=run_flask)
    flask_thread.daemon = True
    flask_thread.start()

    # Your existing Streamlit code
    col1, col2 = st.columns(2)
    col1.write("인식")
    user_input = st.text_input("사용자 음성 입력:")

    col2.write("번역")

    # Embed the HTML and JavaScript
    html_code = """
    <!DOCTYPE html>
    <html lang="en">
        <head>
            <meta charset="UTF-8">
            <title>음성 인식</title>
        </head>
        <style>
            html, body {
                height: 100%;
                margin: 0;
                padding: 0;
                display: flex;
                flex-direction: column;
                align-items: center; /* Center content horizontally */
                justify-content: flex-start; /* Align content at the top */
                background-color: #f4f4f4; /* Background color for aesthetics */
            }
            /* Style for scrollable transcript and translated sections */
            #transcript, #translated {
                max-height: 200px;  /* Set a max height for the elements */
                overflow-y: auto;   /* Enable vertical scrolling when content exceeds the height */
                padding: 10px;
                border: 1px solid #ccc;
                margin: 10px 0;
                width: 80%; /* Set a reasonable width */
            }

            /* Optional: Add some style to buttons */
            button {
                margin: 10px;
                padding: 10px 20px;
                font-size: 16px;
            }
        </style>
        <body>
            <button id="start-btn">음성 인식 시작</button>
            <button id="stop-btn">음성 인식 중지</button>
            <p id="transcript">음성 인식 결과가 여기에 표시됩니다: <br></p>
            <p id="translated">번역 결과가 여기에 표시됩니다: <br></p>
            <script>
                const startBtn = document.getElementById('start-btn');
                const stopBtn = document.getElementById('stop-btn');
                const transcriptElement = document.getElementById('transcript');
                const translatedElement = document.getElementById('translated');

                let recognition;
                let pendingText = '';

                if (!('webkitSpeechRecognition' in window)) {
                    transcriptElement.innerText = "이 브라우저에서는 Web Speech API가 작동하지 않습니다...";
                } else {
                    recognition = new (window.SpeechRecognition || window.webkitSpeechRecognition)();
                    recognition.lang = 'ko-KR';  // 'ko-KR' or 'en-US'
                    recognition.interimResults = false;
                    recognition.continuous = true;

                    recognition.onresult = function(event) {
                        let currentTranscript = transcriptElement.innerText;
                        let newTranscript = '';
                        for (let i = event.resultIndex; i < event.results.length; i++) {
                            newTranscript += event.results[i][0].transcript;
                        }
                        transcriptElement.innerText = currentTranscript + newTranscript;
                        pendingText += newTranscript;
                    };

                    recognition.onerror = function(event) {
                        console.error('Speech recognition error:', event.error);
                    };

                    recognition.onend = function() {
                        console.log('Speech recognition ended');
                    };

                    startBtn.addEventListener('click', function() {
                        if (recognition) {
                            recognition.start();
                        }
                    });

                    stopBtn.addEventListener('click', function() {
                        if (recognition) {
                            recognition.stop();
                        }
                    });
                }

                // Every 5 seconds, translate the pending text
                setInterval(() => {
                    if (pendingText.trim() !== '') {
                        fetch('http://localhost:9020/translate_text', {
                            method: 'POST',
                            headers: {
                                'Content-Type': 'application/json',
                            },
                            body: JSON.stringify({ text: pendingText }),
                        })
                        .then(response => response.json())
                        .then(data => {
                            // Display the translated text
                            translatedElement.innerHTML += data.translatedText + '<br>';
                            // Clear the pending text
                            pendingText = '';
                        })
                        .catch(error => {
                            console.error('Error:', error);
                        });
                    }
                }, 5000);
            </script>

        </body>
    </html>
    """
    components.html(html_code, height=400)

if __name__ == "__main__":
    main()
