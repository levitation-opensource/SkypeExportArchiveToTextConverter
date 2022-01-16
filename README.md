### Skype export archive to text converter

Scrolling the Skype chats is painfully slow. There is no way to annotate or bookmark text in the chats for future reference. And searching over multiple chats is impossible as well. It would be much more convenient to have the Skype chat histories available as text files. This enables quick scrolling and search. If annotation or bookmarking is needed, you can further copy these text files to Google Docs, for example.

This software utility extracts chat logs into a human readable text format from Skype export archives.
<br>You can request a machine-readable archive export of your Skype chats from here: https://secure.skype.com/en/data-export
<br>After downloading the archive, provide the filename of that archive to this utility in the form indicated below in order to obtain the chat log files in text format.

### Usage:

To extract a chat log with one particular user:
<br>python SkypeExportToText.py "username" "C:\path\to\export.tar"
<br>or
<br>python SkypeExportToText.py "username" "C:\path\to\messages.json"

To extract chat logs with all users (note the empty quotes here):
<br>python SkypeExportToText.py "" "C:\path\to\export.tar"
<br>or
<br>python SkypeExportToText.py "" "C:\path\to\messages.json"

The extracted chat logs are saved into a subfolder named "chats". The subfolder will be created where the Python script is located.
<br>Each Skype chat or group chat log is saved into a separate file.
<br>If there are previously existing files with same names then these colliding old files will be backed up with names in the form "chat username.txt.old".


A Python 3 installation is required. There are no package dependencies for this software.


### Licence
Version 1.0.5
<br>Copyright: Roland Pihlakas, 2022, roland@simplify.ee
<br>Licence: LGPL 2.1
<br>You can obtain a copy of this free software from https://github.com/levitation-opensource/SkypeExportArchiveToTextConverter/

### State
Ready to use. Maintained and in active use.

### Alternative software
Alternative software for parsing Skype export achives:
<br>https://go.skype.com/skype-parser (it does not generate text files and does less comprehensive parsing of the messages)
<br>https://jimmysie.com/2021/08/13/saving-skype-media-files-from-exported-archive/ (for exporting media files into a more useful file structure)

Note. The archive exported from Skype webpage will contain Skype chats starting from somewhere in the middle of year 2017.
<br>For exporting archives of older Skype chats there are various alternative software available. For example:
<br>https://suurjaak.github.io/Skyperious/
<br>https://www.nirsoft.net/utils/skype_log_view.html
<br>https://www.bitrecover.com/free/skype-chat-viewer/


<br>
<br>
<br>
<br>

[![Analytics](https://ga-beacon.appspot.com/UA-351728-28/SkypeExportArchiveToTextConverter/README.md?pixel)](https://github.com/igrigorik/ga-beacon)    
