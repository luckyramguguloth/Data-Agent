import plotly.express as px
import pandas as pd
import streamlit as st
import plotly.graph_objects as go

def render_chart(df: pd.DataFrame, config: dict):
    """
    Renders a Plotly chart with smart auto-aggregation and Glassmorphism styling.
    """

    if df is None or df.empty:
        st.warning("⚠️ No data available to visualize.")
        return None

    # --- 1. PRE-PROCESSING & TYPE DETECTION ---
    df = df.copy() 
    
    # Convert 'date'/'time' columns safely
    for col in df.columns:
        if df[col].dtype == 'object':
            # Heuristic: only try if looks like date or name contains date
            if 'date' in col.lower() or 'time' in col.lower() or 'day' in col.lower():
                try:
                    df[col] = pd.to_datetime(df[col], errors='coerce')
                except Exception:
                    pass
            else:
                 # Try convert but don't force it (prevents warnings on random text)
                 try:
                    # Check first not-null value
                    first_valid = df[col].dropna().iloc[0] if not df[col].dropna().empty else None
                    if first_valid and isinstance(first_valid, str) and len(first_valid) > 6 and any(c.isdigit() for c in first_valid):
                         df[col] = pd.to_datetime(df[col], errors='ignore')
                 except:
                     pass

    # Identify column types
    num_cols = df.select_dtypes(include=['number']).columns.tolist()
    cat_cols = df.select_dtypes(include=['object', 'category', 'string']).columns.tolist()
    date_cols = df.select_dtypes(include=['datetime']).columns.tolist()

    # --- 2. SMART CONFIG PARSING ---
    chart_type = config.get("chart_type", "auto").lower()
    x_col = config.get("x_axis")
    y_col = config.get("y_axis")
    title = config.get("title", "Data Visualization")

    # VALIDATION
    if x_col and x_col not in df.columns:
        x_col = None
    if y_col and y_col not in df.columns:
        matches = [c for c in num_cols if y_col.replace("avg_", "").replace("sum_", "") in c]
        if matches:
            y_col = matches[0]
        elif num_cols:
            y_col = num_cols[0]
        else:
            y_col = None

    # --- 3. AUTO-AGGREGATION LOGIC ---
    if chart_type in ["bar", "line", "auto"] and x_col in cat_cols and y_col in num_cols:
        if df[x_col].duplicated().any():
            df = df.groupby(x_col)[y_col].mean().reset_index()
            title = f"Average {y_col} by {x_col}"
            
    # --- 4. FALLBACK CHART SELECTION ---
    if chart_type == "auto" or not x_col:
        # Prioritize Date for X axis
        if date_cols and num_cols:
            chart_type = "line"
            x_col = date_cols[0]
            y_col = num_cols[0]
        elif cat_cols and num_cols:
            chart_type = "bar"
            x_col = cat_cols[0]
            y_col = num_cols[0]
            df = df.groupby(x_col)[y_col].mean().reset_index()
        elif len(num_cols) >= 2:
            chart_type = "scatter"
            x_col = num_cols[0]
            y_col = num_cols[1]
        elif num_cols:
            chart_type = "histogram"
            x_col = num_cols[0]
            y_col = None

    # --- 5. RENDER CHART (GLASSMORPHISM STYLE) ---
    try:
        # Custom Colors: Neon Blue, Purple, Pink, Cyan
        colors = ["#00c6ff", "#0072ff", "#f72585", "#4cc9f0", "#7209b7"]
        
        # Valid PX arguments (Not Layout)
        px_args = {
            "title": title,
            "template": "plotly_dark",
            "height": 500
        }

        if chart_type == "bar":
            fig = px.bar(df, x=x_col, y=y_col, color=x_col if len(df) < 20 else None, 
                         color_discrete_sequence=colors, **px_args)
        elif chart_type == "line":
            fig = px.line(df, x=x_col, y=y_col, markers=True, color_discrete_sequence=colors, **px_args)
            fig.update_traces(line=dict(width=3, color='#00c6ff'))
        elif chart_type == "scatter":
            fig = px.scatter(df, x=x_col, y=y_col, color_discrete_sequence=colors, **px_args)
            fig.update_traces(marker=dict(size=10, opacity=0.8, line=dict(width=1, color='white')))
        elif chart_type == "pie":
            if y_col:
                fig = px.pie(df, names=x_col, values=y_col, color_discrete_sequence=colors, **px_args)
            else:
                fig = px.pie(df, names=x_col, color_discrete_sequence=colors, **px_args)
            fig.update_traces(textinfo='percent+label')
        elif chart_type == "histogram":
            fig = px.histogram(df, x=x_col, nbins=30, color_discrete_sequence=['#00c6ff'], **px_args)
        else:
            fig = px.bar(df, x=x_col, y=y_col, color_discrete_sequence=colors, **px_args)

        # APPLY LAYOUT STYLING AFTER CREATION
        fig.update_layout(
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(255,255,255,0.05)",
            font={"family": "Outfit", "color": "#b0bec5"},
            title_font={"color": "white", "size": 20},
            margin=dict(l=20, r=20, t=50, b=20)
        )
        
        fig.update_xaxes(showgrid=False, zeroline=False)
        fig.update_yaxes(showgrid=True, gridcolor='rgba(255,255,255,0.1)')
        
        return fig

    except Exception as e:
        st.error(f"Visualization Error: {e}")
        return None