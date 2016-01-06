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

''' Utility methods (server-to-client) '''


class Running(amp.Command):
    '''Emitted when server is fully started'''
    arguments = []
    response = []
    requiresAnswer = False


class SetList(amp.Command):
    '''
    Paginated list of sets. Each set is represented as dictionary with
    'filepath' and 'name' keys.
    '''
    arguments = [('curpage', amp.Integer()), ('totalpage', amp.Integer()),
                 ('jsonlist', amp.ListOf(amp.String()))]
    response = []
    requiresAnswer = False


class SongList(amp.Command):
    '''
    Paginated list of songs. Each song is represented as dictionary with
    'filepath', 'name', and 'itemtype' keys.
    '''
    arguments = [('curpage', amp.Integer()), ('totalpage', amp.Integer()),
                 ('jsonlist', amp.ListOf(amp.String()))]
    response = []
    requiresAnswer = False


class SearchList(amp.Command):
    '''
    Paginated list of search results. Each result is represented as dictionary
    with 'filepath' and 'name' keys (itemtype is assumed to be song).
    '''
    arguments = [('curpage', amp.Integer()), ('totalpage', amp.Integer()),
                 ('jsonlist', amp.ListOf(amp.String()))]
    response = []
    requiresAnswer = False


class ScriptureList(amp.Command):
    arguments = [('curpage', amp.Integer()), ('totalpage', amp.Integer()),
                 ('jsonlist', amp.ListOf(amp.String()))]
    response = []
    requiresAnswer = False


''' Utility methods (client-to-server) '''


class GetItem(amp.Command):
    arguments = [('itemtype', amp.Unicode()), ('relpath', amp.Unicode())]
    response = [('jsonitem', amp.String())]


class GetSet(amp.Command):
    arguments = [('relpath', amp.Unicode())]
    response = [('jsonset', amp.String())]


class Search(amp.Command):
    arguments = [('term', amp.Unicode())]
    response = []
    requiresAnswer = False


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


''' Edit messages (server-to-client) '''


class EditItem(amp.Command):
    arguments = [('itemtype', amp.Unicode()), ('jsonitem', amp.String())]
    response = []
    requiresAnswer = False


class EditSet(amp.Command):
    arguments = [('jsonset', amp.String())]
    response = []
    requiresAnswer = False


''' Edit messages (client-to-server) '''


class ChangeEditItem(amp.Command):
    arguments = [('itemtype', amp.Unicode()), ('relpath', amp.Unicode())]
    response = []
    requiresAnswer = False


class SaveEditItem(amp.Command):
    arguments = [('itemtype', amp.Unicode()), ('jsonitem', amp.String()),
                 ('relpath', amp.Unicode())]
    response = []
    requiresAnswer = False


class NewEditItem(amp.Command):
    arguments = [('itemtype', amp.Unicode()), ('relpath', amp.Unicode())]
    response = []
    requiresAnswer = False


class DeleteEditItem(amp.Command):
    arguments = [('itemtype', amp.Unicode()), ('relpath', amp.Unicode())]
    response = []
    requiresAnswer = False


class ChangeEditSet(amp.Command):
    arguments = [('relpath', amp.Unicode())]
    response = []
    requiresAnswer = False


class SaveEditSet(amp.Command):
    arguments = [('jsonset', amp.String()), ('relpath', amp.Unicode())]
    response = []
    requiresAnswer = False


class NewEditSet(amp.Command):
    arguments = [('relpath', amp.Unicode())]
    response = []
    requiresAnswer = False


class DeleteEditSet(amp.Command):
    arguments = [('relpath', amp.Unicode())]
    response = []
    requiresAnswer = False


''' Show messages (server-to-client) '''


class ShowSet(amp.Command):
    '''
    JSON-encoded __dict__ of an SPSet()
    '''
    arguments = [('jsonset', amp.String())]
    response = []
    requiresAnswer = False


class ShowPosition(amp.Command):
    '''
    The currently shown item (corresponds with index in current ShowItems and
    ShowSlides lists) and the currently shown slide (corresponds with index in
    inner list of current ShowSlides item).
    '''
    arguments = [('item', amp.Integer()), ('slide', amp.Integer())]
    response = []
    requiresAnswer = False


class ShowToggles(amp.Command):
    '''
    The currently active toggle. One of the following values:-
        'hidden', 'black', 'white', 'freeze', 'normal'
    '''
    argument = [('toggle', amp.String())]
    response = []
    requiresAnswer = False


''' Show messages (client-to-server) '''


class Resolution(amp.Command):
    '''
    Update the server on current display resolution, for fontsize selection.
    '''
    arguments = [('width', amp.Integer()), ('height', amp.Integer())]
    response = []
    requiresAnswer = False


class ChangeShowSet(amp.Command):
    '''
    Change the current ShowSet to the set in relpath
    '''
    arguments = [('relpath', amp.Unicode())]
    response = []
    requiresAnswer = False


class AddShowItem(amp.Command):
    '''
    Add the item at relpath to the current ShowSet
    '''
    arguments = [('itemtype', amp.String()), ('relpath', amp.Unicode()),
                 ('position', amp.Integer())]
    response = []
    requiresAnswer = False


class RemoveShowItem(amp.Command):
    '''
    Remove the item at the given position
    '''
    arguments = [('position', amp.Integer())]
    response = []
    requiresAnswer = False


class UpdateShowPosition(amp.Command):
    '''
    Update the currently shown item (corresponds with index in current
    ShowItems and ShowSlides lists) and the currently shown slide (corresponds
    with index in inner list of current ShowSlides item).
    '''
    arguments = [('item', amp.Integer()), ('slide', amp.Integer())]
    response = []
    requiresAnswer = False


class UpdateShowToggles(amp.Command):
    '''
    Change the currently active toggle. One of the following values:-
        'hidden', 'black', 'white', 'freeze', 'normal'
    '''
    argument = [('toggle', amp.String())]
    response = []
    requiresAnswer = False
