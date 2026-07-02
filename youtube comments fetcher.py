from googleapiclient.discovery import build
import html
import re
import csv

API_KEY = "AIzaSyDS5y7uMcD1qDP4qTK2vzAaXyRfw1kqut4" 

def get_video_id(url):
    if "v=" in url:
        return url.split("v=")[1].split("&")[0]
    elif "youtu.be/" in url:
        return url.split("youtu.be/")[1].split("?")[0]
    else:
        return None

def clean_comment(text):
    text = html.unescape(text)
    text = re.sub(r'<[^>]+>', '', text)
    return text.strip()

def fetch_comments(video_url, max_comments=500):
    video_id = get_video_id(video_url)
    
    if not video_id:
        print("Invalid URL!")
        return []
    
    youtube = build("youtube", "v3", developerKey=API_KEY)
    
    comments = []
    next_page_token = None
    
    while len(comments) < max_comments:
        response = youtube.commentThreads().list(
            part="snippet",
            videoId=video_id,
            maxResults=min(100, max_comments - len(comments)),
            pageToken=next_page_token
        ).execute()
        
        for item in response["items"]:
            raw = item["snippet"]["topLevelComment"]["snippet"]["textDisplay"]
            likes = item["snippet"]["topLevelComment"]["snippet"]["likeCount"]
            comments.append({
                "comment": clean_comment(raw),
                "likes": likes
            })
        
        next_page_token = response.get("nextPageToken")
        if not next_page_token:
            break
    
    return comments

if __name__ == "__main__":
    url = input("YouTube video URL dalo: ")
    print("Comments fetch ho rahe hain...")
    
    comments = fetch_comments(url, max_comments=500)
    
    # Video ID nikalo filename ke liye
    video_id = get_video_id(url)
    filename = f"comments_{video_id}.csv"
    
    print(f"\nTotal comments fetch hue: {len(comments)}")
    print("\nPehle 3 comments:")
    for i, c in enumerate(comments[:3]):
        print(f"{i+1}. {c['comment'][:100]}")
    
    # CSV save karo
    with open(filename, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=["comment", "likes"])
        writer.writeheader()
        writer.writerows(comments)
    
    print(f"{filename} file save ho gayi!")