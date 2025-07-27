import logging

import discord
import scrapetube


class LatestApi:
    def __init__(self, youtuber: str, limit: int, ctx: discord.Interaction):
        self.ctx = ctx
        self.search = youtuber
        self.limit = limit
        self.channel_id = str()
        self.channel_name = str()
        self.channel_icon = str()
        self.video_titles = list()
        self.video_ids = list()
        self.video_thumbnails = list()
        self.embed = discord.Embed()
        self.success = bool()

        self._get_channel_info()
        self._get_videos_info()
        self._is_success()

    def _get_channel_info(self) -> None:
        """Makes a search on YouTube to find information about the Youtuber"""
        data_search_channel = scrapetube.get_search(self.search, results_type='channel')
        if data_search_channel:
            for channel in data_search_channel:
                self.channel_id = channel.get('channelId')
                self.channel_name = channel.get('title').get('simpleText')
                break

        data_search_video = scrapetube.get_search(self.channel_name)
        if data_search_video:
            for video in data_search_video:
                self.channel_icon = \
                    video['channelThumbnailSupportedRenderers']['channelThumbnailWithLinkRenderer']['thumbnail'][
                        'thumbnails'][
                        0]['url']
                break

    def _get_videos_info(self):
        """Collects videos information in the Youtuber's channel"""
        try:
            for index, video in enumerate(scrapetube.get_channel(self.channel_id)):
                self.video_titles.append(video['title']['runs'][0]['text'])
                self.video_ids.append(video['videoId'])
                self.video_thumbnails.append(video['thumbnail']['thumbnails'][3]['url'])

                if index == self.limit - 1:
                    break
        except Exception as e:
            logging.debug(e)

    def _is_success(self):
        """Verifies if any variable is missing; if so, sets `self.success` to False"""
        args = [
            self.channel_id, self.channel_name, self.channel_icon,
            self.video_titles, self.video_ids, self.video_thumbnails
        ]

        empty_arg = int()

        for index, arg in enumerate(args):
            if not arg:
                empty_arg += 1
            if index + 1 == len(args):
                if empty_arg > 0:
                    self.success = False
                else:
                    self.success = True
