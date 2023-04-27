import argparse
import json
import os
import sys
import time
import mimetypes
import re

import requests
import http.cookiejar as cookielib


def get_arg_parser():
    parser = argparse.ArgumentParser(
        description='Attempts to download community posts.')
    parser.add_argument('communitypage',
                        help='A text file with a list of commmunity pages')
    parser.add_argument('outputdir',
                        help='A directory to use to store the saved data')
    parser.add_argument('--no-save-intermediaries',
                        help="[not implemented] Do not save intermediate files (Not recommended)")
    parser.add_argument('--cookies',
                        help="Cookies.txt for youtube (needed for members content and posts)")
    return parser


def download_page(url, cookiepath):
    if cookiepath:
        cj = cookielib.MozillaCookieJar(cookiepath)
        cj.load()
        r = requests.get(url, cookies=cj)
    else:
        r = requests.get(url)
    if r.status_code != 200:
        raise ConnectionError("Could not download requested URL")
    return r.text


def extract_script(page):
    result = re.search(
        r"<script.*var ytInitialData = (\{.*\});</script>", page)
    # TODO: error handling
    return result.group(1)


def get_base_post_data(data):
    post_data = {
        "current_timestamp": time.time(),
        "image_urls": None,
        "members_only": False,
    }
    item_section_renderer_contents = data['contents']['twoColumnBrowseResultsRenderer']['tabs'][0][
        'tabRenderer']['content']['sectionListRenderer']['contents'][0]['itemSectionRenderer']['contents']
    for x in item_section_renderer_contents:
        if 'backstagePostThreadRenderer' in x:
            # do stuff
            backstage_post_renderer = x['backstagePostThreadRenderer']['post']['backstagePostRenderer']
            post_data['post_id'] = backstage_post_renderer['postId']
            backstage_post_renderer['publishedTimeText']
            text = backstage_post_renderer['contentText']
            post_data['text'] = text
            if 'sponsorsOnlyBadge' in backstage_post_renderer:
                # I think the existence of this field == members. Could be wrong and is def flimsy.
                post_data['members_only'] = True
            # Assuming a single run here... whatever a run is.
            post_data['published_time_text'] = backstage_post_renderer['publishedTimeText']['runs'][0]['text']
            backstage_attachment = backstage_post_renderer['backstageAttachment']
            if 'postMultiImageRenderer' in backstage_attachment:
                # We have a multi image post here
                images = backstage_attachment['postMultiImageRenderer']['images']
                image_urls = []
                for im in images:
                    backstageImageRenderer = im['backstageImageRenderer']
                    # Assuming that the last item in the thumbnail list is the largest one...
                    image_url = backstageImageRenderer['image']['thumbnails'][-1]['url']
                    image_urls.append(image_url)
                post_data['image_urls'] = image_urls
            elif 'backstageImageRenderer' in backstage_attachment:
                # We have a single image post here
                backstageImageRenderer = backstage_attachment['backstageImageRenderer']
                image_url = backstageImageRenderer['image']['thumbnails'][-1]['url']
                # Also assuming that we can only have one type of attachment here...
                post_data['image_urls'] = [image_url]
            # TODO: maybe support other types of posts (namely pollRenderer)
            break
    return post_data


def download_image_data(urls, output_dir):
    # Looks like images don't require cookies even for members posts. Should be easy to add later if this is ever required...
    for i, u in enumerate(urls):
        r = requests.get(u)
        extension = mimetypes.guess_extension(r.headers['content-type'])
        extension = extension if extension else ".bin"
        with open(os.path.join(output_dir, f"{i}{extension}"), 'wb') as outfile:
            outfile.write(r.content)


if __name__ == "__main__":
    parser = get_arg_parser()
    args = parser.parse_args()
    with open(args.communitypage) as infile:
        urls = [u.strip() for u in infile.readlines()]

    outputdir = args.outputdir

    if not os.path.exists(outputdir):
        os.makedirs(outputdir)
    elif not os.path.isdir(outputdir):
        raise ValueError(f"{args.outputir} is not a valid directory.")

    with open(os.path.join(outputdir, "summary.txt"), 'w') as summaryfile:
        for i, url in enumerate(urls):
            summaryfile.flush()
            print(f"{i}: {url}", file=summaryfile)
            try:
                os.mkdir(os.path.join(outputdir, str(i)))
            except:
                pass
            try:
                page = download_page(url, args.cookies)
            except ConnectionError:
                print(
                    f"An error occurred while trying to download {url}. Might be member post. Check your cookies.", file=sys.stderr)
                print(
                    "Failed to download. Might be member post. Check your cookies.", file=summaryfile)
                continue

            with open(os.path.join(outputdir, str(i), "rawpage.html"), 'w') as rawpagefile:
                rawpagefile.write(page)

            script = extract_script(page)

            with open(os.path.join(outputdir, str(i), "ytinitialdata.json"), 'w') as ytinitialdatafile:
                ytinitialdatafile.write(script)

            try:
                data = json.loads(script)
            except:
                print("JSON parse error", file=sys.stderr)
                print("Failed to parse JSON", file=summaryfile)
                continue

            extracted_data = get_base_post_data(data)

            with open(os.path.join(outputdir, str(i), "extracted_post_data.json"), 'w') as outfile:
                json.dump(extracted_data, outfile, indent=4)

            if 'image_urls' in extracted_data and extracted_data['image_urls']:
                download_image_data(
                    extracted_data['image_urls'], os.path.join(outputdir, str(i)))
