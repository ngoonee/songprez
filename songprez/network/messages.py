from twisted.protocols import amp

''' These are AMP commands to be sent to the display '''

''' Utility methods (server-to-client) '''


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


class SearchList(amp.Command):
    '''
    Paginated list of search results. Each result is represented as dictionary
    with 'filepath' and 'name' keys (itemtype is assumed to be song).
    '''
    arguments = [('curpage', amp.Integer()), ('totalpage', amp.Integer()),
                 ('jsonlist', amp.ListOf(amp.String()))]
    response = []


''' Utility methods (client-to-server) '''


class GetItem(amp.Command):
    arguments = [('itemtype', amp.String()), ('relpath', amp.Unicode())]
    response = [('jsonitem', amp.String())]


class GetSet(amp.Command):
    arguments = [('relpath', amp.Unicode())]
    response = [('jsonset', amp.String())]


class Search(amp.Command):
    arguments = [('term', amp.Unicode())]
    response = []


''' Edit messages (server-to-client) '''


class EditItem(amp.Command):
    arguments = [('itemtype', amp.String()), ('jsonitem', amp.String())]
    response = []


class EditSet(amp.Command):
    arguments = [('jsonset', amp.String())]
    response = []


''' Edit messages (client-to-server) '''


class ChangeEditItem(amp.Command):
    arguments = [('itemtype', amp.String()), ('relpath', amp.Unicode())]
    response = []


class SaveEditItem(amp.Command):
    arguments = [('itemtype', amp.String()), ('jsonitem', amp.String()),
                 ('relpath', amp.Unicode())]
    response = []


class NewEditItem(amp.Command):
    arguments = [('itemtype', amp.String()), ('relpath', amp.Unicode())]
    response = []


class DeleteEditItem(amp.Command):
    arguments = [('itemtype', amp.String()), ('relpath', amp.Unicode())]
    response = []


class ChangeEditSet(amp.Command):
    arguments = [('relpath', amp.Unicode())]
    response = []


class SaveEditSet(amp.Command):
    arguments = [('jsonset', amp.String()), ('relpath', amp.Unicode())]
    response = []


class NewEditSet(amp.Command):
    arguments = [('relpath', amp.Unicode())]
    response = []


class DeleteEditSet(amp.Command):
    arguments = [('relpath', amp.Unicode())]
    response = []


''' Show messages (server-to-client) '''


class ShowSlides(amp.Command):
    '''
    A list of slide-splits, json-encoded.
    After decoding, each song-item in the list takes the following form:-
        [[startline, endline, tag], [startline, endline, tag], ...]
    Each scripture-item in the list takes the following form:-
        [[startchap:startvers, endchap:endverse, book],
         [startchap:startvers, endchap:endverse, book], ...]
    Each item corresponds with one item in the current ShowSet (the ShowItem
    at the same index)
    '''
    arguments = [('curpage', amp.Integer()), ('totalpage', amp.Integer()),
                 ('jsonlist', amp.ListOf(amp.String()))]
    response = []


class ShowItems(amp.Command):
    '''
    Paginated list of songs. Unlike SongList, ShowItems sends the actual SPSong
    objects (json-encoded __dict__) for proper synchronization using ShowSlides
    values.
    '''
    arguments = [('curpage', amp.Integer()), ('totalpage', amp.Integer()),
                 ('jsonlist', amp.ListOf(amp.String()))]
    response = []


class ShowSet(amp.Command):
    '''
    JSON-encoded __dict__ of an SPSet()
    '''
    arguments = [('jsonset', amp.String())]
    response = []


class ShowPosition(amp.Command):
    '''
    The currently shown item (corresponds with index in current ShowItems and
    ShowSlides lists) and the currently shown slide (corresponds with index in
    inner list of current ShowSlides item).
    '''
    arguments = [('item', amp.Integer()), ('slide', amp.Integer())]
    response = []


class ShowToggles(amp.Command):
    '''
    The currently active toggle. One of the following values:-
        'hidden', 'black', 'white', 'freeze', 'normal'
    '''
    argument = [('toggle', amp.String())]
    response = []


''' Show messages (client-to-server) '''


class Resolution(amp.Command):
    '''
    Update the server on current display resolution, for fontsize selection.
    '''
    arguments = [('width', amp.Integer()), ('height', amp.Integer())]
    response = []


class ChangeShowSet(amp.Command):
    '''
    Change the current ShowSet to the set in relpath
    '''
    arguments = [('relpath', amp.Unicode())]
    response = []


class AddShowItem(amp.Command):
    '''
    Add the item at relpath to the current ShowSet
    '''
    arguments = [('itemtype', amp.String()), ('relpath', amp.Unicode()),
                 ('position', amp.Integer())]
    response = []


class RemoveShowItem(amp.Command):
    '''
    Remove the item at the given position
    '''
    arguments = [('position', amp.Integer())]
    response = []


class UpdateShowPosition(amp.Command):
    '''
    Update the currently shown item (corresponds with index in current
    ShowItems and ShowSlides lists) and the currently shown slide (corresponds
    with index in inner list of current ShowSlides item).
    '''
    arguments = [('item', amp.Integer()), ('slide', amp.Integer())]
    response = []


class UpdateShowToggles(amp.Command):
    '''
    Change the currently active toggle. One of the following values:-
        'hidden', 'black', 'white', 'freeze', 'normal'
    '''
    argument = [('toggle', amp.String())]
    response = []
