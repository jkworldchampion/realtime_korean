import tempfile
import streamlit as st
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.llms import Ollama
from langchain.document_loaders import PyPDFLoader


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
st.title(" 🦜내가 너를 영어로부터 구원하리")

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


if __name__ == "__main__":
    main()