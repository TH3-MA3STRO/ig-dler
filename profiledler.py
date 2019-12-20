'''
Module to download all the posts from an instagram profile or a selected one using its shortcode
'''
import json
import os
import re
import time
import urllib.parse
import sys
import bs4
import requests
from bs4 import BeautifulSoup

from login import get_id
from queryhashes import query_hash

query_hash = query_hash().posts


class ProfileDler():
    '''
    Downloads all the posts from a profile
    '''

    def __init__(self, username: str, blk, progress, session=None, _filter=None):
        '''
        username: username of profile whose story have to save
        blk: QTextEdit() from pyqt5 where output is displayed
        progress: QProgressBar() from pyqt5 which displays th current progress
        session: Session with login cookies
        filter_title: 'Shortcode' of the post, used to download a particular particular post(only for posts)
        '''
        if sys.platform == 'windows':
            self.dirspace = '\\'
        else:
            self.dirspace = '/'

        self.username = username
        self.blockDisplay = blk
        self.progressDisplay = progress
        self.postCount = 0
        try:
            self.user_id = get_id(self.username)
        except:
            self.blockDisplay.insertPlainText('\nUser Does Not Exists!!\n')
            self.blockDisplay.ensureCursorVisible()
        self.session = session
        self.initialPostNumber = 1
        if _filter is not None:
            self.filter_shortcode = _filter
        else:
            self.filter_shortcode = ''

    def _geturl(self):
        url = 'https://www.instagram.com/{}'.format(self.username)
        page = requests.get(url)
        if page.status_code == 200:
            soup = bs4.BeautifulSoup(page.text, 'lxml')
            scrpt = soup.find('script', text=re.compile(
                "window._sharedData")).text.replace('window._sharedData = ', '')
            scrpt = json.loads(scrpt.replace(';', ''))[
                'entry_data']['ProfilePage'][0]['graphql']['user']
            self.blockDisplay.insertPlainText("\n***ACCOUNT DETAILS***\n\nFull name: {}\nFollowers: {}\nFollowing: {}\nPrivate: {}\n".format(
                scrpt['full_name'], scrpt['edge_followed_by']['count'], scrpt['edge_follow']['count'], scrpt['is_private']))
            self.blockDisplay.ensureCursorVisible()
            return scrpt['profile_pic_url_hd']
        else:
            pass

    def _getdp(self, url, fname):
        img = requests.get(url, stream=True)
        with open(fname, 'wb') as f:
            f.write(img.content)

    def execute(self):
        total = 1
        curr = 0
        try:
            url = self._geturl()
            if not os.path.exists(self.username):
                os.mkdir(self.username)
            filename = self.username + self.dirspace + self.username + '.jpg'
            if url != None:
                dp = self._getdp(url, filename)
                curr += 1
                completed = curr/total
                self.progressDisplay.setValue(completed*100)
                self.blockDisplay.insertPlainText(
                    "\nSUCCESS! Image saved in file: {}\n".format(filename))
                self.blockDisplay.ensureCursorVisible()
            else:
                pass
        except:
            self.blockDisplay.insertPlainText(
                '\nSome Error Occured :(\nPlease Try Again!\n')
            self.blockDisplay.ensureCursorVisible()

    def info(self, shortcode, has_multipleMedia=False):
        '''
        Prints info of a post
        shortcode: Post's shortcode
        has_multipleMedia: bool 
        NOTE: This is an ugly peice of code please don't try to understand what's going on, even I don't know WTH I did in here.
                    I might improve this later but for now I'll leave it as it is xD
        '''
        html = self.session.get('https://www.instagram.com/p/'+shortcode)
        soup = BeautifulSoup(html.text, 'lxml')
        title = soup.find('title').text
        scripts = soup.find_all('script')
        vscript = ''
        for i in scripts:
            if "edge_media_preview_like" in i.text:
                lscript = scripts[scripts.index(i)].text
            if "edge_media_to_caption" in i.text:
                cscript = scripts[scripts.index(i)].text
            if "edge_media_to_parent_comment" in i.text:
                cmscript = scripts[scripts.index(i)].text
            if 'video_view_count' in i.text:
                vscript = scripts[scripts.index(i)].text
        spacer = "-"*55

        if lscript == cscript == cmscript:
            script = lscript
            num_o_likes = json.loads('{' + script[script.index('"edge_media_preview_like"'):script.index(
                ',', script.index('"edge_media_preview_like"'))]+r'}}')['edge_media_preview_like']['count']
            caption = json.loads('{}{}{}'.format('{', script[script.index('"edge_media_to_caption"'):script.index(
                ']}', script.index("edge_media_to_caption"))], r']}}'))['edge_media_to_caption']['edges'][0]['node']['text']
            num_o_cmnts = json.loads('{}{}{}'.format('{', script[script.index('"edge_media_to_parent_comment"'):script.index(
                ',', script.index('"edge_media_to_parent_comment"'))], r'}}'))['edge_media_to_parent_comment']['count']
        else:
            caption = json.loads('{}{}{}'.format('{', cscript[cscript.index(
                '"edge_media_to_caption"'):cscript.index(']}', cscript.index("edge_media_to_caption"))], r']}}'))
            num_o_likes = json.loads('{' + lscript[lscript.index('"edge_media_preview_like"'):lscript.index(
                ',', lscript.index('"edge_media_preview_like"'))]+r'}}')
            num_o_cmnts = json.loads('{}{}{}'.format('{', cmscript[cmscript.index(
                '"edge_media_to_parent_comment"'):cmscript.index(',', cmscript.index('"edge_media_to_parent_comment"'))], r'}}'))
        if vscript != '':
            view_count = 'View Count: {}'.format(json.loads(
                '{'+vscript[vscript.index('"video_view_count"'):vscript.index(',', vscript.index('"video_view_count"'))]+'}')['video_view_count'])
        else:
            view_count = 'Not a Video'
        if has_multipleMedia:
            view_count = "Post has multiple media!"
        self.blockDisplay.insertPlainText('\n{space}\nPost Description: {}\n{space}\nCaption: \n{}\n{space}\nNumber Of likes: {}\nNumber of Comments: {}\n{}\n{space}'.format(
            title, caption, num_o_likes, num_o_cmnts, view_count, space=spacer))
        self.blockDisplay.ensureCursorVisible()

    def downloadmedia(self, res, isvideo, timestamp, side=None):
        '''
        Download media from a post
        isvideo: bool
        res: dictionary of media resources
        timestamp: time at which post was uploaded
        side: optional argument, used for differentiating between multiple media to be downloaded from a single post
        '''
        time_taken = time.strftime(
            "%d_%b_%Y_%H-%M-%S", time.localtime(timestamp))
        if side is None:
            side = ''

        # Checks if a folder with the given username exists or not
        if not os.path.exists(self.username):
            os.mkdir(self.username)

        if not isvideo:
            img_path = '{folder}{dirs}{child_id}{time}.jpg'.format(
                child_id=side, folder=self.username, time=time_taken,dirs=self.dirspace)
            # Checks if the image already exists or not
            if not os.path.exists(img_path):
                with open(img_path, 'wb') as op:
                    op.write(requests.get(res, stream=True).content)
                    self.blockDisplay.insertPlainText('\nDownloaded!\n')
                    self.blockDisplay.ensureCursorVisible()

            else:
                self.blockDisplay.insertPlainText(
                    '\nMedia already exists! SKIPPING....\n')
                self.blockDisplay.ensureCursorVisible()

        else:
            vid_path = '{folder}{dirs}{child_id}{time}.mp4'.format(
                child_id=side, folder=self.username, time=time_taken,dirs=self.dirspace)
            # Checks if the video already exists or not
            if not os.path.exists(vid_path):
                with open(vid_path, 'wb') as op:
                    op.write(requests.get(res, stream=True).content)
                    self.blockDisplay.insertPlainText('\nDownloaded!\n')
                    self.blockDisplay.ensureCursorVisible()
            else:
                self.blockDisplay.insertPlainText(
                    '\nMedia already exists! SKIPPING....\n')
                self.blockDisplay.ensureCursorVisible()

    def get_child_sidecar(self, dicto):
        '''
        Iterate over a post with multiple media
        dicto: dictionary which contains ressources of multiple media 
        '''

        time = dicto["taken_at_timestamp"]
        dicto = dicto["edge_sidecar_to_children"]
        # Number of media in current post (if contains more than one :p)
        length_of_dicto = len(dicto['edges'])
        initial = 1
        self.blockDisplay.insertPlainText(
            '\nPost with multiple media found!\nDownloading all {} posts\n'.format(length_of_dicto))
        self.blockDisplay.ensureCursorVisible()

        for child in dicto['edges']:
            count_info = 'Downloading {}/{}...'.format(
                initial, length_of_dicto)

            if child['node']['__typename'].lower() == 'graphimage':
                self.blockDisplay.insertPlainText(count_info)
                self.blockDisplay.ensureCursorVisible()

                self.downloadmedia(
                    isvideo=False, res=child['node']['display_resources'][2]['src'], timestamp=time, side=child['node']['id'])
                initial += 1

            elif child['node']['__typename'].lower() == 'graphvideo':
                self.blockDisplay.insertPlainText(count_info)
                self.blockDisplay.ensureCursorVisible()

                self.downloadmedia(
                    isvideo=True, res=child['node']['video_url'], timestamp=time, side=child['node']['id'])
                initial += 1

    def getSave_all_posts(self, resp_data):
        for i in resp_data['edge_owner_to_timeline_media']['edges']:
            post_info = 'Downloading post {} of {}...'.format(
                self.initialPostNumber, self.postCount)
            if self.filter_shortcode in i['node']['shortcode']:
                if i['node']['__typename'].lower() == "graphsidecar":
                    self.info(i['node']['shortcode'], has_multipleMedia=True)
                    self.get_child_sidecar(dicto=i['node'])
                    self.initialPostNumber += 1

                elif i['node']['__typename'].lower() == 'graphimage':
                    self.info(i['node']['shortcode'])
                    self.downloadmedia(
                        isvideo=False, res=i['node']['display_resources'][2]['src'], timestamp=i['node']["taken_at_timestamp"])
                    self.initialPostNumber += 1

                elif i['node']['__typename'].lower() == 'graphvideo':
                    self.info(i['node']['shortcode'])
                    self.downloadmedia(
                        isvideo=True, res=i['node']['video_url'], timestamp=i['node']["taken_at_timestamp"])
                    self.initialPostNumber += 1
            else:
                continue
            currProg = self.initialPostNumber/self.postCount
            self.progressDisplay.setValue(currProg*100)

    def profile_iterator(self):
        '''
        Iterates over profile for posts
        '''
        try:
            host = 'www.instagram.com'
            path = 'graphql/query'
            variables = {"id": int(self.user_id), "first": 100, "after": None}
            variables_json = json.dumps(variables, separators=(',', ':'))
            params = {
                'query_hash': query_hash,
                'variables': variables_json
            }

            posts = self.session.get(
                'https://{}/{}/'.format(host, path), params=params)
            resp_data = json.loads(posts.text)['data']['user']
            self.postCount = int(
                resp_data['edge_owner_to_timeline_media']['count'])
            after = resp_data['edge_owner_to_timeline_media']['page_info']
            self.getSave_all_posts(resp_data=resp_data)
            while after['has_next_page']:
                variables['after'] = after['end_cursor']
                variables_json = json.dumps(variables, separators=(',', ':'))
                params['variables'] = variables_json
                posts = self.session.get(
                    'https://{}/{}/'.format(host, path), params=params)
                resp_data = json.loads(posts.text)['data']['user']
                self.getSave_all_posts(resp_data=resp_data)
                after = resp_data['edge_owner_to_timeline_media']['page_info']
            self.blockDisplay.insertPlainText(
                "Downloaded everything from {username}'s profile".format(username=self.username))
            self.blockDisplay.ensureCursorVisible()

        except KeyboardInterrupt:
            pass
