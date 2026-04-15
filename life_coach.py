import dotenv
dotenv.load_dotenv()

import streamlit as st
from openai import OpenAI
from agents import Agent, Runner, WebSearchTool, FileSearchTool

VECTOR_STORE_ID = "vs_69df2cc09f188191a61a740b3ab86793"

openai_client = OpenAI()

agent = Agent(
    name="Life Coach",
    model="gpt-4o-mini",
    instructions="""당신은 따뜻하고 격려하는 라이프 코치입니다.
사용자의 목표 달성과 자기 개발을 돕는 것이 당신의 사명입니다.
- 항상 긍정적이고 공감하는 태도로 대화하세요
- 파일 검색으로 사용자의 개인 목표와 기록을 참조하세요
- 웹 검색을 활용해 최신 연구 기반의 실용적인 조언을 제공하세요
- 구체적이고 실천 가능한 단계를 제시하세요
- 사용자를 격려하고 동기를 부여하세요
- 한국어로 답변하세요""",
    tools=[
        WebSearchTool(),
        FileSearchTool(vector_store_ids=[VECTOR_STORE_ID], max_num_results=3),
    ],
)

st.title("🌟 Life Coach Agent")
st.caption("당신의 성장을 응원하는 AI 라이프 코치입니다")

if "messages" not in st.session_state:
    st.session_state.messages = []
if "history" not in st.session_state:
    st.session_state.history = []

for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

if prompt := st.chat_input("고민이나 목표를 말씀해 주세요...", accept_file=True, file_type=["txt", "pdf"]):
    for file in prompt.files:
        uploaded = openai_client.files.create(
            file=(file.name, file.read()),
            purpose="assistants",
        )
        openai_client.vector_stores.files.create(
            vector_store_id=VECTOR_STORE_ID,
            file_id=uploaded.id,
        )
        with st.spinner("🔍 검색하고 분석 중..."):
            st.success(f"📄 {file.name} 업로드 완료! 코치가 이 파일을 참조할 수 있습니다.")

    if prompt.text:
        st.session_state.messages.append({"role": "user", "content": prompt.text})
        with st.chat_message("user"):
            st.markdown(prompt.text)

        with st.chat_message("assistant"):
            with st.spinner("🔍 검색하고 분석 중..."):
                input_list = st.session_state.history + [{"role": "user", "content": prompt.text}]
                result = Runner.run_sync(agent, input_list)
                response = result.final_output
            st.markdown(response)

        st.session_state.history = result.to_input_list()
        st.session_state.messages.append({"role": "assistant", "content": response})
