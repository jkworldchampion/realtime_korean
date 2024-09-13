import tempfile
import streamlit as st
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.llms import Ollama
from langchain.document_loaders import PyPDFLoader
import streamlit.components.v1 as components


# Ollama 언어 모델 서버의 기본 URL
CUSTOM_URL = "http://localhost:11434"


# 요약을 위한 Ollama 언어 모델 초기화
llm = Ollama(
    model="llama3.1:8b", 
    base_url=CUSTOM_URL, 
    temperature=0,
    num_predict=200
)

# Streamlit 앱의 제목 구성
st.title(" 🦜앵무 Say 🦜")

def main():
    """
    Streamlit 앱을 실행하는 메인 함수.
    """
    if 'translation_result' not in st.session_state:
        st.session_state.translation_result = ""

    # 여기서부터 내가 빌드한다.
    col1, col2 = st.columns(2)
    col1.write("인식")
    user_input = st.text_input("사용자 음성 입력:")

    col2.write("번역")

    html_code = """
        <!DOCTYPE html>
            <html lang="en">
            <head>
                <meta charset="UTF-8">
                <meta name="viewport" content="width=device-width, initial-scale=1.0">
                <title>음성 인식</title>
            </head>
            <body>
                <button id="start-btn">음성 인식 시작</button>
                <button id="stop-btn">음성 인식 중지</button>
                <p id="transcript">음성 인식 결과가 여기에 표시됩니다.</p>

                <script>
                    const startBtn = document.getElementById('start-btn');
                    const stopBtn = document.getElementById('stop-btn');
                    const transcriptElement = document.getElementById('transcript');
                    
                    let recognition;

                    if (!('webkitSpeechRecognition' in window)) {
                        transcriptElement.innerText = "Web Speech API is not supported in this browser.";
                    } else {
                        recognition = new (window.SpeechRecognition || window.webkitSpeechRecognition)();
                        recognition.lang = 'en-us';  // 언어 설정
                        recognition.interimResults = false;
                        recognition.continuous = true;

                        recognition.onresult = function(event) {
                            let transcript = '';
                            for (let i = event.resultIndex; i < event.results.length; i++) {
                                transcript += event.results[i][0].transcript;
                            }
                            transcriptElement.innerText = transcript;

                            // Streamlit으로 결과 전송
                            fetch('/update_transcript', {
                                method: 'POST',
                                headers: {
                                    'Content-Type': 'application/json',
                                },
                                body: JSON.stringify({ text: transcript }),
                            });
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
                </script>
            </body>
        </html>
    """
    components.html(html_code, height=400)
    # 결과 출력
    if 'transcript' in st.session_state:
        st.write(f"음성 인식 결과: {st.session_state.transcript}")


if __name__ == "__main__":
    main()