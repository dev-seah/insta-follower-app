
import streamlit as st
import pandas as pd
import instaloader
import tempfile
from io import BytesIO

st.title("📸 인스타그램 팔로워 수 수집기")

uploaded_file = st.file_uploader("엑셀 파일을 업로드하세요 (.xlsx)", type=["xlsx"])

if uploaded_file:
    try:
        df = pd.read_excel(uploaded_file)
        if df.empty or 'A' not in df.columns and df.columns[0] != 'Unnamed: 0':
            st.error("엑셀 파일의 A열에 인스타그램 URL을 넣어주세요.")
        else:
            L = instaloader.Instaloader()
            followers = []

            urls = df.iloc[:, 0].dropna().tolist()

            with st.spinner("팔로워 수 가져오는 중..."):
                for url in urls:
                    try:
                        username = str(url).strip().strip('/').split('/')[-1]
                        profile = instaloader.Profile.from_username(L.context, username)
                        followers.append(profile.followers)
                    except Exception as e:
                        followers.append(f"에러: {e}")

            df['팔로워 수'] = followers

            output = BytesIO()
            with pd.ExcelWriter(output, engine='openpyxl') as writer:
                df.to_excel(writer, index=False)
            st.success("완료! 아래 버튼으로 결과 파일을 다운로드하세요.")
            st.download_button(
                label="📥 결과 파일 다운로드",
                data=output.getvalue(),
                file_name="instagram_result.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            )
    except Exception as e:
        st.error(f"파일 처리 중 오류가 발생했습니다: {e}")
