#NGO's Project

# Importing the important libraries to be used
import streamlit as st
import random
from streamlit_extras.switch_page_button import switch_page


# To have Wide page
st.set_page_config(page_title="Main", layout="wide", initial_sidebar_state="collapsed")

# Hide the Sidebar
st.markdown("""
            <style>
            [data-testid="stSidebar"] {
                display: none
            }

            [data-testid="collapsedControl"] {
                display: none
            }
            </style>
            """, unsafe_allow_html=True)

# Define the custom CSS
custom_css = """
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Roboto+Slab:wght@700&display=swap');

        .welcome-text {
            text-align: center;
            font-family: 'Roboto Slab', serif;
            font-size: 100px;
            font-weight: bold;
            color: black;
            text-shadow: 11px 2px 4px red;
            animation: fadeInDown 5s;
            transition: all 0.9s ease;
        }

        .welcome-text:hover {
            color: #FF5733;
            text-shadow: 11px 0px 8px black;
            transform: scale(1.2);
        }

        .random-statement {
            text-align: center;
            font-size: 34px;
            color: #4a4a4a;
            animation: fadeIn 2s;
            transition: all 0.9s ease;
        }

        .random-statement:hover {
            color: #FF5733;
            transform: scale(1.1);
        }

        .stButton>button {
            font-size: 40px !important;
            text-align: center;
            color: white;
            padding: 20px;
            width: 95%;
            height: 100%;
            border-radius: 5px;
            background-color: rgb(97, 153, 222);
            transition: all 0.6s ease;
            cursor: pointer;
            border: solid;

        }

        .stButton>button:hover {
            background-color: white ;
            border: solid black;
            transform: scale(1.04) ;
            text-decoration: none ;
            color: black ;
        }

        @keyframes fadeIn {
            from {
                opacity: 0;
            }
            to {
                opacity: 1;
            }
        }

        @keyframes fadeInDown {
            from {
                opacity: 0;
                transform: translateY(-40px);
            }
            to {
                opacity: 1;
                transform: translateY(0);
            }
        }
    </style>
"""

# Allow CSS and HTML
st.markdown(custom_css, unsafe_allow_html=True)

# Display Text
st.markdown('<div class = "welcome-text">WELCOME</div>', unsafe_allow_html=True)
st.markdown('<div class = "random-statement">To Geo Pro</div>', unsafe_allow_html=True)
st.markdown(f'<div class = "random-statement">UNICEF RV</div>', unsafe_allow_html=True)


# Create columns for buttons
col1, col2 = st.columns([1, 1])

# Display buttons on the same line
with col1:
    st.markdown(custom_css, unsafe_allow_html=True)
    if st.button('# View Mood'):
        switch_page('View-Mood')

with col2:
    st.markdown(custom_css, unsafe_allow_html=True)
    if st.button('# Admin Mood'):
        switch_page('Admin-Page')

# Edit footer
footer="""<style>
footer {
	
	visibility: hidden;
	
	}

a:link , a:visited{
color: blue;
background-color: transparent;
text-decoration: none;
}

a:hover,  a:active {
color: red;
background-color: transparent;
text-decoration: none !important;
transform: scale(1.04);
}

.footer {
position: fixed;
left: 0;
bottom: 0;
width: 100%;
background-color: none !important;
color: black;
text-align: center;
}
</style>
<div class="footer">
<p>Developed by ❤<a style='display: block; text-align: center;' href="https://www.linkedin.com/in/hazrat-bilal-3642b4228/" target="_blank">Hazrat Bilal</a></p>
</div>
"""
st.markdown(footer,unsafe_allow_html=True)

# ... footer end
