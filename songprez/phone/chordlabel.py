#!/usr/bin/env python
import kivy
# kivy.require('1.9.1')
from kivy.core.text import Label as CoreLabel
from kivy.uix.widget import Widget
from kivy.graphics import Rectangle, Color, Scale
from kivy.graphics import PushMatrix, PopMatrix
from kivy.properties import StringProperty
from kivy.metrics import dp
import re
from math import ceil

def _generate_lists(chords, lyrics):
    # Remove first character ('.' or ' ')
    chords = chords[1:]
    lyrics = lyrics[1:]
    # chordslist contains lengths of str, each of which starts
    # with a chord (except perhaps the first) and only contains
    # one chord at most
    chordslist = []
    for c in re.split('(\S+)', chords):
        if not c.isspace():
            chordslist.append(c)
        else:
            if chordslist == []:
                chordslist.append(c)
            else:
                chordslist[-1] += c
    if chordslist[-1] == '':
        chordslist.pop()
    # A running sum generator
    def running_sum(a):
        tot = 0
        for item in a:
            tot += len(item)
            yield tot
    # chordspos contains the positions of each chord
    chordspos = [i for i in running_sum(chordslist)]
    chordspos.insert(0, 0)
    chordspos.pop()
    # Extend lyrics if it's shorter than chords
    lyrics = lyrics + ' '*(len(chords) - len(lyrics))
    # lyricslist contains lengths of lyrics matching the lengths
    # of in chordslist
    lyricslist = []
    initial = chordspos[0]
    for i in chordspos[1:]:
        lyricslist.append(lyrics[initial:i])
        initial = i
    lyricslist.append(lyrics[initial:])
    return chordslist, lyricslist


class ChordLabel(Widget):
    text = StringProperty('')
    
    def __init__(self, **kwargs):
        super(ChordLabel, self).__init__(**kwargs)
        self.spacing = dp(5)

    def on_size(self, instance, value):
        text = self.text.strip()
        # Split up sections
        parts = []
        in_chord = None
        for l in text.split('\n'):
            if in_chord:
                if l and l[0] == ' ': # Song line
                    parts.append(('pair', (in_chord, l)))
                    in_chord = None
                    continue
                else:
                    parts.append(('chord', (in_chord,)))
                    in_chord = None
            if l and l[0] == '.':  # Chord line
                in_chord = l
                continue
            elif l and l[0] == '[':
                parts.append(('label', (l,)))
            else:
                parts.append(('lyric', (l,)))
        
        # For each pair, generate a texture which fits
        max_width = 0
        heights = []
        textures = []
        for t, v in parts:
            if t == 'pair':
                chords, lyrics = v
                chordslist, lyricslist = _generate_lists(chords, lyrics)
                chordstextures, lyricstextures = self._generate_textures(chordslist, lyricslist)
                width = sum([max(c.width if c else 0, l.width if l else 0)
                                for c, l in zip(chordstextures, lyricstextures)])
                if width > max_width:
                    max_width = width
                heights.append(max([l.height if l else 0 
                                    for l in lyricstextures])
                                + max([c.height if c else 0 
                                          for c in chordstextures]))
                textures.append((chordstextures, lyricstextures))
                continue
            elif t == 'chord':
                chordslabel = CoreLabel(font_size=60, bold=False, italic=False,
                               font_name='NotoSansCJK')
                chordslabel.text = v[0][1:]
                chordslabel.refresh()
                texture = chordslabel.texture
            elif t == 'label':
                labelslabel = CoreLabel(font_size=30, bold=False, italic=False,
                               font_name='NotoSansCJK')
                labelslabel.text = v[0]
                labelslabel.refresh()
                texture = labelslabel.texture
            elif t == 'lyric':
                lyricslabel = CoreLabel(font_size=45, bold=False, italic=False,
                               font_name='NotoSansCJK')
                lyricslabel.text = v[0][1:]
                lyricslabel.refresh()
                texture = lyricslabel.texture
            # Check for an empty texture
            if texture.height == 1:
                labelslabel = CoreLabel(font_size=30, bold=False, italic=False,
                               font_name='NotoSansCJK')
                labelslabel.text = ' '
                labelslabel.refresh()
                texture = labelslabel.texture
            if texture.width > max_width:
                max_width = texture.width
            heights.append(texture.height)
            textures.append((texture,))

        # Iterate through possible number of columns
        previous_scale = 0
        for cols in range(1, 8):
            target_height = int(ceil(sum(heights)/float(cols)))
            height = 0
            indices = [0]
            max_height = 0
            for i, h in enumerate(heights):
                if height + h > target_height:
                    # Check if current height or next height is closer
                    if height + float(h/2) > target_height:
                        max_height = height if height > max_height else max_height
                        height = h
                        indices.append(i)
                        continue
                height += h
            if len(indices) > cols:
                indices.pop(-1)
            max_height = height if height > max_height else max_height
            indices.append(-1)
            scale = min(float(self.width)/(cols*max_width+dp(10)*(cols-1)),
                        (float(self.height)/max_height))
            if scale < previous_scale:
                scale = previous_scale
                indices = previous_indices
                break
            previous_scale = scale
            previous_indices = indices
        textures_list = []
        for i in range(len(indices)-1):
            textures_list.append(textures[indices[i]:indices[i+1]])
        textures_list[-1].append(textures[-1])

        self.canvas.clear()
        cols = len(indices) - 1
        total_width = max_width*cols + dp(10)*(cols-1)
        if total_width < self.width/scale:
            start_x = self.x + (self.width/scale-total_width)//2
        else:
            start_x = self.x
        for i, tex_list in enumerate(textures_list):
            with self.canvas:
                PushMatrix()
                Scale(scale, scale, scale, origin=(self.x, self.y+self.height))
                y = self.y + self.height
                x = init_x = start_x + i*(max_width+dp(10))
                for t in tex_list:
                    if len(t) == 2:  # pair of rows
                        t_h = max(l.height if l else 0 for l in t[1])
                        c_h = max(c.height if c else 0 for c in t[0])
                        for c, l in zip(t[0], t[1]):
                            w = 0
                            if l:
                                Rectangle(texture=l, pos=(x, y-c_h-t_h), size=l.size)
                                w = l.width
                            if c:
                                Rectangle(texture=c, pos=(x, y-c_h), size=c.size)
                                w = c.width if c.width > w else w
                            x += w
                        y -= t_h + c_h
                        x = init_x
                    else:
                        Rectangle(texture=t[0], pos=(x, y-t[0].height), size=t[0].size)
                        y -= t[0].height
                        x = init_x
                PopMatrix()

    def _generate_textures(self, chordslist, lyricslist):
        # Generate textures, every lyric texture must be at least
        # as long as the matching chord texture. Chord textures are
        # generated stripped of space except for one trailing (hack
        # to provide separation when placed)
        chordslist = [c.strip() + ' ' if c and not c.isspace() else None
                        for c in chordslist]
        chordstextures = []
        for c in chordslist:
            if not c:
                chordstextures.append(None)
                continue
            chordslabel = CoreLabel(font_size=60, bold=False, italic=False,
                               font_name='NotoSansCJK')
            chordslabel.text = c
            chordslabel.refresh()
            chordstextures.append(chordslabel.texture)
        lyricslabel = CoreLabel(font_size=45, bold=False, italic=False,
                               font_name='NotoSansCJK')
        lyricslabel.text = ' '
        lyricslabel.refresh()
        space_width = lyricslabel.texture.width
        lyricslabel.text = '_'
        lyricslabel.refresh()
        underscore_width = lyricslabel.texture.width
        lyricstextures = []
        for (i, (l, ctex)) in enumerate(zip(lyricslist, chordstextures)):
            if not l:
                lyricstextures.append(None)
                continue
            lyricslabel = CoreLabel(font_size=45, bold=False, italic=False,
                               font_name='NotoSansCJK')
            lyricslabel.text = l
            lyricslabel.refresh()
            if ctex and lyricslabel.texture.width < ctex.width:
                # Need to increase the width of this label
                if l == lyricslist[-1]:  # Last one
                    w = space_width
                    char = ' '
                elif not l[-1].isspace() and not lyricslist[i+1][0].isspace():
                    w = underscore_width
                    char = '_'
                else:
                    w = space_width
                    char = ' '
                count = int(ceil(float(ctex.width
                                       - lyricslabel.texture.width)/w))
                l += count*char
                lyricslabel.text = l
                lyricslabel.refresh()
            lyricstextures.append(lyricslabel.texture)
        return chordstextures, lyricstextures
