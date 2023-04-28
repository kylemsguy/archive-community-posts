# archive-community-posts
A couple of quick and dirty scripts to help with archiving YouTube community posts (including Members posts)

Hacked together while I'm on vacation because recent events have made scripts like this desirable.

## How to use (TODO: automate the loading of the posts [steps 1-3])
1. Open https://www.youtube.com/@<channel_name>/community
2. Scroll down to the bottom in order to load all of the posts
3. Open up dev console and copy the entire page
4. Save it to a file of your choice (we'll use `community-posts.html` as an example)
5. Run the following command: `python3 extract_post_urls.py community-posts.html -o youryoutubechannelposts.txt` (feel free to change the filenames as you please)
6. Run the following command (omit --cookies if you don't care about members posts): `python3 archive_community_pages.py --cookies youtube.com_cookies.txt youryoutubechannelposts.txt path/to/youtubechannelarchive`
