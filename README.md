# example_5

def dataframe_height(df, max_rows=14):
    """
    Calculate table height based on the number of rows.
    Avoid unnecessary empty space below the last record.
    """
    header_height = 38
    row_height = 35

    visible_rows = min(len(df), max_rows)

    return header_height + row_height * max(visible_rows, 1)


def show_table(df, *, key, max_rows=14, link_cols=None):
    """
    Display a responsive, read-only Streamlit dataframe.
    """

    # Remove completely empty records
    df = df.dropna(how="all").reset_index(drop=True)

    # Configure hyperlink columns
    cfg = {
        c: st.column_config.LinkColumn(
            c,
            display_text="Open ↗"
        )
        for c in (link_cols or [])
        if c in df.columns
    }

    # Render table
    st.dataframe(
        df,
        use_container_width=True,
        hide_index=True,
        height=dataframe_height(df, max_rows),
        column_config=cfg,
        key=key
    )
