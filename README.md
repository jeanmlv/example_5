# example_5

import re

import pandas as pd
import streamlit as st

from src.ui import show_table


# =============================================================================
# CONFIGURATION
# =============================================================================

ASSETS = {
    "SDTM/ADaM": {
        "status_cols": [
            "SDTM/ADaM (Domino)",
            "SDTM/ADaM (Med.ai)",
        ],
        "location_col": "SDTM/ADaM Location",
    },
    "ARD": {
        "status_cols": [
            "Analysis-Ready-Dataset (ARD)",
        ],
        "location_col": "ARD Location",
    },
    "Annotations": {
        "status_cols": [
            "Annotations",
        ],
        "location_col": "Annotations Location",
    },
    "Clinical GT": {
        "status_cols": [
            "Clinical GT",
        ],
        "location_col": "Clinical GT Location",
    },
    "Feature Vectors": {
        "status_cols": [
            "Feature Vectors",
        ],
        "location_col": "Feature Vectors Location",
    },
}


# =============================================================================
# HELPERS
# =============================================================================

def clean_value(value):
    """Return a clean string representation of a cell value."""

    if pd.isna(value):
        return ""

    value = str(value).strip()

    if value.lower() in {"nan", "none", "null"}:
        return ""

    return value


def split_locations(value):
    """
    Split a location cell into individual locations.

    Supports:
    - one location per line
    - multiple locations separated by semicolon
    """

    value = clean_value(value)

    if not value:
        return []

    parts = re.split(r"[\n;]+", value)

    locations = []

    for part in parts:
        part = part.strip()

        if part and part not in locations:
            locations.append(part)

    return locations


def get_locations(df, column):
    """Collect unique locations from a location column."""

    if column not in df.columns:
        return []

    locations = []

    for value in df[column]:
        for location in split_locations(value):
            if location not in locations:
                locations.append(location)

    return locations


def availability_status(value):
    """Normalize availability values."""

    value = clean_value(value).lower()

    if value in {
        "available",
        "yes",
        "y",
        "true",
        "1",
    }:
        return "Available"

    if value in {
        "pending",
        "in progress",
        "in-progress",
    }:
        return "Pending"

    if value in {
        "missing",
        "no",
        "n",
        "false",
        "0",
        "not available",
    }:
        return "Missing"

    if not value:
        return "Not specified"

    return value.title()


def get_asset_status(df, columns):
    """Determine the overall status for an asset."""

    statuses = []

    for column in columns:

        if column not in df.columns:
            continue

        for value in df[column]:
            status = availability_status(value)

            if status != "Not specified":
                statuses.append(status)

    if not statuses:
        return "Not specified"

    if "Available" in statuses:
        return "Available"

    if "Pending" in statuses:
        return "Pending"

    if "Missing" in statuses:
        return "Missing"

    return statuses[0]


def render_location_list(locations):
    """Render individual locations inside an expander."""

    for i, location in enumerate(locations, start=1):

        st.markdown(f"**Location {i}**")

        # Web link
        if location.lower().startswith(
            (
                "http://",
                "https://",
            )
        ):
            st.markdown(f"[Open location ↗]({location})")

        # Domino / filesystem path
        else:
            st.code(location, language=None)

        if i < len(locations):
            st.markdown("")


def render_location_asset(title, status, locations):
    """
    Render one asset/location section.

    Uses native Streamlit components to avoid HTML
    being displayed as raw text.
    """

    status_text = availability_status(status)
    number_locations = len(locations)

    if number_locations == 1:
        location_label = "1 location"
    else:
        location_label = f"{number_locations} locations"

    # -------------------------------------------------------------------------
    # Asset summary
    # -------------------------------------------------------------------------

    col1, col2 = st.columns([5, 1])

    with col1:
        st.markdown(f"**{title}**")
        st.caption(location_label)

    with col2:
        st.markdown(f"**{status_text}**")

    # -------------------------------------------------------------------------
    # Location details
    # -------------------------------------------------------------------------

    if locations:

        if number_locations == 1:
            expander_label = f"View 1 {title.lower()} location"
        else:
            expander_label = (
                f"View {number_locations} "
                f"{title.lower()} locations"
            )

        with st.expander(expander_label):
            render_location_list(locations)

    else:
        st.caption("No location registered.")

    st.markdown("")


# =============================================================================
# AVAILABILITY MATRIX
# =============================================================================

def create_availability_matrix(df):
    """Create the compact study-level availability matrix."""

    if df.empty:
        return pd.DataFrame()

    rows = []

    if "Study ID" in df.columns:
        groups = df.groupby(
            "Study ID",
            dropna=False,
        )
    else:
        groups = [("", df)]

    for study_id, study_df in groups:

        row = {
            "Study ID": study_id,
        }

        if "Study Name" in study_df.columns:
            names = (
                study_df["Study Name"]
                .dropna()
                .astype(str)
                .str.strip()
            )

            row["Study"] = (
                names.iloc[0]
                if not names.empty
                else ""
            )

        # -------------------------------------------------------------
        # Standard availability fields
        # -------------------------------------------------------------

        standard_columns = {
            "Videos": ["Videos"],
            "Med.ai": ["SDTM/ADaM (Med.ai)"],
            "Domino": ["SDTM/ADaM (Domino)"],
            "ARD": ["Analysis-Ready-Dataset (ARD)"],
            "Symptom": ["Symptom Data"],
            "QS": ["QS"],
            "ADQS": ["ADQS"],
        }

        for label, columns in standard_columns.items():
            row[label] = get_asset_status(
                study_df,
                columns,
            )

        # -------------------------------------------------------------
        # Location-based assets
        # -------------------------------------------------------------

        for asset_name, config in ASSETS.items():

            # SDTM/ADaM is already represented by Med.ai + Domino
            if asset_name == "SDTM/ADaM":
                continue

            row[asset_name] = get_asset_status(
                study_df,
                config["status_cols"],
            )

        rows.append(row)

    return pd.DataFrame(rows)


def status_symbol(value):
    """Convert availability status into compact matrix symbol."""

    status = availability_status(value)

    symbols = {
        "Available": "●",
        "Missing": "○",
        "Pending": "◐",
        "Not specified": "–",
    }

    return symbols.get(status, "–")


# =============================================================================
# KPI CALCULATIONS
# =============================================================================

def count_studies_with_asset(df, asset_name):
    """Count studies where an asset is available."""

    if df.empty:
        return 0

    config = ASSETS[asset_name]

    count = 0

    if "Study ID" in df.columns:
        groups = df.groupby(
            "Study ID",
            dropna=False,
        )
    else:
        groups = [("", df)]

    for _, study_df in groups:

        status = get_asset_status(
            study_df,
            config["status_cols"],
        )

        if status == "Available":
            count += 1

    return count


# =============================================================================
# DATA LOCATIONS
# =============================================================================

def render_data_locations(df):
    """
    Show detailed locations when exactly one study is selected.
    """

    if df.empty:
        return

    if "Study ID" not in df.columns:
        return

    study_ids = (
        df["Study ID"]
        .dropna()
        .astype(str)
        .unique()
    )

    if len(study_ids) != 1:
        st.info(
            "Select a single study from the sidebar "
            "to view detailed data locations."
        )
        return

    study_id = study_ids[0]

    study_df = df[
        df["Study ID"].astype(str) == study_id
    ].copy()

    # -------------------------------------------------------------------------
    # Study identification
    # -------------------------------------------------------------------------

    study_name = ""

    if "Study Name" in study_df.columns:

        names = (
            study_df["Study Name"]
            .dropna()
            .astype(str)
            .str.strip()
        )

        if not names.empty:
            study_name = names.iloc[0]

    if study_name:
        st.subheader(study_name)

    st.caption(study_id)

    # -------------------------------------------------------------------------
    # Assets
    # -------------------------------------------------------------------------

    for asset_name, config in ASSETS.items():

        locations = get_locations(
            study_df,
            config["location_col"],
        )

        status = get_asset_status(
            study_df,
            config["status_cols"],
        )

        render_location_asset(
            asset_name,
            status,
            locations,
        )


# =============================================================================
# MAIN RENDER
# =============================================================================

def render(filtered, data):

    # -------------------------------------------------------------------------
    # Header
    # -------------------------------------------------------------------------

    st.header("Data Availability")

    st.markdown(
        """
        <div class="section-note">
        Study-level availability across clinical source data,
        SDTM/ADaM, analysis-ready datasets, annotations,
        clinical ground truth and feature vectors.
        </div>
        """,
        unsafe_allow_html=True,
    )

    df = filtered.get(
        "02_DATA_AVAILABILITY",
        pd.DataFrame(),
    )

    if df.empty:
        st.info(
            "No data availability information is available "
            "for the current selection."
        )
        return

    # -------------------------------------------------------------------------
    # KPI CARDS
    # -------------------------------------------------------------------------

    number_studies = (
        df["Study ID"].nunique()
        if "Study ID" in df.columns
        else 0
    )

    sdtm_available = len(
    get_locations(df, "SDTM/ADaM Location")
    )

    ard_available = len(
    get_locations(df, "ARD Location")
    )

    annotations_available = len(
    get_locations(df, "Annotations Location")
    )

    clinical_gt_available = len(
    get_locations(df, "Clinical GT Location")
    )

    feature_vectors_available = len(
    get_locations(df, "Feature Vectors Location")
    )

    c1, c2, c3, c4, c5, c6 = st.columns(6)

    c1.metric(
        "Studies",
        number_studies,
    )

    c2.metric(
        "SDTM/ADaM",
        sdtm_available,
    )

    c3.metric(
        "ARD",
        ard_available,
    )

    c4.metric(
        "Annotations",
        annotations_available,
    )

    c5.metric(
        "Clinical GT",
        clinical_gt_available,
    )

    c6.metric(
        "Feature Vectors",
        feature_vectors_available,
    )

    # -------------------------------------------------------------------------
    # AVAILABILITY MATRIX
    # -------------------------------------------------------------------------

    st.markdown("### Availability Matrix")

    st.markdown(
        """
        <div class="section-note">
        Study-level overview of available data assets.
        ● Available &nbsp;&nbsp;
        ○ Missing / No &nbsp;&nbsp;
        ◐ Pending
        </div>
        """,
        unsafe_allow_html=True,
    )

    matrix = create_availability_matrix(df)

    if not matrix.empty:

        display_matrix = matrix.copy()

        status_columns = [
            column
            for column in display_matrix.columns
            if column not in [
                "Study ID",
                "Study",
            ]
        ]

        for column in status_columns:
            display_matrix[column] = (
                display_matrix[column]
                .apply(status_symbol)
            )

        show_table(
            display_matrix,
            key="availability_matrix",
            max_rows=20,
        )

    # -------------------------------------------------------------------------
    # DATA LOCATIONS
    # -------------------------------------------------------------------------

    st.markdown("---")

    st.markdown("### Data Locations")

    st.markdown(
        """
        <div class="section-note">
        Detailed storage locations are shown when a single
        study is selected from the sidebar.
        </div>
        """,
        unsafe_allow_html=True,
    )

    render_data_locations(df)
