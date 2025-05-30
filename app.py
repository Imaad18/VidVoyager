import streamlit as st
import requests
from datetime import datetime

# Custom CSS injection with dark sidebar and professional interface
def inject_css():
    st.markdown("""
    <style>
        :root {
            --sidebar-dark: #1a1a2e;
            --sidebar-accent: #16213e;
            --main-bg: #f5f7fa;
            --card-bg: #ffffff;
            --text-dark: #2d3748;
            --text-light: #f8f9fa;
            --primary: #4f46e5;
            --secondary: #7c3aed;
        }
        
        .stApp {
            background-color: var(--main-bg);
        }
        
        /* Dark sidebar */
        [data-testid="stSidebar"] {
            background: linear-gradient(180deg, var(--sidebar-dark), var(--sidebar-accent)) !important;
        }
        
        /* Sidebar text */
        [data-testid="stSidebar"] * {
            color: var(--text-light) !important;
        }
        
        /* Sidebar inputs */
        [data-testid="stSidebar"] .stTextInput input,
        [data-testid="stSidebar"] .stSelectbox select {
            background-color: rgba(255,255,255,0.1) !important;
            color: white !important;
            border-color: rgba(255,255,255,0.3) !important;
        }
        
        /* Main content area */
        .main .block-container {
            background-color: var(--main-bg);
        }
        
        /* Video cards */
        .video-card {
            background-color: var(--card-bg);
            border-radius: 12px;
            padding: 16px;
            margin-bottom: 24px;
            box-shadow: 0 4px 12px rgba(0,0,0,0.05);
            border: 1px solid rgba(0,0,0,0.05);
        }
        
        /* Headers */
        h1, h2, h3, h4, h5, h6 {
            color: var(--text-dark) !important;
        }
        
        /* Buttons */
        .stButton>button {
            background-color: var(--primary) !important;
            color: white !important;
            border-radius: 8px !important;
            padding: 8px 16px !important;
            transition: all 0.3s ease;
        }
        
        .stButton>button:hover {
            background-color: var(--secondary) !important;
            transform: translateY(-2px);
        }
        
        /* Metrics */
        [data-testid="metric-container"] {
            background-color: rgba(79, 70, 229, 0.1) !important;
            border-radius: 8px;
            padding: 8px;
        }
    </style>
    """, unsafe_allow_html=True)

# Initialize session state
def init_session():
    if 'search_history' not in st.session_state:
        st.session_state.search_history = []
    if 'favorites' not in st.session_state:
        st.session_state.favorites = {}

# Enhanced sidebar
def setup_sidebar():
    with st.sidebar:
        st.image("https://images.pexels.com/lib/api/pexels-white.png", width=150)
        st.title("VidVoyager")
        st.markdown("---")
        
        api_key = st.text_input("🔑 API Key", type="password", 
                              help="Get your API key from Pexels.com")
        
        st.markdown("---")
        with st.expander("🔍 Search History"):
            if not st.session_state.search_history:
                st.write("No searches yet")
            else:
                for i, query in enumerate(st.session_state.search_history[-5:]):
                    if st.button(f"{query}", key=f"hist_{i}_{query[:10]}"):
                        st.session_state.last_search = query
        
        with st.expander("❤️ Favorites"):
            if not st.session_state.favorites:
                st.write("No favorites yet")
            else:
                for vid_id, details in st.session_state.favorites.items():
                    st.write(f"⭐ {details['title'][:20]}...")
        
        st.markdown("---")
        st.markdown("### Video Filters")
        orientation = st.selectbox(
            "Orientation", 
            ["Any", "Portrait", "Landscape", "Square"],
            index=0,
            key="sidebar_orientation"
        )
        size = st.selectbox(
            "Size", 
            ["Any", "Large (4K)", "Medium (HD)", "Small (SD)"],
            index=0,
            key="sidebar_size"
        )
        min_duration = st.slider(
            "Minimum Duration (seconds)", 
            0, 60, 5,
            key="sidebar_duration"
        )
        
        st.markdown("---")
        st.markdown("""
        **Tips:**
        - Try specific searches like "ocean waves" or "city timelapse"
        - Click the ⭐ icon to save favorites
        - HD videos will be prioritized when available
        """)
        
        return {
            "api_key": api_key,
            "orientation": orientation.lower() if orientation != "Any" else "",
            "size": size.split(" ")[0].lower() if size != "Any" else "",
            "min_duration": min_duration
        }

# Video card component with unique keys
def video_card(video, index):
    with st.container():
        st.markdown(f"<div class='video-card'>", unsafe_allow_html=True)
        
        col1, col2 = st.columns([4, 1])
        with col1:
            st.subheader(f"Video #{index + 1}")
        with col2:
            if st.button("⭐", key=f"fav_{video['id']}_{index}"):
                if video['id'] not in st.session_state.favorites:
                    st.session_state.favorites[video['id']] = {
                        "title": video.get('user', {}).get('name', 'Unknown'),
                        "url": video['video_files'][0]['link'],
                        "added": datetime.now().strftime("%Y-%m-%d")
                    }
                    st.success("Added to favorites!")
                else:
                    st.error("Already in favorites")
        
        # Get best quality video
        video_files = sorted(
            video['video_files'], 
            key=lambda x: x.get('width', 0) * x.get('height', 0), 
            reverse=True
        )
        best_video = video_files[0] if video_files else None
        
        if best_video:
            st.video(best_video['link'])
            
            cols = st.columns(3)
            with cols[0]:
                st.metric("Duration", f"{video['duration']}s")  # Removed key parameter
            with cols[1]:
                st.metric("Dimensions", f"{video['width']}×{video['height']}")  # Removed key parameter
            with cols[2]:
                st.metric("Quality", best_video['quality'].upper())  # Removed key parameter
            
            st.caption(f"By: {video.get('user', {}).get('name', 'Unknown')}")
            
            with st.expander("Download Options"):
                for i, vf in enumerate(video_files[:3]):
                    st.download_button(
                        label=f"Download {vf['width']}×{vf['height']} ({vf['quality']})",
                        data=requests.get(vf['link']).content,
                        file_name=f"pexels_{video['id']}_{vf['quality']}.mp4",
                        mime="video/mp4",
                        key=f"dl_{video['id']}_{vf['quality']}_{i}"
                    )
        
        st.markdown("</div>", unsafe_allow_html=True)

# Main app function
def main():
    inject_css()
    init_session()
    
    st.title("🌿 VidVoyager")
    st.markdown("Discover high-quality stock videos for your projects")
    
    # Setup sidebar and get filters
    filters = setup_sidebar()
    
    if not filters['api_key']:
        st.warning("Please enter your Pexels API key in the sidebar")
        st.stop()
    
    # Main search interface
    col1, col2 = st.columns([4, 1])
    with col1:
        query = st.text_input(
            "Search videos", 
            value=st.session_state.get('last_search', 'nature'),
            placeholder="Try 'forest' or 'business'...",
            key="main_search_input"
        )
    with col2:
        per_page = st.selectbox("Results", [5, 10, 15, 20], index=0, key="results_per_page")
    
    if st.button("Search", type="primary", key="main_search_button") or query:
        if query and query not in st.session_state.search_history:
            st.session_state.search_history.append(query)
        
        headers = {"Authorization": filters['api_key']}
        params = {
            "query": query,
            "per_page": per_page,
            "orientation": filters['orientation'],
            "size": filters['size'],
            "min_duration": filters['min_duration']
        }
        
        # Clean empty params
        params = {k: v for k, v in params.items() if v}
        
        try:
            with st.spinner("🌱 Searching Pexels..."):
                response = requests.get(
                    "https://api.pexels.com/videos/search",
                    headers=headers,
                    params=params
                )
            
            if response.status_code == 200:
                data = response.json()
                videos = data.get("videos", [])
                
                if not videos:
                    st.warning("No videos found. Try different search terms.")
                else:
                    st.success(f"Found {len(videos)} videos matching your criteria")
                    st.markdown("---")
                    
                    for i, video in enumerate(videos):
                        video_card(video, i)
                    
            else:
                st.error(f"API Error: {response.status_code} - {response.text}")
        
        except Exception as e:
            st.error(f"An error occurred: {str(e)}")
    
    # Footer
    st.markdown("""
    <div class="footer">
        Powered by Pexels API | Made with Streamlit
    </div>
    """, unsafe_allow_html=True)

if __name__ == "__main__":
    main()
