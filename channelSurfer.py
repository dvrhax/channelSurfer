import xbmc, xbmcaddon, xbmcgui
import random, json, time


class MyPlayer(xbmc.Player):#None of these callbacks work and need this functionality to do a seek at the beginning of new media.
    def __init__(self):
        #xbmc.Player.__init__(self)
        xbmc.log('ChannelSurfer - Instantiating Player', xbmc.LOGWARNING)
        pass

    def onPlayBackEnded(self):
        xbmc.log('ChannelSurfer - PlayBackEnded', xbmc.LOGWARNING)

    def onPlayBackStarted(self):
        xbmc.log('ChannelSurfer - PlayBackStarted', xbmc.LOGWARNING)

    def onPlaybackStopped(self):
        xbmc.log('ChannelSurfer - PlayBackStopped', xbmc.LOGWARNING)

    def onAVStarted(self):
        xbmc.log('ChannelSurfer - AVStarted', xbmc.LOGWARNING)

    def onAVChange(self):
        xbmc.log('ChannelSurfer - AVChange', xbmc.LOGWARNING)

    def onQueueNextItem(self):
        xbmc.log('ChannelSurfer - QueueNextItem', xbmc.LOGWARNING)

#query_AllMovies = '{"jsonrpc": "2.0", "method": "VideoLibrary.GetMovies", "params": {"properties" : ["file"]}, "id": "libMovies"}'
query_AllMovies = '{"jsonrpc": "2.0", "method": "VideoLibrary.GetMovies", "params": {"properties" : ["playcount", "genre", "file"]}, "id": "libMovies"}' #Include Watched and genre data

ret = xbmc.executeJSONRPC(query_AllMovies)
movies = json.loads(ret)['result']['movies']

def getGenres(movies, exclude=[]):
    genres = set()
    for movie in movies:
        genres.update(movie['genre'])
    for e in exclude:
        try:
            genres.remove(e)
        except KeyError:
            pass
    return sorted(genres)

def filterMovies(movies, genre):
    ret = []
    
    for movie in movies:
        if genre == 'Watched':
            if movie['playcount']:
                ret.append(movie)
        elif genre == 'Unwatched':
            if not movie['playcount']:
                ret.append(movie)
        elif genre in movie['genre']:
            ret.append(movie)
    return ret

genres = getGenres(movies)

selected = None
genreSelectPrepend = ['Play', 'Watched', 'Unwatched']
selectedList = []
while True:
    selectionList = genreSelectPrepend + genres
    selected = selectionList[xbmcgui.Dialog().select('Genre Select', selectionList)]
    selectedList.append(selected)
    if selected == 'Play': break
    elif selected in ('Watched', 'Unwatched'):
        genreSelectPrepend = ['Play']
    movies = filterMovies(movies, selected)
    genres = getGenres(movies, selectedList)

playList = xbmc.PlayList(xbmc.PLAYLIST_VIDEO)
for movie in movies:
    playList.add(movie['file'])

playList.shuffle()

player = MyPlayer()
#player.PlayMedia(movie['file'], noresume=True) #Need to figure out the noresume functionality to keep from litering continue watching
player.play(playList)
while not player.isPlaying():#Seek fails if called too early
    time.sleep(2)
player.seekTime(random.randint(60, 300))#Doesn't work reliably and doesn't seem to work at all on Android

lastPlaying = player.getPlayingFile()

while player.isPlaying():#Keeps script alive while media is playing
    if not (lastPlaying == player.getPlayingFile()):#A bit hackish, would prefer to capture a callback event to handle this.
        lastPlaying = player.getPlayingFile()
        player.seekTime(random.randint(60, 300))
    time.sleep(2)
xbmc.log('ChannelSurfer Out', xbmc.LOGWARNING)
