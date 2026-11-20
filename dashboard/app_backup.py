from pathlib import Path
import pandas as pd
import plotly.express as px
import streamlit as st

st.set_page_config(
    page_title="SOFDI Kobo Analytics",
    page_icon="🌱",
    layout="wide",
)

BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data" / "cleaned"
REPORTS_DIR = BASE_DIR / "reports"


def get_latest_file(folder, pattern):
    files = list(folder.glob(pattern))
    if not files:
        return None
    return max(files, key=lambda file: file.stat().st_mtime)


@st.cache_data
def load_csv(file_path):
    return pd.read_csv(file_path, dtype=str).fillna("")


# LOAD DATA
cleaned_file = get_latest_file(
    DATA_DIR, "mhac_agroecology_cleaned_*.csv"
)
indicator_file = get_latest_file(
    DATA_DIR, "mhac_practice_indicators_*.csv"
)
quality_file = REPORTS_DIR / "mhac_data_quality_report.csv"

if cleaned_file is None or indicator_file is None:
    st.error("Required MHAC data files were not found.")
    st.stop()

df = load_csv(str(cleaned_file))
indicators = load_csv(str(indicator_file))
quality = load_csv(str(quality_file)) if quality_file.exists() else pd.DataFrame()

required_columns = [
    "category", "field_name", "choice_code", "practice_or_crop",
    "respondents_selected", "respondents_answered",
    "percentage_of_respondents_answered", "label_status",
]
missing_columns = [c for c in required_columns if c not in indicators.columns]
if missing_columns:
    st.error("Practice indicator file is missing: " + ", ".join(missing_columns))
    st.stop()

for column in [
    "respondents_selected",
    "respondents_answered",
    "percentage_of_respondents_answered",
]:
    indicators[column] = pd.to_numeric(
        indicators[column], errors="coerce"
    ).fillna(0)


# HEADER AND REGION FILTER
st.title("🌱 SOFDI Kobo Analytics Dashboard")
st.subheader("MHAC Agroecology Farmers Follow-up")
st.caption(
    "Monitoring, evaluation, practice adoption and data quality overview"
)

with st.sidebar:
    st.header("Dashboard Filters")
    if "Region" in df.columns:
        regions = sorted(
            df["Region"].replace("", pd.NA).dropna().unique().tolist()
        )
        if regions:
            selected_regions = st.multiselect(
                "Filter by Region", regions, default=regions
            )
            df = df[df["Region"].isin(selected_regions)].copy()
        else:
            st.info("No region values are available. Showing all submissions.")
    else:
        st.warning("Region field is unavailable. Showing all submissions.")

    st.divider()
    st.caption("Cleaned dataset")
    st.write(cleaned_file.name)
    st.caption("Practice indicators")
    st.write(indicator_file.name)

st.caption(f"Showing {len(df):,} submissions after applying the region filter.")


# SHARED METRICS
total_submissions = len(df)
if "Lead_Farmer_Name" in df.columns:
    farmer_count = (
        df["Lead_Farmer_Name"].replace("", pd.NA).dropna().nunique()
    )
else:
    farmer_count = 0

if "Name_of_the_Group" in df.columns:
    group_count = (
        df["Name_of_the_Group"].replace("", pd.NA).dropna().nunique()
    )
else:
    group_count = 0

quality_flag_count = len(quality)
if not quality.empty and "submissions_affected" in quality.columns:
    affected_submissions = pd.to_numeric(
        quality["submissions_affected"], errors="coerce"
    ).fillna(0).sum()
else:
    affected_submissions = 0


# HORIZONTAL NAVIGATION
overview_tab, practice_tab, group_tab, quality_tab = st.tabs(
    ["📊 Overview", "🌱 Practice Adoption", "👥 Group Performance", "🔎 Data Quality"]
)


# TAB 1: OVERVIEW
with overview_tab:
    st.header("Executive Overview")
    metric_columns = st.columns(5)
    metric_columns[0].metric("Total Submissions", f"{total_submissions:,}")
    metric_columns[1].metric("Farmer Names", f"{farmer_count:,}")
    metric_columns[2].metric("Recorded Groups", f"{group_count:,}")
    metric_columns[3].metric("Practice Indicators", f"{len(indicators):,}")
    metric_columns[4].metric("Data Quality Flags", f"{quality_flag_count:,}")

    st.divider()
    left_column, right_column = st.columns([1.5, 1])

    with left_column:
        st.subheader("Monthly Submission Trends")
        date_column = "_submission_time"
        if date_column in df.columns:
            trend_data = df.copy()
            trend_data[date_column] = pd.to_datetime(
                trend_data[date_column], errors="coerce"
            )
            trend_data = trend_data.dropna(subset=[date_column])
            if not trend_data.empty:
                trend_data["Month"] = (
                    trend_data[date_column].dt.to_period("M").astype(str)
                )
                monthly_submissions = (
                    trend_data.groupby("Month")
                    .size()
                    .reset_index(name="Submissions")
                )
                monthly_fig = px.bar(
                    monthly_submissions,
                    x="Month",
                    y="Submissions",
                    text="Submissions",
                    title="Submissions by Month",
                )
                monthly_fig.update_layout(
                    xaxis_title="Month",
                    yaxis_title="Number of submissions",
                    height=390,
                )
                st.plotly_chart(monthly_fig, use_container_width=True)
            else:
                st.info("No valid submission dates were found.")
        else:
            st.info("Submission date field is unavailable.")

    with right_column:
        st.subheader("Farmer and Group Coverage")
        st.metric("Distinct recorded farmer names", farmer_count)
        st.metric("Distinct recorded group names", group_count)
        st.caption(
            "Distinct non-empty names in filtered submissions; not necessarily "
            "verified unique individuals or officially registered groups."
        )
        st.subheader("Data Quality Snapshot")
        st.metric(
            "Submission occurrences requiring review",
            int(affected_submissions),
        )

    with st.expander("View data source details"):
        st.write("Cleaned dataset:", cleaned_file.name)
        st.write("Practice indicators:", indicator_file.name)
        st.write("Quality report:", quality_file.name)


# TAB 2: PRACTICE ADOPTION
with practice_tab:
    st.header("Agroecological Practice Adoption")
    st.caption(
        "Percentages use submissions answering each question as the denominator."
    )
    categories = sorted(indicators["category"].dropna().unique().tolist())

    if not categories:
        st.info("No practice categories are available.")
    else:
        selected_category = st.selectbox(
            "Select practice category",
            ["All Categories"] + categories,
            key="adoption_category",
        )
        if selected_category == "All Categories":
            category_data = indicators.copy()
        else:
            category_data = indicators[
                indicators["category"] == selected_category
            ].copy()

        category_data = category_data[
            category_data["label_status"] == "Label available"
        ].copy()

        if category_data.empty:
            st.info("No labelled practice indicators are available here.")
        else:
            category_data = category_data.sort_values(
                "respondents_selected", ascending=False
            )
            practice_fig = px.bar(
                category_data,
                x="respondents_selected",
                y="practice_or_crop",
                orientation="h",
                text="percentage_of_respondents_answered",
                hover_data={
                    "respondents_answered": True,
                    "respondents_selected": True,
                    "percentage_of_respondents_answered": ":.1f",
                    "practice_or_crop": False,
                },
                title="Reported Practice Adoption",
            )
            practice_fig.update_traces(
                texttemplate="%{text:.1f}%",
                textposition="outside",
            )
            practice_fig.update_layout(
                xaxis_title="Submissions selecting practice",
                yaxis_title="Practice / Crop",
                yaxis=dict(autorange="reversed"),
                height=max(480, len(category_data) * 30),
            )
            st.plotly_chart(practice_fig, use_container_width=True)

            with st.expander("View detailed practice adoption table"):
                practice_table = category_data[
                    [
                        "category",
                        "practice_or_crop",
                        "respondents_selected",
                        "respondents_answered",
                        "percentage_of_respondents_answered",
                    ]
                ].rename(
                    columns={
                        "category": "Category",
                        "practice_or_crop": "Practice / Crop",
                        "respondents_selected": "Submissions Selecting",
                        "respondents_answered": "Submissions Answered",
                        "percentage_of_respondents_answered": "Adoption (%)",
                    }
                )
                st.dataframe(
                    practice_table, hide_index=True, width="stretch"
                )


# TAB 3: GROUP PERFORMANCE
with group_tab:
    st.header("Farmer Group Performance")
    st.caption(
        "Comparisons are submission-level, not verified unique farmer counts."
    )
    group_column = "Name_of_the_Group"

    if group_column not in df.columns:
        st.warning("Farmer group information is unavailable.")
    else:
        group_df = df.copy()
        group_df[group_column] = (
            group_df[group_column].fillna("").astype(str).str.strip()
        )
        group_df = group_df[group_df[group_column] != ""].copy()

        if group_df.empty:
            st.info("No farmer group records are available.")
        else:
            group_df["Group Display"] = (
                group_df[group_column]
                .str.replace("_", " ", regex=False)
                .str.title()
            )
            labelled_indicators = indicators[
                indicators["label_status"] == "Label available"
            ].copy()
            available_categories = sorted(
                labelled_indicators["category"].dropna().unique().tolist()
            )

            comparison_column, note_column = st.columns([2, 1])
            with comparison_column:
                if not available_categories:
                    st.info("No labelled practice categories are available.")
                else:
                    selected_group_category = st.selectbox(
                        "Select practice area",
                        available_categories,
                        key="group_category",
                    )
                    category_options = labelled_indicators[
                        labelled_indicators["category"]
                        == selected_group_category
                    ].copy()

                    if category_options.empty:
                        st.info(
                            "No labelled practices are available in this category."
                        )
                    else:
                        selected_practice = st.selectbox(
                            "Select practice to compare",
                            category_options["practice_or_crop"].tolist(),
                            key="group_practice",
                        )
                        selected_row = category_options[
                            category_options["practice_or_crop"]
                            == selected_practice
                        ].iloc[0]
                        field_name = selected_row["field_name"]
                        choice_code = selected_row["choice_code"]

                        if field_name not in group_df.columns:
                            st.warning(
                                "The selected practice field is missing from the dataset."
                            )
                        else:
                            comparison_results = []
                            for group_name, group_data in group_df.groupby(
                                "Group Display"
                            ):
                                answered = group_data[
                                    group_data[field_name]
                                    .fillna("")
                                    .astype(str)
                                    .str.strip()
                                    != ""
                                ]
                                denominator = len(answered)
                                if denominator == 0:
                                    continue
                                numerator = answered[field_name].apply(
                                    lambda value: choice_code
                                    in str(value).split()
                                ).sum()
                                adoption = numerator / denominator * 100
                                comparison_results.append(
                                    {
                                        "Farmer Group": group_name,
                                        "Submissions Answered": denominator,
                                        "Submissions Selecting": int(numerator),
                                        "Adoption (%)": round(adoption, 1),
                                    }
                                )

                            if not comparison_results:
                                st.info(
                                    "There are no group responses available for this practice."
                                )
                            else:
                                comparison_df = pd.DataFrame(
                                    comparison_results
                                ).sort_values(
                                    "Adoption (%)", ascending=False
                                ).reset_index(drop=True)

                                top_group = comparison_df.iloc[0]
                                lowest_group = comparison_df.iloc[-1]
                                average_adoption = comparison_df[
                                    "Adoption (%)"
                                ].mean()

                                summary_columns = st.columns(3)
                                summary_columns[0].metric(
                                    "Top Performing Group",
                                    top_group["Farmer Group"],
                                    f'{top_group["Adoption (%)"]:.1f}% adoption',
                                )
                                summary_columns[1].metric(
                                    "Lowest Performing Group",
                                    lowest_group["Farmer Group"],
                                    f'{lowest_group["Adoption (%)"]:.1f}% adoption',
                                )
                                summary_columns[2].metric(
                                    "Average Group Adoption",
                                    f"{average_adoption:.1f}%",
                                )
                                group_fig = px.bar(
                                    comparison_df,
                                    x="Adoption (%)",
                                    y="Farmer Group",
                                    orientation="h",
                                    text="Adoption (%)",
                                    hover_data={
                                        "Submissions Answered": True,
                                        "Submissions Selecting": True,
                                        "Adoption (%)": False,
                                    },
                                    title=f"Group Ranking: {selected_practice}",
                                )
                                group_fig.update_traces(
                                    texttemplate="%{text:.1f}%",
                                    textposition="outside",
                                )
                                group_fig.update_layout(
                                    xaxis_title="Adoption (%)",
                                    yaxis_title="Farmer Group",
                                    xaxis=dict(range=[0, 100]),
                                    yaxis=dict(autorange="reversed"),
                                    height=max(450, len(comparison_df) * 32),
                                )
                                st.plotly_chart(
                                    group_fig, use_container_width=True
                                )

                                with st.expander(
                                    "View detailed group ranking table"
                                ):
                                    st.dataframe(
                                        comparison_df,
                                        hide_index=True,
                                        width="stretch",
                                    )

            with note_column:
                st.subheader("How to interpret")
                st.write(
                    "Adoption percentage is submissions selecting the "
                    "practice divided by submissions in the group that "
                    "answered that question."
                )
                st.info(
                    "Groups with small response counts may show large "
                    "percentage changes. Check response counts before "
                    "drawing conclusions."
                )

            st.divider()
            with st.expander(
                "Group Performance Across All Practices",
                expanded=True,
            ):
                st.caption(
                    "Compare each group with each labelled practice in the "
                    "selected category."
                )
                if labelled_indicators.empty:
                    st.info("No labelled practice indicators are available.")
                else:
                    heatmap_categories = ["All Categories"] + sorted(
                        labelled_indicators["category"].dropna().unique().tolist()
                    )
                    selected_heatmap_category = st.selectbox(
                        "Select heatmap category",
                        heatmap_categories,
                        key="heatmap_category",
                    )
                    if selected_heatmap_category == "All Categories":
                        all_practices = labelled_indicators.copy()
                    else:
                        all_practices = labelled_indicators[
                            labelled_indicators["category"]
                            == selected_heatmap_category
                        ].copy()

                    heatmap_results = []
                    for _, practice_row in all_practices.iterrows():
                        field_name = practice_row["field_name"]
                        choice_code = practice_row["choice_code"]
                        if field_name not in group_df.columns:
                            continue
                        practice_label = (
                            str(practice_row["category"])
                            + ": "
                            + str(practice_row["practice_or_crop"])
                        )
                        for group_name, group_data in group_df.groupby(
                            "Group Display"
                        ):
                            answered = group_data[
                                group_data[field_name]
                                .fillna("")
                                .astype(str)
                                .str.strip()
                                != ""
                            ]
                            denominator = len(answered)
                            if denominator == 0:
                                continue
                            numerator = answered[field_name].apply(
                                lambda value: choice_code
                                in str(value).split()
                            ).sum()
                            adoption = numerator / denominator * 100
                            heatmap_results.append(
                                {
                                    "Farmer Group": group_name,
                                    "Practice": practice_label,
                                    "Adoption (%)": round(adoption, 1),
                                }
                            )

                    if heatmap_results:
                        heatmap_df = pd.DataFrame(heatmap_results)
                        heatmap_matrix = heatmap_df.pivot_table(
                            index="Farmer Group",
                            columns="Practice",
                            values="Adoption (%)",
                            aggfunc="first",
                        )
                        heatmap_fig = px.imshow(
                            heatmap_matrix,
                            labels={
                                "x": "Agroecological Practice",
                                "y": "Farmer Group",
                                "color": "Adoption (%)",
                            },
                            aspect="auto",
                            color_continuous_scale="YlGn",
                            zmin=0,
                            zmax=100,
                        )
                        heatmap_fig.update_layout(
                            title="Farmer Group Adoption Heatmap",
                            height=max(500, len(heatmap_matrix) * 35),
                            xaxis_tickangle=-60,
                        )
                        st.plotly_chart(
                            heatmap_fig, use_container_width=True
                        )
                        with st.expander(
                            "View detailed group-by-practice figures"
                        ):
                            st.dataframe(
                                heatmap_df.sort_values(
                                    ["Practice", "Adoption (%)"],
                                    ascending=[True, False],
                                ),
                                hide_index=True,
                                width="stretch",
                            )
                    else:
                        st.info(
                            "No comparable group practice data were found."
                        )


# TAB 4: DATA QUALITY
with quality_tab:
    st.header("Data Quality and Validation")
    quality_columns = st.columns(2)
    quality_columns[0].metric("Data Quality Flags", quality_flag_count)
    quality_columns[1].metric(
        "Submission Occurrences Requiring Review",
        int(affected_submissions),
    )

    if not quality.empty:
        st.write(
            "The following issues were identified during the MHAC data quality audit."
        )
        quality_display = quality.rename(
            columns={
                "category": "Category",
                "issue": "Identified Issue",
                "choice_code": "Choice Code",
                "submissions_affected": "Submissions Affected",
                "status": "Review Status",
            }
        )
        st.dataframe(
            quality_display, hide_index=True, width="stretch"
        )
    else:
        st.info("No data quality report is currently available.")

    st.caption(
        "Data quality flags identify records or response patterns that may "
        "require review. They do not automatically mean a submission is invalid."
    )
