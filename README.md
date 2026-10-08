# example_5

from io import BytesIO
import re
import pandas as pd
import plotly.express as px
import streamlit as st
from .config import JNJ_RED, JNJ_DARK, SOFT_RED, BORDER, MUTED

def apply_theme():
    st.markdown(
        f"""
        <style>
        /* =========================================================
           ARGES Commons — theme-aware styling
           Works with both Streamlit Light and Dark modes
           ========================================================= */

        /* Main application */
        .stApp {{
            background-color: var(--background-color);
            color: var(--text-color);
        }}

        .block-container {{
            padding-top: 1.3rem;
            padding-bottom: 3rem;
            max-width: 1500px;
        }}

        /* Sidebar */
        [data-testid="stSidebar"] {{
            background-color: var(--secondary-background-color);
            border-right: 1px solid rgba(128, 128, 128, 0.25);
        }}

        /* Typography */
        h1, h2, h3 {{
            letter-spacing: -0.02em;
            color: var(--text-color);
        }}

        h1 {{
            font-size: 2rem !important;
        }}

        /* =========================================================
           KPI cards
           ========================================================= */

        div[data-testid="stMetric"] {{
            background-color: var(--secondary-background-color);
            border: 1px solid rgba(128, 128, 128, 0.25);
            border-radius: 14px;
            padding: 14px 16px;
            box-shadow: 0 2px 10px rgba(16, 24, 40, 0.06);
        }}

        div[data-testid="stMetricLabel"] {{
            color: var(--text-color) !important;
        }}

        div[data-testid="stMetricLabel"] p {{
            color: var(--text-color) !important;
            opacity: 0.78;
        }}

        div[data-testid="stMetricValue"] {{
            color: var(--text-color) !important;
        }}

        div[data-testid="stMetricValue"] > div {{
            color: var(--text-color) !important;
        }}

        /* =========================================================
           ARGES branding / hero
           ========================================================= */

        .eyebrow {{
            font-size: 12px;
            letter-spacing: .12em;
            text-transform: uppercase;
            color: {JNJ_RED};
            font-weight: 800;
        }}

        .hero {{
            padding: 22px 24px;
            border: 1px solid rgba(128, 128, 128, 0.25);
            border-radius: 18px;
            background-color: var(--secondary-background-color);
            margin-bottom: 18px;
        }}

        .hero-title {{
            font-size: 28px;
            font-weight: 800;
            line-height: 1.15;
            margin: 5px 0 6px 0;
            color: var(--text-color);
        }}

        .hero-copy,
        .section-note {{
            color: var(--text-color);
            opacity: 0.70;
            font-size: 13px;
        }}

        /* =========================================================
           Tables / controls
           ========================================================= */

        [data-testid="stDataFrame"] {{
            border: 1px solid rgba(128, 128, 128, 0.25);
            border-radius: 12px;
            overflow: hidden;
        }}

        hr {{
            border-color: rgba(128, 128, 128, 0.25);
        }}

        </style>
        """,
        unsafe_allow_html=True,
    )

def render_header():
    st.markdown('<div class="hero"><div class="eyebrow">Clinical data inventory</div><div class="hero-title">ARGES Commons Dashboard</div><div class="hero-copy">A study-centric view from source assets and processing through data splits, analysis-ready datasets, variable traceability, analyses, and external data.</div></div>',unsafe_allow_html=True)

def dataframe_height(df,max_rows=14): return min(38+35*(len(df)+1),38+35*(max_rows+1))
def show_table(df,*,key,max_rows=14,link_cols=None):
    cfg={c:st.column_config.LinkColumn(c,display_text='Open ↗') for c in (link_cols or []) if c in df.columns}
    st.dataframe(df,use_container_width=True,hide_index=True,height=dataframe_height(df,max_rows),column_config=cfg,key=key)
def to_excel_bytes(frames):
    bio=BytesIO()
    with pd.ExcelWriter(bio,engine='openpyxl') as writer:
        for sheet,df in frames.items(): df.to_excel(writer,sheet_name=re.sub(r'[\\/*?:\[\]]','_',sheet)[:31],index=False)
    return bio.getvalue()
def download_row(df,stem,*,excel_frames=None):
    c1,c2,_=st.columns([1,1,5])
    with c1: st.download_button('Download CSV',df.to_csv(index=False).encode('utf-8-sig'),f'{stem}.csv','text/csv',key=f'csv_{stem}')
    with c2: st.download_button('Download Excel',to_excel_bytes(excel_frames or {stem[:31]:df}),f'{stem}.xlsx','application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',key=f'xlsx_{stem}')
def donut_from_status(df,col,title):
    if col not in df.columns or df[col].dropna().empty: st.info(f'No data available for {title}.'); return
    x=df[col].fillna('Not specified').astype(str).value_counts().reset_index(); x.columns=[col,'Count']
    fig=px.pie(x,names=col,values='Count',hole=.64,title=title,color_discrete_sequence=[JNJ_RED,'#F97066','#FECACA','#667085','#98A2B3'])
    fig.update_traces(textposition='outside',textinfo='percent+label'); fig.update_layout(height=350,margin=dict(l=10,r=10,t=55,b=10),legend_title_text='')
    st.plotly_chart(fig,use_container_width=True)
