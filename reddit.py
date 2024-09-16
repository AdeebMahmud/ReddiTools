import praw
import requests
import json
import urllib.request
import pandas as pd
from urllib.error import HTTPError, URLError
with open('keys.txt', 'r') as f:
    lines = f.readlines()
    CLIENT_ID = lines[0].strip()
    SECRET_KEY = lines[1].strip()
auth = requests.auth.HTTPBasicAuth(CLIENT_ID, SECRET_KEY)
# take in as user input subreddits to scrape
subreddits = input().split()

with open('pw.txt', 'r') as f:
    pw = f.read()

data = {"grant_type": "password",
        "username": "Takanuvah",
        "password": pw}
headers = {"User-Agent": "nlpAPI/0.0.1 (by u/Takanuvah)"}
response = requests.post("https://www.reddit.com/api/v1/access_token",
                         auth=auth, data=data, headers=headers)
TOKEN = response.json()['access_token']
headers['Authorization'] = f'bearer {TOKEN}'

# Task 1, implement the basic features across multiple subreddits
# Limit to 25 posts per subreddit (can remove later)

# Layer 1: For each subreddit
# test_res = requests.get('https://oauth.reddit.com/r/' +
# "coding" + '/top', headers = headers, params = {'limit': '50', 't': 'all'})

# test_post = test_res.json()['data']['children'][1]
# Thumbnail for main image
# What about multiple images/slides?
# f = open("out.txt", "w")
# f.write(json.dumps(test_res.json()))
# f.close()


def image_download(subreddits):
    download_number = 0
    for i in range(len(subreddits)):
        subreddit = subreddits[i]
        # Add a check to see if the subreddit exists, this works on old subreddits too
        print("NEW SUBREDDIT" + "\n")
        res = requests.get('https://oauth.reddit.com/r/' +
                           subreddit + '/top', headers=headers, params={'limit': '20', 't': 'all'})
        posts = res.json()['data']['children']
        # Layer 2: Within a specific subreddit
        for j in range(len(posts)):
            # Use the preview image instead of thumbnail for higher/original quality.
            # Check if its a gallery, then we handle differently:
            post_hint = posts[j]['data'].get('post_hint')
            if(post_hint and post_hint == "image"):  # single image
                print(posts[j]['data']['title'])
                # replace "preview" with "i" to get the actual image link
                preview_image = posts[j]['data']['preview']['images'][0]['source']['url'].replace(
                    "preview", "i")
                try:
                    # In case a title has "/", replace it with space
                    urllib.request.urlretrieve(
                        preview_image, "data/images/" + str(download_number) + "." + posts[j]['data']['title'].replace("/", " "))
                    download_number += 1
                except URLError:
                    try:  # Try using the url_overridden_by_dest key
                        urllib.request.urlretrieve(posts[j]['data']['url_overridden_by_dest'],
                                                   "data/images/" + str(download_number) + "." + posts[j]['data']['title'])
                        download_number += 1
                    except:  # If that is also giving 403, just skip it
                        print("Image doesn't exist")
            elif(post_hint == None and posts[j]['data']['is_gallery']):
                print(posts[j]['data']['title'])
                print("Gallery post!")
                # look at the metadeta of the gallery
                gallery = posts[j]['data']['media_metadata']
                gallery_counter = 0
                gallery_counted_yet = False
                for post_key in gallery:  # post is the key of a dictionary
                    post = gallery[post_key]
                    if(post['e'] == "Image"):
                        try:  # try to get the original url
                            img_url = post['o'][0]['u'].replace("preview", "i")
                            urllib.request.urlretrieve(
                                img_url, "data/images/" + str(download_number) + "." + str(gallery_counter) + "." + posts[j]['data']['title'])
                            gallery_counter += 1
                            if(gallery_counted_yet == False):
                                download_number += 1
                            gallery_counted_yet = True
                        except URLError:
                            print("Couldn't retrieve image")

                    else:
                        print("gallery item is not an image")


# USING PRAW
# Scrape text data
# Put results into pandas data frame, and add filter cabaility
df = pd.DataFrame()
rows = []
reddit = praw.Reddit(
    client_id=CLIENT_ID,
    client_secret=SECRET_KEY,
    user_agent=f'nlpAPI/0.0.1 (by u/Takanuvah)',
    password=data["password"],
    username=data["username"]
)
# append all comments of subreddits into a dataframe
for subreddit in subreddits:
    sr = reddit.subreddit(subreddit)  # turn into subreddit object
    counter = 0
    limit = 5  # custom limit parameter
    # retrieve limit most recent comments from collection of subreddits
    for comment in sr.stream.comments():
        if(counter >= limit):
            break
        if(comment.author.name != "AutoModerator"):
            rows.append({
                "subreddit": subreddit,
                "author": comment.author.name,
                "post-title": comment.submission.title,
                "comment": comment.body})
            counter += 1
df = pd.DataFrame.from_records(rows)
print(df)
