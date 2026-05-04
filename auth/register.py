import streamlit as st
from db.session import SessionLocal
from db.models import User
from utils.hashing import hash_password


def register_user():
    st.markdown("### 📝 Create New Account")
    username = st.text_input("👤 Username", key="reg_user")
    password = st.text_input("🔒 Password", type="password", key="reg_pass")
    confirm_password = st.text_input("🔒 Confirm Password", type="password", key="reg_confirm")

    if st.button("Sign Up", use_container_width=True):
        # Validation
        if not username.strip() or not password.strip():
            st.warning("Please enter both username and password.")
            return

        if len(username.strip()) < 3:
            st.warning("Username must be at least 3 characters.")
            return

        if len(password) < 6:
            st.warning("Password must be at least 6 characters.")
            return

        if password != confirm_password:
            st.error("Passwords do not match!")
            return

        session = SessionLocal()
        try:
            if session.query(User).filter_by(username=username.strip()).first():
                st.error("Username already exists ❌")
            else:
                hashed = hash_password(password)
                user = User(username=username.strip(), password_hash=hashed)
                session.add(user)
                session.commit()
                st.success("🎉 Registered successfully! Please switch to Login.")
        finally:
            session.close()
