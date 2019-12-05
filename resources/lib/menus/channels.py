from resources.lib.globals import *

# ==================================================================================================================
#
# Channels Menu
#
# ==================================================================================================================


def getChannels(self):
    success, region = self.auth.getRegionInfo()
    if not success:
        notificationDialog(LANGUAGE(30016))
        return

    USER_DMA = region['USER_DMA']
    USER_OFFSET = region['USER_OFFSET']
    subs = binascii.b2a_base64(str.encode(LEGACY_SUBS.replace('+', ','))).decode().strip()
    channels_url = '%s/cms/publish3/domain/channels/v4/%s/%s/%s/1.json' % \
                   (self.endPoints['cms_url'], USER_OFFSET, USER_DMA, subs)
    log('\r%s' % channels_url)
    response = requests.get(channels_url, headers=HEADERS, verify=VERIFY)
    if response is not None and response.status_code == 200:
        response = response.json()
        if 'subscriptionpacks' in response:
            sub_packs = response['subscriptionpacks']
            for sub_pack in sub_packs:
                if 'channels' in sub_pack:
                    for channel in sub_pack['channels']:
                        self.Channels[channel['channel_guid']] = Channel(channel['channel_guid'], self.endPoints, self.db)


def myChannels(self):
    log('My Channels Menu')
    timestamp = int(time.time())
    if len(self.Channels) == 0: getChannels(self)

    for guid in self.Channels:
        if len(self.Channels[guid].On_Now) == 0 or self.Channels[guid].On_Now['Stop'] < timestamp:
            result, on_now = self.Channels[guid].onNow()
            if result: self.Channels[guid].On_Now = on_now
        infoArt = self.Channels[guid].infoArt()
        if self.Channels[guid].On_Now != {} and self.Channels[guid].On_Now['Stop'] >= timestamp:
            infoArt['thumb'] = self.Channels[guid].On_Now['Thumbnail']
            infoArt['poster'] = self.Channels[guid].On_Now['Poster']

        if self.Channels[guid].infoLabels()['duration'] > 0 and 'OFF-AIR' not in \
                self.Channels[guid].infoLabels()['plot']:
            if self.Channels[guid].On_Demand:
                url = ('%s?mode=demand&guid=%s' % (ADDON_URL, guid))

            context_items = []
            if self.Channels[guid].On_Demand:
                context_items = [
                    ('View On Demand', 'Container.Update(plugin://plugin.video.sling/?'
                                       'mode=demand&guid=%s&name=%s)' % (guid, self.Channels[guid].Name))
                ]
            addLink(self.Channels[guid].Name, self.handleID, self.Channels[guid].Qvt_Url, 'play',
                    self.Channels[guid].infoLabels(), infoArt, self.Channels[guid].ID, context_items)
        elif self.Channels[guid].infoLabels()['duration'] == 0:
            context_items = [
                ('Update On Demand Content', 'RunPlugin(plugin://plugin.video.sling/?mode=demand&guid=%s&'
                                             'action=update)' % guid)
            ]
            addDir(self.Channels[guid].Name, self.handleID, '', 'demand&guid=%s' % guid,
                   self.Channels[guid].infoLabels(), self.Channels[guid].infoArt(), context_items)

    xbmc.executebuiltin('Container.NextSortMethod()')
