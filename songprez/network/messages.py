from twisted.protocols import amp

'''
These are AMP commands to be sent between the server (some instance of
SPControl) and the client (responsible for UI and/or display).

A {Set,Song,Search}List contains a list of json-encoded dictionaries. They are
paginated and json-decoded automatically (transparently to the receiver) so the
receiver receives a list of dictionaries.

A Set is a json-encoded SPSet.__dict__. It is json-decoded automatically, the
requester receives an SPSet object. They are uniquely identified (by requester)
by a filepath (actually a relpath).

A Item is a json-encoded SPSong.__dict__ (or some other item type to be added
later). It is json-decoded automatically, the requester receives the actual
object. They are uniquely identified by a relpath. In the case of scripture,
this relpath take the form of <Book Chapter:Verse(s)|Translation>.

The list of supported values for itemtype (when sending/receiving Item objects)
    song (fully supported via SPSong)
    scripture (being implemented)
    image (not yet implemented)
    custom (not yet implemented)
'''

''' Announcements (server-to-client) '''


class Running(amp.Command):
    '''Emitted when server is fully started'''
    arguments = []
    response = []


class SetList(amp.Command):
    '''
    Paginated list of sets. Each set is represented as dictionary with
    'filepath' and 'name' keys.
    '''
    arguments = [('curpage', amp.Integer()), ('totalpage', amp.Integer()),
                 ('jsonlist', amp.ListOf(amp.String()))]
    response = []


class SongList(amp.Command):
    '''
    Paginated list of songs. Each song is represented as dictionary with
    'filepath', 'name', and 'itemtype' keys.
    '''
    arguments = [('curpage', amp.Integer()), ('totalpage', amp.Integer()),
                 ('jsonlist', amp.ListOf(amp.String()))]
    response = []


class ScriptureList(amp.Command):
    arguments = [('curpage', amp.Integer()), ('totalpage', amp.Integer()),
                 ('jsonlist', amp.ListOf(amp.String()))]
    response = []


class CurrentSet(amp.Command):
    '''
    JSON-encoded __dict__ of an SPSet()
    '''
    arguments = [('jsonset', amp.String())]
    response = []


class CurrentItem(amp.Command):
    arguments = [('itemtype', amp.String()), ('jsonitem', amp.String())]
    response = []


class CurrentPosition(amp.Command):
    arguments = [('item', amp.Integer()), ('slide', amp.Integer())]
    response = []


class CurrentToggles(amp.Command):
    '''
    The currently active toggle. One of the following values:-
        'hidden', 'black', 'white', 'freeze', 'normal'
    '''
    argument = [('toggle', amp.String())]
    response = []


''' Request methods (client-to-server, with response) '''


class GetItem(amp.Command):
    arguments = [('itemtype', amp.Unicode()), ('relpath', amp.Unicode())]
    response = [('jsonitem', amp.String())]


class GetSet(amp.Command):
    arguments = [('relpath', amp.Unicode())]
    response = [('jsonset', amp.String())]


class Search(amp.Command):
    arguments = [('term', amp.Unicode())]
    response = [('jsonlist', amp.ListOf(amp.String()))]


class GetBooks(amp.Command):
    arguments = [('version', amp.Unicode())]
    response = [('booklist', amp.ListOf(amp.Unicode()))]


class GetChapters(amp.Command):
    arguments = [('version', amp.Unicode()), ('book', amp.Unicode())]
    response = [('chapterlist', amp.ListOf(amp.Unicode()))]


class GetVerses(amp.Command):
    arguments = [('version', amp.Unicode()), ('book', amp.Unicode()),
                 ('chapter', amp.Unicode())]
    response = [('verselist', amp.ListOf(amp.Unicode())),
                ('verses', amp.ListOf(amp.ListOf(amp.Unicode())))]


''' Control methods (client-to-server, no response) '''


class ChangeCurrentSet(amp.Command):
    '''
    Change the current ShowSet to the set in relpath
    '''
    arguments = [('jsonset', amp.String())]
    response = []


class SaveSet(amp.Command):
    arguments = [('jsonset', amp.String()), ('relpath', amp.Unicode())]
    response = []


class DeleteSet(amp.Command):
    arguments = [('relpath', amp.Unicode())]
    response = []


class AddItemToSet(amp.Command):
    '''
    Add the item at relpath to the current ShowSet
    '''
    arguments = [('itemtype', amp.String()), ('relpath', amp.Unicode()),
                 ('position', amp.Integer())]
    response = []


class RemoveItemFromSet(amp.Command):
    '''
    Remove the item at the given position
    '''
    arguments = [('relpath', amp.Unicode()), ('position', amp.Integer())]
    response = []


class ChangeCurrentItem(amp.Command):
    arguments = [('itemtype', amp.Unicode()), ('jsonsong', amp.String())]
    response = []


class SaveItem(amp.Command):
    arguments = [('itemtype', amp.Unicode()), ('jsonitem', amp.String()),
                 ('relpath', amp.Unicode())]
    response = []


class DeleteItem(amp.Command):
    arguments = [('itemtype', amp.Unicode()), ('relpath', amp.Unicode())]
    response = []


class ChangeCurrentPosition(amp.Command):
    '''
    Update the currently shown item (corresponds with index in current
    ShowItems and ShowSlides lists) and the currently shown slide (corresponds
    with index in inner list of current ShowSlides item).
    '''
    arguments = [('index', amp.Integer()), ('linestart', amp.Integer()),
                 ('lineend', amp.Integer())]
    response = []


class ChangeCurrentToggles(amp.Command):
    '''
    Change the currently active toggle. One of the following values:-
        'hidden', 'black', 'white', 'freeze', 'normal'
    '''
    argument = [('toggle', amp.Unicode())]
    response = []
