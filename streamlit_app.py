import streamlit as st
import pandas as pd
import instaloader
import time
from io import BytesIO

st.title("📸 인스타그램 팔로워 수 수집기")

# 로그인 입력 받기
st.subheader("🔐 인스타그램 로그인")
username = st.text_input("아이디", placeholder="예: insta_helper_bot")
password = st.text_input("비밀번호", type="password")

logged_in = False
L = instaloader.Instaloader()

if st.button("로그인"):
    try:
        L.login(username, password)
        st.success("로그인 성공! 이제 엑셀 파일을 업로드하세요.")
        logged_in = True
    except Exception as e:
        st.error(f"로그인 실패: {e}")

# 로그인에 성공했을 때만 크롤링 기능 활성화
if logged_in:
    st.subheader("📁 엑셀 업로드")
    uploaded_file = st.file_uploader("엑셀 파일을 업로드하세요 (.xlsx)", type=["xlsx"])

    if uploaded_file:
        try:
            df = pd.read_excel(uploaded_file, header=None)
            if df.empty:
                st.error("엑셀 파일이 비어 있습니다.")
            else:
                urls = df.iloc[:, 0].dropna().tolist()
                if not urls:
                    st.error("엑셀 파일의 A열에 인스타그램 URL을 넣어주세요.")
                else:
                    followers = []
                    with st.spinner("팔로워 수 가져오는 중..."):
                        for url in urls:
                            try:
                                username = str(url).strip().strip('/').split('/')[-1]
                                profile = instaloader.Profile.from_username(L.context, username)
                                followers.append(profile.followers)
                                time.sleep(1.5)  # 요청 사이 딜레이
                            except Exception as e:
                                followers.append(f"에러: {e}")

                    df = pd.DataFrame({
                        "인스타그램 URL": urls,
                        "팔로워 수": followers
                    })

                    output = BytesIO()
                    with pd.ExcelWriter(output, engine='openpyxl') as writer:
                        df.to_excel(writer, index=False)

                    st.success("✅ 완료! 아래 버튼으로 결과 파일을 다운로드하세요.")
                    st.download_button(
                        label="📥 결과 파일 다운로드",
                        data=output.getvalue(),
                        file_name="instagram_result.xlsx",
                        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                    )
        except Exception as e:
            st.error(f"파일 처리 중 오류가 발생했습니다: {e}")
