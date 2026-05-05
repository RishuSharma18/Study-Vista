import pandas as pd


def calculate_burnout(df):
    """
    Calculate a burnout risk score on a 0–10 scale.

    Factors considered:
    - Average daily study hours (overwork indicator)
    - Focus level decline trend (mental fatigue)
    - Study session frequency (no-rest patterns)
    - Focus variability (inconsistency = stress)

    Returns a float between 0.0 and 10.0.
    """
    if df.empty:
        return 0.0

    df = df.copy().sort_values("date")
    score = 0.0

    # Factor 1: Average study hours (0–3 points)
    avg_hours = df["study_hours"].mean()
    if avg_hours > 8:
        score += 3.0
    elif avg_hours > 6:
        score += 2.0
    elif avg_hours > 4:
        score += 1.0

    # Factor 2: Focus decline trend (0–3 points)
    if len(df) >= 3:
        df["focus_trend"] = df["focus_level"].diff()
        avg_trend = df["focus_trend"].mean()
        if avg_trend < -0.5:
            score += 3.0
        elif avg_trend < -0.2:
            score += 2.0
        elif avg_trend < 0:
            score += 1.0

    # Factor 3: Session frequency / no rest days (0–2 points)
    if len(df) >= 7:
        unique_dates = df["date"].nunique()
        date_range = (df["date"].max() - df["date"].min()).days + 1
        if date_range > 0:
            study_ratio = unique_dates / date_range
            if study_ratio > 0.9:
                score += 2.0  # Studying almost every day
            elif study_ratio > 0.75:
                score += 1.0

    # Factor 4: Focus variability (0–2 points)
    focus_std = df["focus_level"].std()
    if focus_std > 1.5:
        score += 2.0
    elif focus_std > 1.0:
        score += 1.0

    return min(10.0, max(0.0, round(score, 1)))
