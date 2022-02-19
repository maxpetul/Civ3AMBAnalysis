
# Table of Contents

1.  [AMB overview](#orge95a964)
2.  [Useful links](#orgc111dbe)
3.  [Format overview](#org64a43d8)
4.  [Endianess and null termination conventions](#org2ef1ee8)
5.  [Type definitions](#org30c9479)
6.  [Prgm chunk](#orga48220d)
7.  [KmapItem](#org1b60f5e)
8.  [Kmap chunk](#orgb6b3b9b)
9.  [Glbl chunk](#org63db5af)
10. [InfoTrack](#org79b9b3b)
11. [SoundTrack](#org66bed77)
12. [Embedded Midi](#org9836c50)


<a id="orge95a964"></a>

# AMB overview

AMB files are used by the game Sid Meier's Civilization III. They describe a sound effect as a combination of sound files with randomized effects
applied. As far as I know these files were created by Firaxis for Civ 3 and never used for anything else.


<a id="orgc111dbe"></a>

# Useful links

-   Overview of MIDIs:
    <https://www.skytopia.com/project/articles/midi.html>
-   MIDI spec:
    <https://www.cs.cmu.edu/~music/cmsip/readings/Standard-MIDI-file-format-updated.pdf>
-   Previous work:
    -   <https://forums.civfanatics.com/threads/modifying-amb-files.326218/>
    -   <https://forums.civfanatics.com/threads/sounds-overlapping-repeating.347898/>
    -   <https://forums.civfanatics.com/threads/sounds-question-on-amb-files.112884/#post-2579780>


<a id="org64a43d8"></a>

# Format overview

An AMB file is made up of many Prgm and Kmap chunks, exactly one Glbl chunk, and exactly one embedded Midi file. AMBs follow the Resource
Interchange File Format, so every chunk begins with a 4-character identifier followed by a 4-byte integer size. The embedded Midi specifies a time
offset at which each component sound is to be played. Each component sound corresponds to a Prgm chunk which specifies randomized effects and a
variable name. Finally the variable name is associated with a sound file name by a Kmap chunk. As far as I can tell, the Glbl chunk contains no
useful information.


<a id="org2ef1ee8"></a>

# Endianess and null termination conventions

Be aware that the AMB files use two different conventions here. Inside the embedded Midi file integers are big endian and strings are not
null-terminated, while outside the embedded Midi, i.e., in the Prgm, Kmap, and Glbl chunks, integers are little endian and strings are null
terminated.


<a id="org30c9479"></a>

# Type definitions

-   tag: Array of 4 ASCII characters
-   int: 4-byte integer. Signedness unknown, but the value contained is positive and too small for it to make a difference
-   signed int: 4-byte integer that is definitely signed
-   short: 2-byte integer
-   str+0: String including null terminator
-   str: String without null terminator
-   vlq: "variable length quantity" from Midi spec. Check the spec for all the details but the jist of it is that a VLQ is a simple compression scheme
    for 4-byte integers. In each VLQ byte, the bottom 7 bits come from the compressed integer and the 8th bit indicates whether or not the next byte
    from the file is also part of the VLQ.


<a id="orga48220d"></a>

# Prgm chunk

<table border="2" cellspacing="0" cellpadding="6" rules="groups" frame="hsides">


<colgroup>
<col  class="org-left" />

<col  class="org-left" />

<col  class="org-left" />
</colgroup>
<thead>
<tr>
<th scope="col" class="org-left">TYPE</th>
<th scope="col" class="org-left">CONTENTS</th>
<th scope="col" class="org-left">COMMENT</th>
</tr>
</thead>

<tbody>
<tr>
<td class="org-left">tag</td>
<td class="org-left">'prgm'</td>
<td class="org-left">&#xa0;</td>
</tr>


<tr>
<td class="org-left">int</td>
<td class="org-left">chunk size</td>
<td class="org-left">&#xa0;</td>
</tr>


<tr>
<td class="org-left">int</td>
<td class="org-left">prgm number</td>
<td class="org-left">Equals n where this is the n-th prgm chunk in the file. There is one exception to this: in ChariotAttack.amb both the fifth and eigth prgm chunks have number 5.</td>
</tr>


<tr>
<td class="org-left">int</td>
<td class="org-left">flags</td>
<td class="org-left">Bit 0 = random pitch, bit 1 = ?</td>
</tr>


<tr>
<td class="org-left">int</td>
<td class="org-left">max random pitch</td>
<td class="org-left">&#xa0;</td>
</tr>


<tr>
<td class="org-left">signed int</td>
<td class="org-left">min random pitch</td>
<td class="org-left">Often negative</td>
</tr>


<tr>
<td class="org-left">int</td>
<td class="org-left">?</td>
<td class="org-left">&#xa0;</td>
</tr>


<tr>
<td class="org-left">int</td>
<td class="org-left">?</td>
<td class="org-left">&#xa0;</td>
</tr>


<tr>
<td class="org-left">int</td>
<td class="org-left">0xFA</td>
<td class="org-left">Chunk end indicator, except in this case there are two more fields</td>
</tr>


<tr>
<td class="org-left">str+0</td>
<td class="org-left">effect name (?)</td>
<td class="org-left">&#xa0;</td>
</tr>


<tr>
<td class="org-left">str+0</td>
<td class="org-left">var name</td>
<td class="org-left">Matches names in Kmap chunks</td>
</tr>
</tbody>
</table>


<a id="org1b60f5e"></a>

# KmapItem

<table border="2" cellspacing="0" cellpadding="6" rules="groups" frame="hsides">


<colgroup>
<col  class="org-left" />

<col  class="org-left" />

<col  class="org-left" />
</colgroup>
<thead>
<tr>
<th scope="col" class="org-left">TYPE</th>
<th scope="col" class="org-left">CONTENTS</th>
<th scope="col" class="org-left">COMMENT</th>
</tr>
</thead>

<tbody>
<tr>
<td class="org-left">byte[12]</td>
<td class="org-left">[0x7F, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0]</td>
<td class="org-left">Probably 3 4-byte ints: 127, 0, 1.</td>
</tr>


<tr>
<td class="org-left">str+0</td>
<td class="org-left">wav file name</td>
<td class="org-left">&#xa0;</td>
</tr>
</tbody>
</table>


<a id="orgb6b3b9b"></a>

# Kmap chunk

<table border="2" cellspacing="0" cellpadding="6" rules="groups" frame="hsides">


<colgroup>
<col  class="org-left" />

<col  class="org-left" />

<col  class="org-left" />
</colgroup>
<thead>
<tr>
<th scope="col" class="org-left">TYPE</th>
<th scope="col" class="org-left">CONTENTS</th>
<th scope="col" class="org-left">COMMENT</th>
</tr>
</thead>

<tbody>
<tr>
<td class="org-left">tag</td>
<td class="org-left">'kmap'</td>
<td class="org-left">&#xa0;</td>
</tr>


<tr>
<td class="org-left">int</td>
<td class="org-left">chunk size</td>
<td class="org-left">&#xa0;</td>
</tr>


<tr>
<td class="org-left">int</td>
<td class="org-left">2</td>
<td class="org-left">Looks like bit flags</td>
</tr>


<tr>
<td class="org-left">int</td>
<td class="org-left">0</td>
<td class="org-left">&#xa0;</td>
</tr>


<tr>
<td class="org-left">int</td>
<td class="org-left">0</td>
<td class="org-left">&#xa0;</td>
</tr>


<tr>
<td class="org-left">str+0</td>
<td class="org-left">var name</td>
<td class="org-left">Matches name from a Prgm chunk</td>
</tr>


<tr>
<td class="org-left">int</td>
<td class="org-left">item count</td>
<td class="org-left">Number of items in the following array. All Kmap chunks in Civ 3 have 1 item except for 3 of them which have 0.</td>
</tr>


<tr>
<td class="org-left">int</td>
<td class="org-left">12</td>
<td class="org-left">Item data size</td>
</tr>


<tr>
<td class="org-left">KmapItem[]</td>
<td class="org-left">items</td>
<td class="org-left">&#xa0;</td>
</tr>


<tr>
<td class="org-left">int</td>
<td class="org-left">0xFA</td>
<td class="org-left">Chunk end indicator</td>
</tr>
</tbody>
</table>


<a id="org63db5af"></a>

# Glbl chunk

<table border="2" cellspacing="0" cellpadding="6" rules="groups" frame="hsides">


<colgroup>
<col  class="org-left" />

<col  class="org-left" />

<col  class="org-left" />
</colgroup>
<thead>
<tr>
<th scope="col" class="org-left">TYPE</th>
<th scope="col" class="org-left">CONTENTS</th>
<th scope="col" class="org-left">COMMENT</th>
</tr>
</thead>

<tbody>
<tr>
<td class="org-left">tag</td>
<td class="org-left">'glbl'</td>
<td class="org-left">&#xa0;</td>
</tr>


<tr>
<td class="org-left">int</td>
<td class="org-left">chunk size</td>
<td class="org-left">&#xa0;</td>
</tr>


<tr>
<td class="org-left">int</td>
<td class="org-left">12</td>
<td class="org-left">Size of following array</td>
</tr>


<tr>
<td class="org-left">byte[12]</td>
<td class="org-left">[0, 0, 0, 0, 0, 0, 0, 0, 0xCD, 0xCD, 0xCD, 0xCD]</td>
<td class="org-left">&#xa0;</td>
</tr>
</tbody>
</table>


<a id="org79b9b3b"></a>

# InfoTrack

<table border="2" cellspacing="0" cellpadding="6" rules="groups" frame="hsides">


<colgroup>
<col  class="org-left" />

<col  class="org-left" />
</colgroup>
<thead>
<tr>
<th scope="col" class="org-left">TYPE</th>
<th scope="col" class="org-left">COMMENT</th>
</tr>
</thead>

<tbody>
<tr>
<td class="org-left">vlq, TrackName event</td>
<td class="org-left">All info tracks are named "Seq-1"</td>
</tr>


<tr>
<td class="org-left">vlq, SMPTEOffset event</td>
<td class="org-left">Irrelevant as far as I can tell</td>
</tr>


<tr>
<td class="org-left">vlq, TimeSignature event</td>
<td class="org-left">&#xa0;</td>
</tr>


<tr>
<td class="org-left">vlq, SetTempo event</td>
<td class="org-left">Specifies the tempo in microseconds per quarter note</td>
</tr>


<tr>
<td class="org-left">vlq, EndOfTrack event</td>
<td class="org-left">&#xa0;</td>
</tr>
</tbody>
</table>


<a id="org66bed77"></a>

# SoundTrack

<table border="2" cellspacing="0" cellpadding="6" rules="groups" frame="hsides">


<colgroup>
<col  class="org-left" />

<col  class="org-left" />
</colgroup>
<thead>
<tr>
<th scope="col" class="org-left">TYPE</th>
<th scope="col" class="org-left">COMMENT</th>
</tr>
</thead>

<tbody>
<tr>
<td class="org-left">vlq, TrackName event</td>
<td class="org-left">&#xa0;</td>
</tr>


<tr>
<td class="org-left">(vlq, ControlChange event)[]</td>
<td class="org-left">Array length is either 1 or 2</td>
</tr>


<tr>
<td class="org-left">vlq, ProgramChange event</td>
<td class="org-left">&#xa0;</td>
</tr>


<tr>
<td class="org-left">vlq, NoteOn event</td>
<td class="org-left">&#xa0;</td>
</tr>


<tr>
<td class="org-left">vlq, NoteOff event</td>
<td class="org-left">&#xa0;</td>
</tr>


<tr>
<td class="org-left">vlq, EndOfTrack event</td>
<td class="org-left">&#xa0;</td>
</tr>
</tbody>
</table>


<a id="org9836c50"></a>

# Embedded Midi

<table border="2" cellspacing="0" cellpadding="6" rules="groups" frame="hsides">


<colgroup>
<col  class="org-left" />

<col  class="org-left" />

<col  class="org-left" />
</colgroup>
<thead>
<tr>
<th scope="col" class="org-left">TYPE</th>
<th scope="col" class="org-left">CONTENTS</th>
<th scope="col" class="org-left">COMMENT</th>
</tr>
</thead>

<tbody>
<tr>
<td class="org-left">tag</td>
<td class="org-left">'MThd'</td>
<td class="org-left">&#xa0;</td>
</tr>


<tr>
<td class="org-left">int</td>
<td class="org-left">6</td>
<td class="org-left">Header size</td>
</tr>


<tr>
<td class="org-left">short</td>
<td class="org-left">1</td>
<td class="org-left">Midi format</td>
</tr>


<tr>
<td class="org-left">short</td>
<td class="org-left">track count</td>
<td class="org-left">Always &gt;= 2 and &lt;= 13</td>
</tr>


<tr>
<td class="org-left">short</td>
<td class="org-left">ticks per quarter note</td>
<td class="org-left">"Division" in the Midi spec. All AMBs in Civ 3 use "metric time", i.e., this field specifies the length of a quarter note in delta time ticks</td>
</tr>


<tr>
<td class="org-left">InfoTrack</td>
<td class="org-left">info track</td>
<td class="org-left">First track contains no sound data, just info about the tempo</td>
</tr>


<tr>
<td class="org-left">SoundTrack[]</td>
<td class="org-left">sound tracks</td>
<td class="org-left">Array length = track count - 1</td>
</tr>
</tbody>
</table>

