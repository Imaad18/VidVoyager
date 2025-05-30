import streamlit as st
import requests
import os

# Set up the app
st.title("Pexels Video Search")
st.write("Search for free stock videos from Pexels")

# Get API key (you can enter it in the sidebar)
api_key = st.sidebar.text_input("Enter your Pexels API Key", type="password")

if not api_key:
    st.warning("Please enter your Pexels API key in the sidebar")
    st.stop()

# Search parameters
query = st.text_input("Search for videos", "nature")
per_page = st.slider("Number of videos to display", 1, 20, 5)
orientation = st.selectbox("Orientation", ["any", "portrait", "landscape", "square"])
size = st.selectbox("Size", ["any", "large", "medium", "small"])

if st.button("Search Videos"):
    headers = {"Authorization": api_key}
    params = {
        "query": query,
        "per_page": per_page,
        "orientation": orientation if orientation != "any" else "",
        "size": size if size != "any" else ""
    }
    
    # Remove empty parameters
    params = {k: v for k, v in params.items() if v}
    
    try:
        response = requests.get(
            "https://api.pexels.com/videos/search",
            headers=headers,
            params=params
        )
        
        if response.status_code == 200:
            data = response.json()
            videos = data.get("videos", [])
            
            if not videos:
                st.warning("No videos found. Try a different search term.")
            else:
                st.success(f"Found {len(videos)} videos")
                
                for video in videos:
                    # Get the HD video file if available
                    video_files = video.get("video_files", [])
                    hd_video = next(
                        (vf for vf in video_files if vf.get("quality") == "hd"),
                        video_files[0] if video_files else None
                    )
                    
                    if hd_video:
                        st.subheader(video.get("user", {}).get("name", "Unknown"))
                        st.video(hd_video["link"])
                        st.caption(f"Duration: {video.get('duration')}s | Dimensions: {video.get('width')}x{video.get('height')}")
                        st.write(f"Download: [Link]({hd_video['link']})")
                        st.write("---")
        else:
            st.error(f"Error: {response.status_code} - {response.text}")
    
    except Exception as e:
        st.error(f"An error occurred: {str(e)}")

# Add some instructions
st.sidebar.markdown("""
### How to use:
1. Get your API key from [Pexels](https://www.pexels.com/api/)
2. Enter it in the sidebar
3. Search for videos
4. Click on any video to play it

### Note:
- Videos are streamed directly from Pexels
- API key is only used for the current session
- This app doesn't store your API key
""")
