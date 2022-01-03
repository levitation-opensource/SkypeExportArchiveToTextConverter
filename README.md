# SkypeExportArchiveToTextConverter

This software utility extracts chat logs into a human readable text format from Skype export archives.
You can request a machine-readable archive export of your Skype chats from here: https://secure.skype.com/en/data-export
After downloading the archive, provide the filename of that archive to this utility in the form indicated below.

Usage:

To extract a chat log with one particular user:
python SkypeExportToText.py "username" "export.tar"
or
python SkypeExportToText.py "username" "messages.json"

To extract chat logs with all users (note the empty quotes here):
python SkypeExportToText.py "" "export.tar"
or
python SkypeExportToText.py "" "messages.json"

The extracted chat logs are saved into a subfolder named "chats".
Each Skype chat or group chat log is saved into a separate file.
If there are previously existing files with same names then these colliding old files will be backed up with names in the form "chat username.txt.old".


Copyright: Roland Pihlakas, 2022, roland@simplify.ee
License: LGPL 2.1
You can obtain a copy of this free software from https://github.com/levitation-opensource/


Note. The archive exported from Skype webpage will contain Skype chats starting from somewhere in the middle of year 2017.
For exporting archives of older Skype chats there are various alternative software available. For example:
https://suurjaak.github.io/Skyperious/
https://www.nirsoft.net/utils/skype_log_view.html
https://www.bitrecover.com/free/skype-chat-viewer/
