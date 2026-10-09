# example_5

import pandas as pd
import streamlit as st
from .config import JNJ_RED, MUTED

def clean_text_values(series: pd.Series) -> list[str]:
    return sorted(series.dropna().astype(str).str.strip().loc[lambda s:s.ne('')].unique().tolist())

def render_sidebar_filters(studies: pd.DataFrame) -> tuple[pd.DataFrame,set[str]]:
    with st.sidebar:
        st.markdown(f'<div style="padding:10px 0 20px 0;"><div style="font-family:Georgia,serif;font-size:24px;font-weight:700;color:{JNJ_RED};white-space:nowrap;">Johnson&amp;Johnson</div><div style="font-size:12px;color:{MUTED};margin-top:4px;">ARGES Commons • Clinical Data Inventory</div></div>',unsafe_allow_html=True)
        st.markdown('### Filters')
        eligible=studies.copy()
        selected=st.multiselect('Study',clean_text_values(eligible.get('Study Name',pd.Series(dtype=str))))
        if selected and 'Study Name' in eligible: eligible=eligible[eligible['Study Name'].astype(str).isin(selected)]
        phases=st.multiselect('Phase',clean_text_values(eligible.get('Phase',pd.Series(dtype=str))))
        if phases and 'Phase' in eligible: eligible=eligible[eligible['Phase'].astype(str).isin(phases)]
        statuses=st.multiselect('Trial status',clean_text_values(eligible.get('Trial Status',pd.Series(dtype=str))))
        if statuses and 'Trial Status' in eligible: eligible=eligible[eligible['Trial Status'].astype(str).isin(statuses)]
        compounds=st.multiselect('Compound',clean_text_values(eligible.get('Compound',pd.Series(dtype=str))))
        if compounds and 'Compound' in eligible: eligible=eligible[eligible['Compound'].astype(str).isin(compounds)]
        ids=set(eligible['Study ID'].dropna().astype(str))
        st.markdown('---'); st.caption(f"{len(ids)} of {studies['Study ID'].nunique()} studies selected")
    return eligible, ids
