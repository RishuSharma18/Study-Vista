import streamlit as st
from db.session import SessionLocal
from db.models import User
from utils.hashing import verify_password


def login_user():
    st.markdown("### 🔑 Login to your Account")
    username = st.text_input("👤 Username", key="login_user")
    password = st.text_input("🔒 Password", type="password", key="login_pass")

    if st.button("Login", use_container_width=True):
        if not username.strip() or not password.strip():
            st.warning("Please enter both username and password.")
            return

        session = SessionLocal()
        try:
            user = session.query(User).filter_by(username=username.strip()).first()
            if user and verify_password(password, user.password_hash):
                st.session_state["logged_in"] = True
                st.session_state["user_id"] = user.id
                st.session_state["username"] = user.username
                st.success(f"🎉 Welcome back, {username}!")
                st.rerun()
            else:
                st.error("❌ Invalid username or password.")
        finally:
            session.close()
