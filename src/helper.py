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
            "bg_app": "#0f0f23",
            "bg_gradient": "linear-gradient(135deg, #0f0f23 0%, #1a1a3e 50%, #0f0f23 100%)",
            "bg_sidebar": "#1a1a2e",
            "text": "#ffffff",
            "text_secondary": "#a0a0b0",
            "card_bg": "#1e1e3f",
            "card_border": "rgba(255, 255, 255, 0.1)",
            "input_bg": "#252547",
            "input_border": "rgba(255, 255, 255, 0.2)",
            "input_text": "#ffffff",
            "primary": "#667eea",
            "primary_gradient": "linear-gradient(135deg, #667eea 0%, #764ba2 100%)",
            "button_text": "#ffffff",
            "secondary_bg": "#1a1a3e",
            "accent": "#f093fb",
            "success": "#4ade80",
            "user_bubble": "linear-gradient(135deg, #667eea 0%, #764ba2 100%)",
            "assistant_bubble": "#1e1e3f",
        }
    else:
        colors = {
            "bg_app": "#fafbfc",
            "bg_gradient": "linear-gradient(135deg, #fafbfc 0%, #f0f4ff 50%, #fafbfc 100%)",
            "bg_sidebar": "#ffffff",
            "text": "#1a1a2e",
            "text_secondary": "#6b7280",
            "card_bg": "#ffffff",
            "card_border": "rgba(0, 0, 0, 0.08)",
            "input_bg": "#ffffff",
            "input_border": "rgba(0, 0, 0, 0.12)",
            "input_text": "#1a1a2e",
            "primary": "#667eea",
            "primary_gradient": "linear-gradient(135deg, #667eea 0%, #764ba2 100%)",
            "button_text": "#ffffff",
            "secondary_bg": "#f8fafc",
            "accent": "#764ba2",
            "success": "#22c55e",
            "user_bubble": "linear-gradient(135deg, #667eea 0%, #764ba2 100%)",
            "assistant_bubble": "#ffffff",
        }

    st.markdown(f"""
    <style>
        /* Import Inter font from Google Fonts */
        @import url('https://fonts.googleapis.com/css2?family=Inter:ital,opsz,wght@0,14..32,100..900;1,14..32,100..900&display=swap');
        @import url('https://fonts.googleapis.com/css2?family=Fira+Code:wght@400;500&display=swap');
        
        /* Root Variables */
        :root {{
            --font-sans: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            --font-mono: 'Fira Code', 'SF Mono', 'Consolas', monospace;
            --transition-fast: 0.15s ease;
            --transition-normal: 0.25s ease;
            --shadow-sm: 0 1px 2px rgba(0, 0, 0, 0.05);
            --shadow-md: 0 4px 6px -1px rgba(0, 0, 0, 0.1), 0 2px 4px -1px rgba(0, 0, 0, 0.06);
            --shadow-lg: 0 10px 15px -3px rgba(0, 0, 0, 0.1), 0 4px 6px -2px rgba(0, 0, 0, 0.05);
            --radius-sm: 6px;
            --radius-md: 12px;
            --radius-lg: 16px;
            --radius-xl: 24px;
        }}
        
        /* Apply Inter font globally */
        html, body, [class*="css"], .stApp, .stMarkdown, p, span, label, div {{
            font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif !important;
        }}
        
        /* Sidebar Section Titles */
        .sidebar-section-title {{
            font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif !important;
            font-size: 1.1rem !important;
            font-weight: 600 !important;
            color: {colors['text']} !important;
            margin: 0 0 0.75rem 0 !important;
            padding: 0 !important;
            letter-spacing: -0.01em;
        }}
        
        .sidebar-subheading {{
            font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif !important;
            font-size: 0.95rem !important;
            font-weight: 600 !important;
            color: {colors['text']} !important;
            margin: 1rem 0 0.5rem 0 !important;
            padding-bottom: 0.5rem !important;
            border-bottom: 2px solid {colors['primary']} !important;
        }}
        
        /* Global Reset & Font */
        html, body, [class*="css"] {{
            font-family: var(--font-sans) !important;
            color: {colors['text']};
            font-size: 16px;
            line-height: 1.6;
            -webkit-font-smoothing: antialiased;
            -moz-osx-font-smoothing: grayscale;
        }}
        
        /* App Background with Gradient */
        .stApp {{
            background: {colors['bg_gradient']};
            background-attachment: fixed;
        }}
        
        /* Main container padding */
        .main .block-container {{
            padding: 2rem 3rem;
            max-width: 1200px;
        }}
        
        /* Typography */
        h1 {{
            font-size: 2.5rem !important;
            font-weight: 700 !important;
            color: {colors['text']} !important;
            letter-spacing: -0.02em;
            margin-bottom: 0.5rem !important;
        }}
        
        h2 {{
            font-size: 1.75rem !important;
            font-weight: 600 !important;
            color: {colors['text']} !important;
            letter-spacing: -0.01em;
        }}
        
        h3 {{
            font-size: 1.25rem !important;
            font-weight: 600 !important;
            color: {colors['text']} !important;
        }}
        
        p, li, span {{
            color: {colors['text_secondary']};
        }}
        
        /* Sidebar Styling */
        [data-testid="stSidebar"] {{
            background: {colors['bg_sidebar']};
            border-right: 1px solid {colors['card_border']};
            box-shadow: var(--shadow-md);
        }}
        
        [data-testid="stSidebar"] > div:first-child {{
            padding: 2rem 1.5rem;
        }}
        
        [data-testid="stSidebar"] h1, 
        [data-testid="stSidebar"] h2, 
        [data-testid="stSidebar"] h3 {{
            color: {colors['text']} !important;
        }}
        
        [data-testid="stSidebar"] p,
        [data-testid="stSidebar"] label,
        [data-testid="stSidebar"] .stMarkdown {{
            color: {colors['text_secondary']} !important;
        }}
        
        /* Sidebar Header Styling */
        [data-testid="stSidebar"] [data-testid="stHeader"] {{
            background: transparent;
        }}
        
        /* Chat Messages Container */
        [data-testid="stChatMessageContainer"] {{
            padding: 0.5rem 0;
        }}
        
        /* Chat Message Bubbles */
        .stChatMessage {{
            background: {colors['assistant_bubble']};
            border: 1px solid {colors['card_border']};
            border-radius: var(--radius-lg) !important;
            padding: 1rem 1.25rem !important;
            margin-bottom: 1rem !important;
            box-shadow: var(--shadow-sm);
            transition: var(--transition-normal);
        }}
        
        .stChatMessage:hover {{
            box-shadow: var(--shadow-md);
            transform: translateY(-1px);
        }}
        
        /* User message styling */
        .stChatMessage[data-testid="user-message"] {{
            background: {colors['user_bubble']};
            border: none;
        }}
        
        .stChatMessage[data-testid="user-message"] p {{
            color: #ffffff !important;
        }}
        
        /* Chat Input */
        .stChatInput {{
            border-radius: var(--radius-lg) !important;
            overflow: hidden;
            border: none !important;
        }}
        
        .stChatInput > div {{
            background: transparent !important;
            border: none !important;
            border-radius: var(--radius-lg) !important;
            transition: var(--transition-fast);
        }}
        
        .stChatInput > div > div {{
            background: {colors['input_bg']} !important;
            border: 2px solid {colors['input_border']} !important;
            border-radius: var(--radius-lg) !important;
        }}
        
        .stChatInput > div > div:focus-within {{
            border-color: {colors['primary']} !important;
            box-shadow: 0 0 0 3px {colors['primary']}25 !important;
        }}
        
        .stChatInput textarea {{
            background: transparent !important;
            color: {colors['input_text']} !important;
            font-family: var(--font-sans) !important;
            font-size: 1rem !important;
            padding: 0.75rem 1rem !important;
            border: none !important;
        }}
        
        .stChatInput textarea::placeholder {{
            color: {colors['text_secondary']} !important;
            opacity: 0.7;
        }}
        
        /* Buttons - Primary Gradient Style */
        div.stButton > button {{
            background: {colors['primary_gradient']};
            color: {colors['button_text']};
            border: none;
            border-radius: var(--radius-md);
            padding: 0.625rem 1.25rem;
            font-family: var(--font-sans);
            font-weight: 600;
            font-size: 0.9rem;
            letter-spacing: 0.01em;
            transition: var(--transition-normal);
            box-shadow: var(--shadow-sm);
            cursor: pointer;
        }}
        
        div.stButton > button:hover {{
            transform: translateY(-2px);
            box-shadow: var(--shadow-lg), 0 0 20px {colors['primary']}40;
            filter: brightness(1.1);
        }}
        
        div.stButton > button:active {{
            transform: translateY(0);
        }}
        
        /* Secondary/Outline Buttons */
        div.stButton > button[kind="secondary"] {{
            background: transparent;
            color: {colors['text']};
            border: 2px solid {colors['input_border']};
        }}
        
        div.stButton > button[kind="secondary"]:hover {{
            border-color: {colors['primary']};
            color: {colors['primary']};
            background: {colors['primary']}10;
        }}
        
        /* Input Fields - Text inputs */
        .stTextInput > div > div {{
            background: transparent !important;
            border: none !important;
            box-shadow: none !important;
        }}
        
        .stTextInput > div > div > input,
        .stTextInput input {{
            background: {colors['input_bg']} !important;
            border: 2px solid {colors['input_border']} !important;
            border-radius: var(--radius-md) !important;
            color: {colors['input_text']} !important;
            font-family: var(--font-sans) !important;
            font-size: 0.95rem !important;
            padding: 0.75rem 1rem !important;
            transition: var(--transition-fast);
            width: 100% !important;
            box-sizing: border-box !important;
        }}
        
        .stTextArea > div > div {{
            background: transparent !important;
            border: none !important;
            box-shadow: none !important;
        }}
        
        .stTextArea textarea {{
            background: {colors['input_bg']} !important;
            border: 2px solid {colors['input_border']} !important;
            border-radius: var(--radius-md) !important;
            color: {colors['input_text']} !important;
            font-family: var(--font-sans) !important;
            font-size: 0.95rem !important;
            padding: 0.75rem 1rem !important;
            transition: var(--transition-fast);
        }}
        
        .stTextInput > div > div > input::placeholder,
        .stTextInput input::placeholder,
        .stTextArea textarea::placeholder {{
            color: {colors['text_secondary']} !important;
            opacity: 0.8 !important;
        }}
        
        .stTextInput > div > div > input:focus,
        .stTextInput input:focus,
        .stTextArea textarea:focus {{
            border-color: {colors['primary']} !important;
            box-shadow: 0 0 0 3px {colors['primary']}25 !important;
            outline: none !important;
        }}
        
        /* Password inputs */
        .stTextInput input[type="password"] {{
            background: {colors['input_bg']} !important;
            color: {colors['input_text']} !important;
        }}
        
        /* All text input containers - remove any borders */
        .stTextInput > div {{
            background: transparent !important;
            border: none !important;
        }}
        
        /* Ensure label styling */
        .stTextInput label,
        .stSelectbox label {{
            color: {colors['text']} !important;
            font-family: var(--font-sans) !important;
            font-size: 0.9rem !important;
            font-weight: 500 !important;
            margin-bottom: 0.25rem !important;
        }}
        
        /* Select boxes - remove wrapper borders */
        .stSelectbox > div {{
            background: transparent !important;
            border: none !important;
        }}
        
        .stSelectbox > div > div {{
            background: {colors['input_bg']} !important;
            border: 2px solid {colors['input_border']} !important;
            border-radius: var(--radius-md) !important;
            color: {colors['input_text']} !important;
        }}
        
        .stSelectbox > div > div > div {{
            color: {colors['input_text']} !important;
        }}
        
        .stSelectbox > div > div:focus-within {{
            border-color: {colors['primary']} !important;
            box-shadow: 0 0 0 3px {colors['primary']}25 !important;
        }}
        
        /* Selectbox dropdown menu */
        [data-baseweb="popover"] ul {{
            background: {colors['card_bg']} !important;
        }}
        
        [data-baseweb="popover"] li {{
            background: {colors['card_bg']} !important;
            color: {colors['text']} !important;
        }}
        
        [data-baseweb="popover"] li:hover {{
            background: {colors['input_bg']} !important;
        }}
        
        /* Radio buttons */
        .stRadio > div {{
            gap: 0.5rem;
            flex-wrap: wrap;
        }}
        
        .stRadio > div > label {{
            background: {colors['input_bg']};
            border: 2px solid {colors['input_border']};
            border-radius: var(--radius-md);
            padding: 0.5rem 0.75rem;
            min-width: 90px;
            text-align: center;
            transition: var(--transition-fast);
            cursor: pointer;
            color: {colors['text']} !important;
            font-size: 0.85rem;
        }}
        
        .stRadio > div > label:hover {{
            border-color: {colors['primary']};
        }}
        
        .stRadio > div > label[data-checked="true"] {{
            background: {colors['primary_gradient']};
            border-color: transparent;
            color: white !important;
        }}
        
        /* Toggle */
        .stToggle > label > div {{
            background: {colors['input_border']};
        }}
        
        .stToggle > label > div[data-checked="true"] {{
            background: {colors['primary_gradient']};
        }}
        
        /* Tabs */
        .stTabs [data-baseweb="tab-list"] {{
            gap: 0.5rem;
            background: transparent;
            border-bottom: 2px solid {colors['card_border']};
            padding-bottom: 0;
        }}
        
        .stTabs [data-baseweb="tab"] {{
            background: transparent;
            border: none;
            border-radius: var(--radius-md) var(--radius-md) 0 0;
            padding: 0.75rem 1.5rem;
            font-weight: 600;
            color: {colors['text_secondary']};
            transition: var(--transition-fast);
        }}
        
        .stTabs [data-baseweb="tab"]:hover {{
            color: {colors['primary']};
        }}
        
        .stTabs [aria-selected="true"] {{
            background: {colors['primary']};
            color: white !important;
        }}
        
        .stTabs [data-baseweb="tab-highlight"] {{
            display: none;
        }}
        
        /* Expanders */
        .streamlit-expanderHeader {{
            background: {colors['secondary_bg']};
            border: 1px solid {colors['card_border']};
            border-radius: var(--radius-md);
            font-weight: 600;
            transition: var(--transition-fast);
        }}
        
        .streamlit-expanderHeader:hover {{
            border-color: {colors['primary']};
        }}
        
        [data-testid="stExpanderDetails"] {{
            background: {colors['secondary_bg']};
            border: 1px solid {colors['card_border']};
            border-top: none;
            border-radius: 0 0 var(--radius-md) var(--radius-md);
            padding: 1rem;
        }}
        
        [data-testid="stExpanderDetails"] * {{
            font-family: var(--font-mono) !important;
            font-size: 0.85rem !important;
        }}
        
        /* Welcome Banner */
        .welcome-banner {{
            background: {colors['card_bg']};
            border: 1px solid {colors['card_border']};
            border-radius: var(--radius-lg);
            padding: 1.5rem 2rem;
            margin-bottom: 2rem;
            position: relative;
            overflow: hidden;
        }}
        
        .welcome-banner::before {{
            content: '';
            position: absolute;
            top: 0;
            left: 0;
            width: 4px;
            height: 100%;
            background: {colors['primary']};
            border-radius: var(--radius-sm) 0 0 var(--radius-sm);
        }}
        
        .welcome-banner h3 {{
            color: {colors['text']} !important;
            margin-bottom: 0.5rem !important;
        }}
        
        .welcome-banner p {{
            color: {colors['text_secondary']} !important;
            margin: 0 !important;
        }}
        
        /* Alerts & Messages */
        .stAlert {{
            background: {colors['secondary_bg']};
            border: 1px solid {colors['card_border']};
            border-radius: var(--radius-md);
            padding: 1rem 1.25rem;
        }}
        
        .stSuccess {{
            border-left: 4px solid {colors['success']};
        }}
        
        .stWarning {{
            border-left: 4px solid #f59e0b;
        }}
        
        .stError {{
            border-left: 4px solid #ef4444;
        }}
        
        .stInfo {{
            border-left: 4px solid {colors['primary']};
        }}
        
        /* Code Blocks */
        code {{
            background: {colors['secondary_bg']} !important;
            color: {colors['accent']} !important;
            padding: 0.2rem 0.4rem;
            border-radius: var(--radius-sm);
            font-family: var(--font-mono) !important;
            font-size: 0.875em !important;
        }}
        
        pre {{
            background: {colors['secondary_bg']} !important;
            border: 1px solid {colors['card_border']};
            border-radius: var(--radius-md) !important;
            padding: 1rem !important;
        }}
        
        pre code {{
            background: transparent !important;
            padding: 0;
        }}
        
        /* Popover */
        [data-testid="stPopover"] > div > button {{
            background: {colors['card_bg']};
            border: 2px solid {colors['input_border']};
            border-radius: var(--radius-md);
            padding: 0.5rem 1rem;
            font-weight: 600;
            transition: var(--transition-fast);
            color: {colors['text']} !important;
        }}
        
        [data-testid="stPopover"] > div > button:hover {{
            border-color: {colors['primary']};
            background: {colors['primary']}10;
        }}
        
        /* Popover Content/Dropdown */
        [data-testid="stPopoverBody"] {{
            background: {colors['card_bg']} !important;
            border: 1px solid {colors['card_border']} !important;
            border-radius: var(--radius-md) !important;
        }}
        
        [data-testid="stPopoverBody"] > div {{
            background: {colors['card_bg']} !important;
        }}
        
        [data-testid="stPopoverBody"] button {{
            background: {colors['card_bg']} !important;
            color: {colors['text']} !important;
            border: none !important;
        }}
        
        [data-testid="stPopoverBody"] button:hover {{
            background: {colors['input_bg']} !important;
        }}
        
        /* Popover container and all children */
        div[data-baseweb="popover"] {{
            background: {colors['card_bg']} !important;
        }}
        
        div[data-baseweb="popover"] > div {{
            background: {colors['card_bg']} !important;
            border: 1px solid {colors['card_border']} !important;
            border-radius: var(--radius-md) !important;
        }}
        
        /* All nested divs in popover */
        div[data-baseweb="popover"] div {{
            background: {colors['card_bg']} !important;
        }}
        
        div[data-baseweb="popover"] hr {{
            border-color: {colors['card_border']} !important;
        }}
        
        /* Forms */
        [data-testid="stForm"] {{
            background: {colors['card_bg']};
            border: 1px solid {colors['card_border']};
            border-radius: var(--radius-lg);
            padding: 1.5rem;
        }}
        
        /* Form Submit Button - Neutral/subtle style */
        [data-testid="stFormSubmitButton"] button,
        [data-testid="stFormSubmitButton"] > button,
        [data-testid="stForm"] button[kind="primary"],
        [data-testid="stForm"] button[type="submit"],
        .stForm button,
        form button[type="submit"] {{
            background: {colors['input_bg']} !important;
            color: {colors['text']} !important;
            border: 2px solid {colors['input_border']} !important;
            border-radius: var(--radius-md) !important;
            padding: 0.625rem 1.25rem !important;
            font-family: var(--font-sans) !important;
            font-weight: 600 !important;
            font-size: 0.9rem !important;
            letter-spacing: 0.01em !important;
            transition: var(--transition-normal) !important;
            box-shadow: none !important;
            cursor: pointer !important;
        }}
        
        [data-testid="stFormSubmitButton"] button:hover,
        [data-testid="stFormSubmitButton"] > button:hover,
        [data-testid="stForm"] button[kind="primary"]:hover,
        [data-testid="stForm"] button[type="submit"]:hover,
        .stForm button:hover,
        form button[type="submit"]:hover {{
            border-color: {colors['primary']} !important;
            color: {colors['primary']} !important;
            background: {colors['input_bg']} !important;
            transform: translateY(-1px) !important;
            box-shadow: var(--shadow-sm) !important;
        }}
        
        [data-testid="stFormSubmitButton"] button:active,
        [data-testid="stFormSubmitButton"] > button:active,
        [data-testid="stForm"] button[kind="primary"]:active,
        [data-testid="stForm"] button[type="submit"]:active,
        .stForm button:active,
        form button[type="submit"]:active {{
            transform: translateY(0) !important;
        }}
        
        /* Dividers */
        hr {{
            border: none;
            border-top: 1px solid {colors['card_border']};
            margin: 1.5rem 0;
        }}
        
        /* Spinner */
        .stSpinner > div {{
            border-color: {colors['primary']} transparent transparent transparent;
        }}
        
        /* Hide Streamlit Branding */
        #MainMenu {{visibility: hidden;}}
        footer {{visibility: hidden;}}
        
        /* Hide the top gradient/colored decoration line */
        [data-testid="stDecoration"] {{
            display: none !important;
        }}
        
        .stDeployButton {{
            display: none !important;
        }}
        
        /* Header area at top of app */
        header[data-testid="stHeader"] {{
            background: {colors['bg_app']} !important;
        }}
        
        [data-testid="stHeader"] {{
            background: {colors['bg_app']} !important;
        }}
        
        [data-testid="stToolbar"] {{
            background: {colors['bg_app']} !important;
        }}
        
        /* App view container */
        [data-testid="stAppViewContainer"] {{
            background: {colors['bg_app']} !important;
        }}
        
        [data-testid="stAppViewBlockContainer"] {{
            background: transparent !important;
        }}
        
        /* Main area background */
        .main {{
            background: {colors['bg_app']} !important;
        }}
        
        section[data-testid="stMain"] {{
            background: {colors['bg_app']} !important;
        }}
        
        /* Bottom container */
        [data-testid="stBottom"] {{
            background: transparent !important;
        }}
        
        [data-testid="stBottom"] > div {{
            background: {colors['bg_app']} !important;
            padding: 1rem;
            border-top: 1px solid {colors['card_border']};
        }}
        
        /* Sticky Header */
        .sticky-header {{
            position: sticky;
            top: 0;
            z-index: 100;
            background: {colors['bg_app']};
            padding: 1.5rem 0;
            margin-bottom: 1rem;
        }}
        
        .sticky-header h1 {{
            margin: 0 !important;
            padding: 0 !important;
            color: {colors['primary']} !important;
            font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif !important;
            font-size: 3.5rem !important;
            font-weight: 700 !important;
            letter-spacing: -0.02em !important;
        }}
        
        /* Scrollbar Styling */
        ::-webkit-scrollbar {{
            width: 8px;
            height: 8px;
        }}
        
        ::-webkit-scrollbar-track {{
            background: {colors['bg_app']};
        }}
        
        ::-webkit-scrollbar-thumb {{
            background: {colors['input_border']};
            border-radius: 4px;
        }}
        
        ::-webkit-scrollbar-thumb:hover {{
            background: {colors['primary']};
        }}
        
        /* Animations */
        @keyframes fadeIn {{
            from {{ opacity: 0; transform: translateY(10px); }}
            to {{ opacity: 1; transform: translateY(0); }}
        }}
        
        .stChatMessage {{
            animation: fadeIn 0.3s ease-out;
        }}
        
        /* Plotly Charts */
        .js-plotly-plot .plotly .main-svg {{
            background: transparent !important;
        }}
        
        /* Caption/Helper Text */
        .stCaption {{
            color: {colors['text_secondary']} !important;
            font-size: 0.875rem;
        }}
        
        /* Metrics */
        [data-testid="stMetric"] {{
            background: {colors['card_bg']};
            border: 1px solid {colors['card_border']};
            border-radius: var(--radius-md);
            padding: 1rem;
        }}
        
        [data-testid="stMetricValue"] {{
            color: {colors['text']} !important;
            font-weight: 700;
        }}
        
        [data-testid="stMetricLabel"] {{
            color: {colors['text_secondary']} !important;
        }}
    </style>
    """, unsafe_allow_html=True)
