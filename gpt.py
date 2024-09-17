import tempfile
import streamlit as st
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.llms import Ollama
from langchain.document_loaders import PyPDFLoader

# 추가하는 library
import streamlit.components.v1 as components
import streamlit as st
from flask import Flask, request, jsonify
from flask_cors import CORS  # For handling CORS issues
from threading import Thread
import streamlit.components.v1 as components
from langchain_community.llms import Ollama


# Ollama 언어 모델 서버의 기본 URL
CUSTOM_URL = "http://localhost:11434"


# 요약을 위한 Ollama 언어 모델 초기화
llm = Ollama(
    model="llama3.1:8b", 
    base_url=CUSTOM_URL, 
    temperature=0,
    num_predict=200
)

# 번역을 위한 함수
def translate_text(text):
    map_prompt_template = """
    - you are a professional translator
    - translate the provided content into Korean
    - only respond with the translation
    {text}
    """
    prompt_text = map_prompt_template.format(text=text)
    stream_generator = llm.stream(prompt_text)
    
    translation_result = ""
    for chunk in stream_generator:
        translation_result += chunk
    return translation_result

# Streamlit 앱의 제목 구성
st.title(" 🦜앵무 Say🦜")

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
                <p id="transcript">음성 인식 결과가 여기에 표시됩니다: <br></p>
                <p id="translated">번역 결과가 여기에 표시됩니다: <br></p>

                <script>
                    const startBtn = document.getElementById('start-btn');
                    const stopBtn = document.getElementById('stop-btn');
                    const transcriptElement = document.getElementById('transcript');
                    const translatedElement = document.getElementById('translated');
                    
                    // 음성 -> 텍스트
                    let recognition;  // 
                    let translation = '';  // 번역된 결과를 저장할 변수
                    let lastTranscript = '';  // 마지막으로 처리된 transcript를 저장

                    if (!('webkitSpeechRecognition' in window)) {  // 웹사이트가 말하기 인식이 되는지 확인
                        transcriptElement.innerText = "이 browse에서는 Web Speech API가 작동하지 않습니다...";  // 안되면 error 내뱉기
                    } else {
                        recognition = new (window.SpeechRecognition || window.webkitSpeechRecognition)();
                        recognition.lang = 'en-us';  // 언어 설정
                        recognition.interimResults = false;  // 중간에 끊을 것인지, 이어서 받을 것인지
                        recognition.continuous = true;

                        // 음성인식 결과가 출력되는 부분
                        recognition.onresult = function(event) {
                            let currentTranscript = transcriptElement.innerText;  // 기존 텍스트를 가져옴
                            let newTranscript = '';  // 새로 인식된 텍스트를 저장할 변수

                            for (let i = event.resultIndex; i < event.results.length; i++) {
                                newTranscript += event.results[i][0].transcript;
                            }

                            // 기존 텍스트에 새로 인식된 내용을 추가하여 화면에 표시!!!!! 여기서 출력함.
                            transcriptElement.innerText = currentTranscript + newTranscript;

                            // 서버로 누적된 결과를 전송
                            fetch('/update_transcript', {
                                method: 'POST',
                                headers: {
                                    'Content-Type': 'application/json',
                                },
                                body: JSON.stringify({ text: transcriptElement.innerText }),  // 누적된 텍스트 전체를 서버에 보냄
                            })
                            .then(response => response.json())  // 서버에서 응답이 JSON 형태로 올 때
                            .then(data => {
                                // 서버에서 처리한 결과를 받아서 화면에 표시 (옵션 사항)
                                // transcriptElement.innerText = data.processedText;
                            });

                            // 새로 추가된 텍스트만 번역 (기존과 비교하여 새로운 부분만 추출)
                            let newAddedText = transcriptElement.innerText.replace(lastTranscript, '');
                            if (newAddedText.trim() !== '') {
                                // 5초마다 새로운 텍스트 번역
                                setTimeout(() => {
                                    fetch('/translate_text', {   // 이렇게 말고
                                        method: 'POST',
                                        headers: {
                                            'Content-Type': 'application/json',
                                        },
                                        body: JSON.stringify({ text: newAddedText }),
                                    })
                                    .then(response => response.json())  // 서버에서 번역된 결과 받기
                                    .then(data => {
                                        // 번역된 결과를 <p id="translated">에 추가
                                        translationElement.innerHTML += data.translatedText + '<br>';
                                    });
                                }, 5000);
                            }
                            lastTranscript = transcriptElement.innerText;
                        };
                        /// 여기까지가 지금 고민하면서 어떻게 llama에게 보낼지 부분.. 아마 다른 code조금 더 보면 될 듯.

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

    # 사용자로부터 영어 텍스트 입력 받기
    input_text = st.text_area("번역할 영어 텍스트를 입력하세요:")
    
    if st.button("번역하기"):
        if input_text:
            # 입력 텍스트를 한글로 번역
            translated_text = translate_text(input_text)
            
            # 번역된 텍스트 표시
            st.write(f"번역된 텍스트: {translated_text}")
        else:
            st.write("텍스트를 입력해주세요.")
    # 서버에서 번역된 결과를 받을 POST 엔드포인트 구현

if __name__ == "__main__":
    main()