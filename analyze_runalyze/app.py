import altair as alt
import polars as pl
import streamlit as st
from color_scheme_names import SCHEMES
from plot_calendar import plot_calendar

if __name__ == "__main__":
    st.title("Your 2024 running data")
    st.write(
        "Source code available at https://github.com/thomascamminady/analyze_runalzye"
    )

    uploaded_file = st.file_uploader(
        label="Got to www.runalyze.com -> Account -> Export data -> Activities -> Drag `runalyze-activities.csv` here.",
        type=["csv"],
    )
    if uploaded_file is not None:
        df = (
            pl.read_csv(uploaded_file, infer_schema_length=None)
            .with_columns(
                time=pl.from_epoch(pl.col("time")),
                created=pl.from_epoch(column=pl.col("created")),
            )
            .with_columns(year=pl.col("time").dt.year())
            .sort("time", descending=True)
        )

        scheme = st.selectbox(label="Color scheme", options=SCHEMES)
        chart: alt.Chart = plot_calendar(df, scheme)  # type: ignore
        # st.altair_chart(chart, use_container_width=False, theme=None)
        st.altair_chart(chart, use_container_width=False)
