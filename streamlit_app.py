import streamlit as st
import pandas as pd
import instaloader
import time
from io import BytesIO
from datetime import datetime

st.set_page_config(page_title="인스타 팔로워 수 수집기", page_icon="📸")
st.title("📸 인스타그램 팔로워 수 수집기 (공개 계정용)")

st.markdown("""
**사용법**
1. A열에 인스타그램 프로필 URL이 들어있는 엑셀 파일을 업로드하세요.
2. 로그인 없이 공개 계정의 팔로워 수를 수집합니다.
3. 결과 엑셀 파일은 수집 시각을 포함한 이름으로 다운로드됩니다.
""")

uploaded_file = st.file_uploader("📁 엑셀 파일 업로드 (.xlsx)", type=["xlsx"])

if uploaded_file:
    try:
        df = pd.read_excel(uploaded_file, header=None)
        if df.empty:
            st.error("엑셀 파일이 비어 있습니다.")
        else:
            urls = df.iloc[:, 0].dropna().tolist()
            if not urls:
                st.error("엑셀 파일의 A열에 인스타그램 URL이 필요합니다.")
            else:
                L = instaloader.Instaloader()
                followers = []

                with st.spinner("팔로워 수 수집 중..."):
                    for url in urls:
                        try:
                            username = str(url).strip().strip('/').split('/')[-1]
                            profile = instaloader.Profile.from_username(L.context, username)
                            followers.append(profile.followers)
                            time.sleep(1.5)  # 요청 제한 완화를 위한 딜레이
                        except Exception as e:
                            followers.append(f"에러: {e}")

                result_df = pd.DataFrame({
                    "인스타그램 URL": urls,
                    "팔로워 수": followers
                })

                # 파일명에 현재 시간 추가
                now = datetime.now().strftime("%y.%m.%d_%H:%M")
                filename = f"instagram_result_{now}.xlsx"

                output = BytesIO()
                with pd.ExcelWriter(output, engine='openpyxl') as writer:
                    result_df.to_excel(writer, index=False)

                st.success("✅ 수집 완료! 아래 버튼으로 결과 파일을 다운로드하세요.")
                st.download_button(
                    label="📥 결과 다운로드 (.xlsx)",
                    data=output.getvalue(),
                    file_name=filename,
                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                )
    except Exception as e:
        st.error(f"처리 중 오류 발생: {e}")
