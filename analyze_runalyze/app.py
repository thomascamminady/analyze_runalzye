import altair as alt
import polars as pl
import streamlit as st
from color_scheme_names import SCHEMES
from plot_calendar import plot_calendar

if __name__ == "__main__":
    st.title("Your 2024 Running Data")
    st.write(
        "Source code available at https://github.com/thomascamminady/analyze_runalzye"
    )

    st.markdown("## Upload `runalyze-activities.csv`")
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
            .with_columns(date=pl.col("time").dt.date())
            .filter(pl.col("year") == 2024)
            .filter(pl.col("sportid") == 168070)
            .sort("time", descending=False)
            .with_columns(total_distance=pl.col("distance").cum_sum())
            .with_columns(total_elevation=pl.col("elevationUp").cum_sum())
        )

        st.markdown("## Calendar Heatmap")
        scheme = st.selectbox(label="Color scheme", options=SCHEMES)
        chart = plot_calendar(df, scheme)  # type: ignore
        # st.altair_chart(chart, use_container_width=False, theme=None)
        calendar = st.altair_chart(chart, use_container_width=False)  # type: ignore

        st.markdown("## Distance & Elevation Progression")
        base = alt.Chart(
            df.select("time", "total_distance", "total_elevation")
            .interpolate()
            .unpivot(on=["total_distance", "total_elevation"], index="time")
        ).encode(
            x=alt.X("monthdate(time):T").title("Date"),
        )
        chart2 = (
            alt.layer(
                base.mark_line(color="#5276A7")
                .transform_filter(alt.datum.variable == "total_distance")
                .encode(
                    y=alt.Y("value:Q")
                    .title("Total Distance (km)")
                    .axis(titleColor="#5276A7"),
                ),
                base.mark_line(color="#F18727")
                .transform_filter(alt.datum.variable == "total_elevation")
                .encode(
                    y=alt.Y("value:Q")
                    .title("Total Elevation Gain (m)")
                    .axis(titleColor="#F18727"),
                ),
            )
            .properties(width=800, height=400)
            .resolve_scale(y="independent")
        )
        st.altair_chart(chart2, theme="streamlit")  # type: ignore
