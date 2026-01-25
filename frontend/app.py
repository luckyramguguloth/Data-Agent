import streamlit as st
import requests
import json
import pandas as pd
import time
from viz_utils import render_chart

# --- CONFIGURATION ---
st.set_page_config(
    page_title="AI Data Analyst",
    page_icon="✨",
    layout="wide",
    initial_sidebar_state="collapsed" 
)

API_URL = "http://127.0.0.1:8000"

# --- GLASSMORPHISM THEME PRO ---
st.markdown("""
<style>
    /* IMPORT FONTS */
    @import url('https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;600;800&display=swap');
    
    /* GLOBAL RESET & GRADIENT BG */
    .stApp {
        background: radial-gradient(circle at 10% 20%, rgb(0, 50, 100) 0%, rgb(10, 20, 40) 90%);
        font-family: 'Outfit', sans-serif;
        color: #e0f7fa;
    }

    /* GLASS CARD MIXIN */
    .glass-card {
        background: rgba(255, 255, 255, 0.05);
        backdrop-filter: blur(12px);
        -webkit-backdrop-filter: blur(12px);
        border: 1px solid rgba(255, 255, 255, 0.1);
        border-radius: 16px;
        padding: 24px;
        box-shadow: 0 8px 32px 0 rgba(0, 0, 0, 0.37);
        transition: transform 0.3s ease;
    }
    .glass-card:hover {
        transform: translateY(-5px);
        border: 1px solid rgba(255, 255, 255, 0.2);
    }

    /* TYPOGRAPHY */
    h1, h2, h3 {
        color: #ffffff !important;
        font-weight: 800;
        letter-spacing: -0.5px;
    }
    p, label {
        color: #b0bec5 !important;
    }

    /* BUTTONS: NEON GLOW */
    div.stButton > button {
        background: linear-gradient(90deg, #00c6ff 0%, #0072ff 100%);
        color: white;
        border: none;
        padding: 12px 28px;
        font-weight: 600;
        border-radius: 12px;
        box-shadow: 0 0 15px rgba(0, 198, 255, 0.4);
        transition: all 0.3s ease;
        text-transform: uppercase;
        letter-spacing: 1px;
    }
    div.stButton > button:hover {
        box-shadow: 0 0 25px rgba(0, 198, 255, 0.7);
        transform: scale(1.05);
    }
    div.stButton > button:active {
        transform: scale(0.95);
    }

    /* INPUTS */
    .stTextInput > div > div > input, 
    .stSelectbox > div > div > div,
    .stTextArea > div > div > textarea {
        background-color: rgba(0, 0, 0, 0.3) !important;
        border: 1px solid rgba(255, 255, 255, 0.1) !important;
        color: white !important;
        border-radius: 10px;
    }

    /* CHAT BUBBLES */
    .user-msg {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        padding: 12px 18px;
        border-radius: 18px 18px 0 18px;
        margin-bottom: 10px;
        display: inline-block;
        box-shadow: 0 4px 15px rgba(0,0,0,0.2);
    }
    .ai-msg {
        background: rgba(255,255,255,0.1);
        color: #e0f7fa;
        padding: 12px 18px;
        border-radius: 18px 18px 18px 0;
        margin-bottom: 10px;
        display: inline-block;
        border: 1px solid rgba(255,255,255,0.1);
    }

    /* PROGRESS BAR */
    .stProgress > div > div > div > div {
        background: linear-gradient(90deg, #00d2ff 0%, #3a7bd5 100%);
    }

    /* TABS */
    .stTabs [data-baseweb="tab-list"] {
        gap: 8px;
        background-color: rgba(0,0,0,0.2);
        padding: 10px;
        border-radius: 16px;
    }
    .stTabs [data-baseweb="tab"] {
        background-color: transparent;
        color: #90a4ae;
        border-radius: 8px;
        border: none;
    }
    .stTabs [aria-selected="true"] {
        background: rgba(255, 255, 255, 0.1) !important;
        color: #00d2ff !important;
        font-weight: bold;
    }
    
    /* CUSTOM METRIC */
    div[data-testid="stMetricValue"] {
        color: #00d2ff !important;
        font-size: 2rem !important;
    }
</style>
""", unsafe_allow_html=True)

# --- SESSION STATE MANAGEMENT ---
if "analysis_result" not in st.session_state:
    st.session_state.update({
        "analysis_result": None,
        "plot_data": None,
        "filtered_data": None,
        "chat_history": [{"role": "assistant", "content": "Hi! I'm your AI Data Analyst. Upload a file to get started."}],
        "processing": False
    })

# --- UI COMPONENTS ---

def hero_section():
    st.markdown("""
    <div style="text-align: center; padding: 40px 0;">
        <h1 style="font-size: 3.5rem; margin-bottom: 0;">AI Data Agent <span style="color: #00c6ff;">2.0</span></h1>
        <p style="font-size: 1.2rem; opacity: 0.8; margin-top: 10px;">
            Powered by Gemini. <br>
            <i>Fast. Intelligent. Local.</i>
        </p>
    </div>
    """, unsafe_allow_html=True)

def upload_section():
    with st.container():
        st.markdown('<div class="glass-card">', unsafe_allow_html=True)
        uploaded_file = st.file_uploader("📂 Drop CSV, Excel, JSON or Parquet", type=['csv', 'xlsx', 'json', 'parquet'])
        st.markdown('</div>', unsafe_allow_html=True)
        
        if uploaded_file and not st.session_state["analysis_result"]:
            if st.button("🚀 Analyze Data", use_container_width=True):
                with st.status("🔮 AI is processing...", expanded=True) as status:
                    st.write("📤 Uploading & Detecting Type...")
                    files = {"file": (uploaded_file.name, uploaded_file.getvalue())}
                    
                    try:
                        # Upload
                        t1 = time.time()
                        response = requests.post(f"{API_URL}/upload", files=files)
                        
                        if response.status_code == 200:
                            st.write("🧠 Generating Insights (Gemini Flash)...")
                            data = response.json()
                            st.session_state["analysis_result"] = data
                            st.session_state["chat_history"].append({"role": "assistant", "content": f"I've analyzed **{data['filename']}**. What would you like to know?"})
                            
                            # Prefetch data for plotting
                            st.write("📊 Preparing Visuals...")
                            res_sql = requests.post(f"{API_URL}/run_sql/", data={"query": f"SELECT * FROM uploaded_data LIMIT 5000"})
                            if res_sql.status_code == 200:
                                st.session_state["plot_data"] = pd.DataFrame(res_sql.json()["data"])
                            
                            status.update(label="✅ Analysis Complete!", state="complete", expanded=False)
                            time.sleep(0.5)
                            st.rerun()
                        else:
                            st.error(f"Upload failed: {response.text}")
                            status.update(label="❌ Failed", state="error")
                    except Exception as e:
                        st.error(f"Connection Error: {e}")
                        status.update(label="❌ Connection Error", state="error")

def dashboard_view():
    data = st.session_state["analysis_result"]
    try:
        analysis = json.loads(data["analysis"])
    except:
        analysis = {"summary": "Error parsing analysis", "viz_config": {}, "queries": []}

    # Header Stats
    c1, c2, c3, c4 = st.columns(4)
    with c1: st.metric("Rows", f"{data['rows']:,}")
    with c2: st.metric("Columns", len(data['columns']))
    with c3: st.metric("Dimensions", f"{data['rows'] * len(data['columns']):,}")
    with c4: st.metric("AI Model", "Gemini 2.5 Flash")

    st.divider()

    # TABS
    tab_viz, tab_chat, tab_sql, tab_export = st.tabs(["📈 Visual Insights", "💬 Deep Chat", "🛠️ SQL Studio", "📤 Export"])

    with tab_viz:
        st.markdown(f"**AI Summary:** {analysis.get('summary')}")
        
    with tab_viz:
        st.markdown(f"**AI Summary:** {analysis.get('summary')}")
        
        col_main, col_ctrl = st.columns([3, 1])
        
        with col_ctrl:
            st.subheader("🎨 Controls")
            
            # Smart Filters
            df_main = st.session_state["plot_data"]
            if df_main is not None:
                cat_cols = [c for c in df_main.columns if df_main[c].dtype == 'object' and df_main[c].nunique() < 15]
                if cat_cols:
                    st.caption("Apply Filters:")
                    for col in cat_cols[:3]: 
                        selected = st.multiselect(col, df_main[col].unique())
                        if selected:
                            df_main = df_main[df_main[col].isin(selected)]
                
                st.session_state["filtered_data"] = df_main
            
            # Chart Picker
            chart_types = ["bar", "line", "scatter", "pie", "histogram"]
            current_chart = analysis['viz_config'].get('chart_type', 'bar')
            sel_chart = st.selectbox("Chart Type", chart_types, index=chart_types.index(current_chart) if current_chart in chart_types else 0)
            analysis['viz_config']['chart_type'] = sel_chart

        with col_main:
            df_viz = st.session_state["filtered_data"] if st.session_state["filtered_data"] is not None else st.session_state["plot_data"]
            if df_viz is not None:
                fig = render_chart(df_viz, analysis['viz_config'])
                if fig:
                    st.plotly_chart(fig, use_container_width=True)

    with tab_chat:
        c_chat, c_hist = st.columns([3, 1])
        
        with c_chat:
            # BUILD CHAT HTML
            chat_html = '<div class="glass-card" style="height: 500px; overflow-y: auto; display: flex; flex-direction: column; gap: 10px; padding: 20px;">'
            for msg in st.session_state["chat_history"]:
                role_cls = "user-msg" if msg["role"] == "user" else "ai-msg"
                align = "right" if msg["role"] == "user" else "left"
                chat_html += f"<div style='text-align:{align}'><span class='{role_cls}'>{msg['content']}</span></div>"
            chat_html += '</div>'
            
            st.markdown(chat_html, unsafe_allow_html=True)
            st.write("") # Spacer
            
            if prompt := st.chat_input("Ask Gemini about your data..."):
                st.session_state["chat_history"].append({"role": "user", "content": prompt})
                
                # Retrieve Context
                summary_ctx = analysis.get('summary')
                with st.spinner("🤖 Thinking..."):
                    try:
                        res = requests.post(f"{API_URL}/query/", data={"query": prompt, "context": summary_ctx})
                        reply = res.json()['response']
                    except:
                        reply = "Sorry, I couldn't connect to the backend."
                
                st.session_state["chat_history"].append({"role": "assistant", "content": reply})
                st.rerun()

    with tab_sql:
        st.subheader("🛠️ SQL Console")
        query = st.text_area("DuckDB Query", value="SELECT * FROM uploaded_data LIMIT 10", height=150)
        if st.button("Run SQL"):
            res = requests.post(f"{API_URL}/run_sql/", data={"query": query})
            if res.status_code == 200 and "data" in res.json():
                st.dataframe(res.json()["data"], use_container_width=True)
            else:
                st.error("Query Error")

    with tab_export:
        st.subheader("📤 Generate Report")
        st.write("Summarize your findings into a professional presentation.")
        if st.button("📄 Download PowerPoint Report"):
             with st.spinner("Generating Slides..."):
                qs = "; ".join([str(q) for q in analysis.get('queries', [])])
                res = requests.post(f"{API_URL}/export_report/", data={"summary": analysis.get('summary'), "queries": qs, "format": "pptx"})
                st.download_button("Download PPTX", res.content, "analysis_report.pptx")

# --- MAIN LAYOUT ---
hero_section()

if st.session_state["analysis_result"] is None:
    upload_section()
else:
    dashboard_view()
    if st.button("🔄 Start Over", type="secondary"):
        st.session_state["analysis_result"] = None
        st.rerun()