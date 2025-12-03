import re
import string
import streamlit as st

def display_code_plots(text):
    pattern = r'```python\s(.*?)```'
    matches = re.findall(pattern, text, re.DOTALL)
    if not matches:
        return None
    else:
        code = matches[0]
        # Replace fig.show() with Streamlit's display method to render inline
        # Replace fig.show() with Streamlit's display method to render inline
        if "fig.show()" in code:
            # Inject template based on current theme if possible, or just default to a good one
            if st.session_state.get('dark_mode', False):
                theme_code = "fig.update_layout(template='plotly_dark', paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)')"
            else:
                theme_code = "fig.update_layout(template='plotly_white', paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)')"
            
            # Insert theme update before showing
            code = code.replace("fig.show()", f"{theme_code}\nst.plotly_chart(fig, use_container_width=True)")
            
        # Ensure common libraries are imported
        imports = []
        if "pandas" not in code and "pd." in code:
            imports.append("import pandas as pd")
        if "plotly.graph_objects" not in code and "go." in code:
            imports.append("import plotly.graph_objects as go")
        if "plotly.express" not in code and "px." in code:
            imports.append("import plotly.express as px")
            
        if imports:
            code = "\n".join(imports) + "\n" + code
            
        return code

def display_text_with_images(text):
    """
    Display text with associated images.
    Args:
        text (str): The text to be displayed.
    Returns:
        None
    """

    # Modify the regex to remove potential '[voir image]' and parentheses around the URL
    image_urls = re.findall(r"https?://[^\s]+image[^\s]*.jpg", text, flags=re.IGNORECASE)

    # Replace the markdown image syntax with just the URL for splitting
    text_for_splitting = re.sub(r"-? +?!?\[lien vers l'image\]\s*\(?(https?://[^\s]+image[^\s]*.jpg)\)?",
        r"\1 \n ", text, flags=re.IGNORECASE)

    # Split text at image URLs
    parts = re.split(r"https?://[^\s]+image[^\s]*.jpg", text_for_splitting)

    for i, part in enumerate(parts):
        # If there is punctuation character, parts[i] must have at least one alpha character.
        if any(char in string.punctuation for char in part) and not any(
            char.isalpha() for char in part
        ):
            continue
        # Display the text part
        st.markdown(part.replace("\n", "\n\n"))

        # Display the image if it exists
        if i < len(image_urls):
            st.image(image_urls[i])

def inject_custom_css(is_dark_mode):
    if is_dark_mode:
        colors = {
            "bg_app": "#09090b",      # Zinc 950
            "bg_sidebar": "#18181b",  # Zinc 900
            "text": "#fafafa",        # Zinc 50
            "card_bg": "#18181b",
            "card_border": "#27272a", # Zinc 800
            "input_bg": "#27272a",
            "input_border": "#3f3f46",# Zinc 700
            "input_text": "#fafafa",
            "primary": "#60a5fa",     # Blue 400
            "button_text": "#ffffff",
            "secondary_bg": "#18181b"
        }
    else:
        colors = {
            "bg_app": "#fafafa",      # Zinc 50
            "bg_sidebar": "#ffffff",  # White
            "text": "#3f3f46",        # Zinc 700
            "card_bg": "#ffffff",
            "card_border": "#eeeef0", # Zinc 200
            "input_bg": "#ffffff",
            "input_border": "#eeeef0",
            "input_text": "#3f3f46",
            "primary": "#60a5fa",     # Blue 400
            "button_text": "#ffffff",
            "secondary_bg": "#ffffff"
        }

    st.markdown(f"""
    <style>
        /* Global Font Settings - Import Inter */
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');
        
        html, body, [class*="css"] {{
            font-family: 'Inter', 'Source Sans Pro', sans-serif;
            color: {colors['text']};
        }}
        
        /* App Background */
        .stApp {{
            background-color: {colors['bg_app']};
        }}
        
        /* Title */
        h1, h2, h3 {{
            color: {colors['text']};
            font-weight: 700;
            letter-spacing: -0.025em;
            padding-bottom: 0.5rem;
        }}
        
        /* Card-like styling for chat messages */
        .stChatMessage {{
            background-color: {colors['secondary_bg']};
            border: 1px solid {colors['card_border']};
            border-radius: 12px;
            padding: 15px;
            margin-bottom: 10px;
            box-shadow: 0 1px 2px 0 rgba(0, 0, 0, 0.05);
        }}
        
        /* Sidebar styling */
        [data-testid="stSidebar"] {{
            background-color: {colors['bg_sidebar']};
            border-right: 1px solid {colors['card_border']};
        }}
        
        [data-testid="stSidebar"] .block-container {{
            padding-top: 1rem;
        }}
        
        /* Custom Button - Outline Style */
        div.stButton > button {{
            background-color: {colors['bg_app']};
            color: {colors['text']};
            border: 1px solid {colors['input_border']};
            border-radius: 8px;
            padding: 0.5rem 1rem;
            font-weight: 500;
            transition: all 0.2s ease;
            box-shadow: 0 1px 2px 0 rgba(0, 0, 0, 0.05);
            opacity: 0.9;
        }}
        
        div.stButton > button:hover {{
            border-color: {colors['primary']};
            color: {colors['primary']};
            background-color: {colors['secondary_bg']};
            transform: translateY(-1px);
            opacity: 1;
        }}
        
        /* Primary Button Override */
        div.stButton > button[kind="primary"] {{
            background-color: {colors['primary']};
            color: {colors['button_text']};
            border: none;
        }}
        
        /* Popover Button Styling */
        [data-testid="stPopover"] button {{
            background-color: {colors['bg_app']};
            color: {colors['text']};
            border: 1px solid {colors['input_border']};
            border-radius: 8px;
            font-weight: 500;
            opacity: 0.9;
        }}
        
        [data-testid="stPopover"] button:hover {{
            border-color: {colors['primary']};
            color: {colors['primary']};
            opacity: 1;
        }}
        
        /* Input fields */
        .stTextInput input, .stSelectbox div[data-baseweb="select"] > div {{
            border-radius: 8px;
            border: 1px solid {colors['input_border']};
            background-color: {colors['input_bg']};
            color: {colors['input_text']};
        }}
        
        .stTextInput input:focus, .stSelectbox div[data-baseweb="select"] > div:focus-within {{
            border-color: {colors['primary']};
            box-shadow: 0 0 0 2px {colors['primary']}33; /* 20% opacity hex */
        }}
        
        /* Text color overrides */
        p, label, .stMarkdown {{
            color: {colors['text']} !important;
        }}
        
        /* Welcome Banner */
        .welcome-banner {{
            background-color: {colors['secondary_bg']};
            border: 1px solid {colors['card_border']};
            border-left: 5px solid {colors['primary']};
            padding: 20px;
            border-radius: 10px;
            margin-bottom: 20px;
        }}
        
        /* Chat Input Styling */
        .stChatInput textarea {{
            background-color: {colors['input_bg']} !important;
            color: {colors['input_text']} !important;
            border: 1px solid {colors['input_border']} !important;
        }}
        
        /* Fix for the bottom container background */
        [data-testid="stBottom"], footer, header {{
            background-color: {colors['bg_app']} !important;
        }}
        
        [data-testid="stBottom"] > div {{
            background-color: {colors['bg_app']} !important;
        }}
        
        /* Ensure the main container background is consistent */
        .stApp > header {{
            background-color: {colors['bg_app']} !important;
        }}
        
        /* Alerts */
        .stAlert {{
            background-color: {colors['secondary_bg']};
            color: {colors['text']};
            border: 1px solid {colors['card_border']};
        }}
        
        /* Code blocks */
        code, pre {{
            background-color: {colors['secondary_bg']} !important;
            color: {colors['text']} !important;
            border-radius: 6px;
        }}
        
        /* Plotly chart background */
        .js-plotly-plot .plotly .main-svg {{
            background-color: transparent !important;
        }}
        
        /* Tool output (expanders) styling to look like code */
        [data-testid="stExpanderDetails"] {{
            background-color: {colors['secondary_bg']};
            border-radius: 8px;
            padding: 10px;
        }}
        
        [data-testid="stExpanderDetails"] * {{
            font-family: 'Fira Code', 'Consolas', 'Monaco', 'Andale Mono', 'Ubuntu Mono', monospace !important;
            font-size: 0.85rem !important;
        }}
        
        /* Sticky Header */
        .sticky-header {{
            position: sticky;
            top: 0;
            z-index: 100;
            background-color: {colors['bg_app']};
            padding: 1rem 0;
            border-bottom: 1px solid {colors['card_border']};
            margin-bottom: 1rem;
        }}
        
        .sticky-header h1 {{
            margin: 0;
            padding: 0;
        }}
    </style>
    """, unsafe_allow_html=True)
