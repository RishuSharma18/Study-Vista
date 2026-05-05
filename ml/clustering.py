import warnings
from sklearn.cluster import KMeans
import pandas as pd


# Cluster label mapping based on centroid characteristics
CLUSTER_LABELS = {
    "high_hours_high_focus": "🌟 High Performer",
    "high_hours_low_focus": "⚠️ Overworked",
    "low_hours_high_focus": "✅ Efficient Learner",
    "low_hours_low_focus": "🔴 Needs Attention",
    "medium": "📊 Balanced",
}


def _label_cluster(row, hours_median, focus_median):
    """Assign a human-readable label based on study hours and focus level."""
    high_hours = row["study_hours"] > hours_median
    high_focus = row["focus_level"] > focus_median

    if high_hours and high_focus:
        return CLUSTER_LABELS["high_hours_high_focus"]
    elif high_hours and not high_focus:
        return CLUSTER_LABELS["high_hours_low_focus"]
    elif not high_hours and high_focus:
        return CLUSTER_LABELS["low_hours_high_focus"]
    else:
        return CLUSTER_LABELS["low_hours_low_focus"]


def cluster_subjects(df):
    """
    Cluster subjects by average study hours and focus level using K-Means.
    Returns a DataFrame with cluster IDs and human-readable labels.
    """
    if df.empty:
        return pd.DataFrame()

    df_grouped = df.groupby("subject")[["study_hours", "focus_level"]].mean().round(2)

    n_samples = len(df_grouped)
    n_clusters = min(3, n_samples)

    if n_clusters < 1:
        return df_grouped.reset_index()

    # Suppress convergence warnings for very small datasets
    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        kmeans = KMeans(n_clusters=n_clusters, random_state=42, n_init=10)
        df_grouped["cluster"] = kmeans.fit_predict(df_grouped)

    # readable labels
    hours_median = df_grouped["study_hours"].median()
    focus_median = df_grouped["focus_level"].median()
    df_grouped["category"] = df_grouped.apply(
        lambda row: _label_cluster(row, hours_median, focus_median), axis=1
    )

    return df_grouped.reset_index()
