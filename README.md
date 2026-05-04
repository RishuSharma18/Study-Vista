# 📚 StudyVista

**StudyVista** is a comprehensive, data-driven study tracking and analytics platform built with Streamlit. It helps students and learners log their study sessions, analyze their performance, monitor burnout levels, and get actionable AI-driven insights to improve their study habits.

## ✨ Key Features

- **User Authentication**: Secure login and registration system using `bcrypt`.
- **Session Tracking**: Log study hours, subjects, focus levels, and personal notes.
- **Interactive Dashboard**: A beautiful glass-morphic UI with dynamic quick stats and visually appealing Plotly charts.
- **Advanced Analytics**: Dive deep into your study patterns (e.g., weekly trends, subject distribution, focus vs. hours).
- **Gamification**: Unlock achievements and badges as you hit study milestones.
- **Burnout Monitor**: Proprietary algorithm to calculate your burnout risk based on your recent study volume and focus levels.
- **AI Insights (Clustering)**: Uses K-Means clustering (`scikit-learn`) to categorize your subjects into distinct patterns (e.g., "High Focus, Low Hours" vs. "High Volume").
- **Weekly Reports**: Generate and download comprehensive PDF reports of your study performance using `fpdf`.

## 🛠️ Tech Stack

- **Frontend & App Framework**: [Streamlit](https://streamlit.io/)
- **Database & ORM**: SQLite, [SQLAlchemy](https://www.sqlalchemy.org/)
- **Data Manipulation**: [Pandas](https://pandas.pydata.org/), [NumPy](https://numpy.org/)
- **Data Visualization**: [Plotly](https://plotly.com/python/), Matplotlib, Seaborn
- **Machine Learning**: [Scikit-Learn](https://scikit-learn.org/) (K-Means Clustering)
- **PDF Generation**: [FPDF](https://pyfpdf.readthedocs.io/en/latest/)

## 📂 Project Structure

```text
Study-Vista/
├── app.py                 # Main Streamlit application entry point
├── requirements.txt       # Project dependencies
├── .gitignore             # Git ignore file
├── auth/                  # Authentication modules (login, register)
├── data/                  # Directory for storing raw/processed data
├── db/                    # Database models and session configurations
├── ml/                    # Machine learning algorithms (clustering)
├── services/              # Core business logic (analytics, burnout, pdf export)
└── utils/                 # Helper functions and utilities
```

## 🚀 Installation & Setup

1. **Clone the repository:**
   ```bash
   git clone https://github.com/yourusername/Study-Vista.git
   cd Study-Vista
   ```

2. **Create a virtual environment (Recommended):**
   ```bash
   python -m venv venv
   # On Windows:
   venv\Scripts\activate
   # On Mac/Linux:
   source venv/bin/activate
   ```

3. **Install the dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

4. **Run the application:**
   ```bash
   streamlit run app.py
   ```

## 💻 Usage

1. Open the app in your browser (usually `http://localhost:8501`).
2. Create a new account or log in.
3. Head over to the **"➕ Add Log"** tab to record your first study session.
4. Explore the **Overview**, **Analytics**, **AI Insights**, and **Burnout Monitor** tabs to analyze your data!

## 🤝 Contributing
Contributions, issues, and feature requests are welcome! Feel free to check the issues page.

---
*Built with ❤️ to make studying smarter, not just harder.*
