import json
from datetime import date

import altair as alt
import polars as pl
from color_scheme_names import SCHEME_TYPE


@alt.theme.register("my_theme", enable=True)
def loader():
    with open("analyze_runalyze/theme.json") as f:
        return json.load(f)


alt.data_transformers.disable_max_rows()


def plot_calendar(
    df: pl.DataFrame,
    scheme: SCHEME_TYPE = "greens",
) -> alt.LayerChart:
    _domain = [
        "Mon",
        "Tue",
        "Wed",
        "Thu",
        "Fri",
        "Sat",
        "Sun",
        "Mon ",
        "Tue ",
        "Wed ",
        "Thu ",
        "Fri ",
        "Sat ",
        "Sun ",
    ]

    _ = (
        pl.DataFrame(
            pl.Series(
                name="date",
                values=pl.date_range(
                    start=date(2024, 1, 1),
                    end=date(2024, 12, 31),
                    eager=True,
                ),
            )
        )
        .with_columns(
            month=pl.col("date").dt.strftime("%b"),
            weekday=pl.col("date").dt.strftime("%a"),
            dayofmonth=pl.col("date").dt.strftime("%-d").cast(pl.Int32),
            dayofyear=pl.col("date").dt.strftime("%-j").cast(pl.Int32),
        )
        .with_columns(
            col=(pl.col("dayofyear") + 13) % 14,
            row=(pl.col("dayofyear") + 13) // 14,
        )
        .with_columns(
            colname=pl.col("col").map_elements(
                lambda i: _domain[i],
                return_dtype=pl.Utf8,
            ),
            weekday1=pl.col("weekday").map_elements(
                lambda s: s[0], return_dtype=pl.Utf8
            ),
        )
    )

    data = (
        df.with_columns(date=pl.col("time").dt.date())
        .filter(pl.col("year") == 2024, pl.col("sportid") == 168070)
        .sort("time", descending=True)
    )

    _ = (_.join(data, on="date", how="left")).with_columns(
        pl.col("distance").fill_null(0)
    )

    scale = 4
    base = alt.Chart(_).encode(
        x=alt.X("colname:N").scale(domain=_domain).title(None).axis(None),
        y=alt.Y("row:N").title(None).axis(None),
    )

    chart = (
        alt.layer(
            base.mark_rect(
                # fillOpacity=1,
                strokeWidth=6,
                strokeOpacity=1,
                cornerRadius=7,
            ).encode(
                stroke=alt.value("white"),
                color=alt.Color("sum(distance):Q")
                .title("Total distance (km)")
                .legend()
                .scale(scheme=scheme),
            ),
            base.transform_filter(alt.datum.dayofmonth == 1)
            .mark_text(
                fontSize=20,
                color="white",
                opacity=1,
                dx=-22,
                dy=-5,
                align="left",
            )
            .encode(
                text="month",
            ),
            base
            # .transform_filter((alt.datum.weekday == "Mon"))
            .mark_text(
                fontSize=10,
                color="white",
                opacity=1,
                dx=23,
                dy=11,
                align="right",
            ).encode(
                text="weekday",
            ),
            base.mark_text(
                fontSize=10,
                color="white",
                opacity=1,
                dx=-23,
                dy=11,
                align="left",
            ).encode(
                text="dayofmonth",
            ),
        )
        .properties(width=250 * scale, height=297 * scale)
        .configure_view(strokeWidth=0)  # type: ignore
        .configure_axis(grid=False, domain=False)
    )

    return chart
