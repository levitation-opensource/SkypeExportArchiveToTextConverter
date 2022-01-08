# -*- coding: utf-8 -*-

#
# Author: Roland Pihlakas, 2022
#
# roland@simplify.ee
#
# Version 1.0.5
# 


import os
import sys
import time
import datetime
import json
import tarfile
import html
import re
import codecs



BOM = codecs.BOM_UTF8


def safeprint(text):

  text = str(text).encode('utf8', 'ignore').decode('ascii', 'ignore')
  print(text)

#/ def safeprint(text):


def get_now_str():

  now_str = datetime.datetime.strftime(datetime.datetime.now(), '%m.%d %H:%M:%S')
  return now_str

#/ def get_now_str():


# https://stackoverflow.com/questions/5849800/tic-toc-functions-analog-in-python
class Timer(object):

  def __init__(self, name=None, quiet=False):
    self.name = name
    self.quiet = quiet

  def __enter__(self):

    if not self.quiet and self.name:
      safeprint(get_now_str() + " : " + self.name + " ...")

    self.tstart = time.time()

  def __exit__(self, type, value, traceback):

    elapsed = time.time() - self.tstart

    if not self.quiet:
      if self.name:
        safeprint(get_now_str() + " : " + self.name + " totaltime: {}".format(elapsed))
      else:
        safeprint(get_now_str() + " : " + "totaltime: {}".format(elapsed))
    #/ if not quiet:

#/ class Timer(object):


def rename_temp_file(filename, make_backup = False):  # NB! make_backup is false by default since this operation would not be atomic

  max_tries = 20
  try_index = 1
  while True:

    try:

      if make_backup and os.path.exists(filename):

        if os.name == 'nt':   # rename is not atomic on windows and is unable to overwrite existing file. On UNIX there is no such problem
          if os.path.exists(filename + ".old"):
            if not os.path.isfile(filename + ".old"):
              raise ValueError("" + filename + ".old" + " is not a file")
            os.remove(filename + ".old")

        os.rename(filename, filename + ".old")

      #/ if make_backup and os.path.exists(filename):


      if os.name == 'nt':   # rename is not atomic on windows and is unable to overwrite existing file. On UNIX there is no such problem
        if os.path.exists(filename):
          if not os.path.isfile(filename):
            raise ValueError("" + filename + " is not a file")
          os.remove(filename)

      os.rename(filename + ".tmp", filename)

      return

    except Exception as ex:

      if try_index >= max_tries:
        raise

      try_index += 1
      safeprint("retrying temp file rename: " + filename)
      time.sleep(5)
      continue

    #/ try:

  #/ while True:

#/ def rename_temp_file(filename):


def read_json(jsonfilename, tarfilename=None, default_data = {}, quiet = False):

  if tarfilename:
    if not os.path.exists(tarfilename):
      return default_data
  else:
    if not os.path.exists(jsonfilename):
      return default_data

  with Timer("file reading : " + jsonfilename + ((" from " + tarfilename) if tarfilename else ""), quiet):

    try:

      if tarfilename:

        with tarfile.open(name=tarfilename, mode="r:", bufsize=1024 * 1024) as tar_handle:
          try:
            with tar_handle.extractfile(jsonfilename) as fh: 
              raw_data = fh.read()
              data = json.loads(raw_data.decode("utf-8", "ignore"))
          except KeyError:   # file not in tar?
            data = default_data

        #/ with tarfile.open(name=tarfilename, mode="r:", bufsize=1024 * 1024) as tar_handle:

      else:   #/ if tarfilename:

        with open(jsonfilename, 'rb', 1024 * 1024) as fh:
          raw_data = fh.read()
          data = json.loads(raw_data.decode("utf-8", "ignore"))
      
      #/ if tarfilename:

    except FileNotFoundError:

      data = default_data

  #/ with Timer("file reading : " + jsonfilename):

  return data

#/ def read_json(jsonfilename, tarfilename=None, default_data = {}, quiet = False):


def save_txt(filename, str, quiet = False, make_backup = False):

  message_template = "file saving {} num of characters: {}"
  message = message_template.format(filename, len(str))

  with Timer(message, quiet):

    with open(filename + ".tmp", 'wt', 1024 * 1024, encoding="utf-8") as fh:    # wt format automatically handles line breaks depending on the current OS type
      # fh.write(BOM + str.encode("utf-8", "ignore"))
      fh.write(BOM.decode("utf-8"))
      fh.write(str)
      fh.flush()  # just in case

    rename_temp_file(filename, make_backup)

  #/ with Timer("file saving {}, num of all entries: {}".format(filename, len(cache))):

#/ def save_txt(filename, data):


last_success_iso_time_parse_format_index = 0
iso_time_formats = [
  "%Y-%m-%dT%H:%M:%S.%fZ",
  "%Y-%m-%dT%H:%M:%SZ"
]

# this function assumes that the time ends with Z, so not entire ISO format is supported, but only the particular format used by Skype export
def parse_iso_time(str):
  global last_success_iso_time_parse_format_index

  # https://stackoverflow.com/questions/12281975/convert-timestamps-with-offset-to-datetime-obj-using-strptime

  result = None

  try:

    result = datetime.datetime.strptime(str, iso_time_formats[last_success_iso_time_parse_format_index])

  except ValueError:

    for index, format in enumerate(iso_time_formats):
      if index == last_success_iso_time_parse_format_index:  # already tried that above
        continue

      try:
        result = datetime.datetime.strptime(str, format)
        last_success_iso_time_parse_format_index = index
        break
      except ValueError:
        continue
    #/ for format in formats:

    if result is None:
      raise

  #/ except ValueError:

  return result

#/ def parse_iso_time(str):


def parse_skype_username(username):

  result = username.split(":", 1)[1]   # split(): remove the prefix "8:"
  return result

#/ def parse_skype_username(username):


def parse_skype_times(message):

  time = parse_iso_time(message["originalarrivaltime"])

  edittime = None
  deletetime = None
  isserversidegenerated = False

  properties = message.get("properties")
  if properties:    # NB! the field might exist but be null

    edittime = properties.get("edittime")
    if edittime:
      edittime = datetime.datetime.fromtimestamp(int(edittime) / 1000)

    deletetime = properties.get("deletetime")
    if deletetime:
      deletetime = datetime.datetime.fromtimestamp(int(deletetime) / 1000)

    isserversidegenerated = properties.get("isserversidegenerated")
    if isserversidegenerated:
      isserversidegenerated = bool(isserversidegenerated)

  #/ if properties:

  message["time"] = time
  message["edittime"] = edittime
  message["deletetime"] = deletetime
  message["isserversidegenerated"] = isserversidegenerated

  return message

#/ def parse_skype_times(message):


def convert_timezone(time):

  # TODO: consider summer times
  result = time.replace(tzinfo=datetime.timezone.utc).astimezone(output_timezone)
  return result

#/ def convert_timezone(time):


tag_re = re.compile(r"<.*?>", re.DOTALL)
space_re = re.compile(r"[ ]+", re.DOTALL)

def remove_tags(text):

  text = re.sub(tag_re, " ", text)    # NB! replace tags by spaces not empty strings since they may separate words
  text = re.sub(space_re, " ", text)
  result = text.strip()

  return result

#/ def remove_tags(text):


# convert numeric timestamps inside legacy quotes into human readable format
# "<quote author=\"roland\" authorname=\"Roland Pihlakas\" timestamp=\"1600529710\" conversation=\"8:roland\" messageid=\"...\" cuid=\"...\"><legacyquote>[1600529710] Roland Pihlakas: </legacyquote>..."
def skype_legacyquote_replacer(matches):

  timestamp = matches.group(1)
  quotee = matches.group(2)
  
  try:
    timestamp = datetime.datetime.fromtimestamp(int(timestamp))   # NB! no division by 1000 here
    timestamp = datetime.datetime.strftime(convert_timezone(timestamp), output_time_format)
  except ValueError:  # non-numeric timestamp: '<legacyquote>[12:35:59] sys: </legacyquote>'
    pass

  result = "/ Quoting " + timestamp + "" + quotee + "/ "
  return result

#/ def skype_legacyquote_replacer(matches):


name_tag_re = re.compile(r"<name>(.*?)</name>", re.DOTALL)
initiator_tag_re = re.compile(r"<initiator>(.*?)</initiator>", re.DOTALL)
target_tag_re = re.compile(r"<target>(.*?)</target>", re.DOTALL)
id_tag_re = re.compile(r"<id>(.*?)</id>", re.DOTALL)
value_tag_re = re.compile(r"<value>(.*?)</value>", re.DOTALL)
legacyquote_tag_re = re.compile(r"<legacyquote>\[(.*?)\](.*?)</legacyquote>", re.DOTALL)
role_tag_re = re.compile(r"<role>(.*?)</role>", re.DOTALL)

call_event_type_re = re.compile(r'<partlist .*?type="(.*?)"', re.DOTALL)
subject_re = re.compile(r'<URIObject .*?subject="(.*?)">', re.DOTALL)
contacts_re = re.compile(r'<c .*?s="(.*?)" .*?f="(.*?)".*?(/>|></c>)', re.DOTALL)
a_href_re = re.compile(r'<a .*?href="(.*?)".*?>', re.DOTALL)
originalname_re = re.compile(r'<OriginalName .*?v="(.*?)".*?(/>|></OriginalName>)', re.DOTALL)


prev_content = None
prev_joiningenabled = True
prev_historydisclosed = True


def reset_conversation_state():
  global prev_content, prev_joiningenabled, prev_historydisclosed

  prev_content = None
  prev_joiningenabled = True
  prev_historydisclosed = True

#/ def reset_conversation_state():


def format_skype_message(message):
  global prev_content, prev_joiningenabled, prev_historydisclosed


  try:

    username = parse_skype_username(message["from"])
    displayname = message["displayName"]
    id = message["id"]
 
    if displayname:   # may be null
      displayname = html.unescape(remove_tags(message["displayName"]))
      name = displayname + " (" + username + ")"
    else:
      name = "(" + username + ")"


    time = datetime.datetime.strftime(convert_timezone(message["time"]), output_time_format)

    edittime = message["edittime"]
    if edittime:
      edittime = datetime.datetime.strftime(convert_timezone(edittime), output_time_format)

    deletetime = message["deletetime"]
    if deletetime:
      return ""


    content = message["content"]

    isserversidegenerated = message["isserversidegenerated"]
    if isserversidegenerated and not content:
      return ""

    if isserversidegenerated and prev_content == content:   # edited messages will be duplicated by the server for some reason
      return ""

    prev_content = content
   
    #if not content:
    #  content = "/message id " + str(id) + "/"


    # re-format the content
    messagetype = message["messagetype"]

    if (messagetype == "RichText" 
        or messagetype == "InviteFreeRelationshipChanged/Initialized"
      ):

      content = re.sub(legacyquote_tag_re, skype_legacyquote_replacer, content)
      content = html.unescape(remove_tags(content))

    elif (messagetype == "RichText/UriObject"
        or messagetype == "RichText/Media_FlikMsg"
        or messagetype == "RichText/Media_GenericFile"
        or messagetype == "RichText/Media_Video"
        or messagetype == "RichText/Media_Card"
      ):

      mesagetype_dict = {
        "RichText/UriObject": "Link",
        "RichText/Media_FlikMsg": "Animation",
        "RichText/Media_GenericFile": "File",
        "RichText/Media_Video": "Video",
        "RichText/Media_Card": "Card",
      }
      message_description = mesagetype_dict[messagetype]

      links = re.findall(a_href_re, content)    # TODO: the links present in Skype export file seem to be invalid, so perhaps no point in showing them in the chat log?
      links = ", ".join([html.unescape(link) for link in links])

      originalnames = re.findall(originalname_re, content)
      originalnames = ", ".join([html.unescape(name[0]) for name in originalnames])
      if originalnames != "" and messagetype == "RichText/Media_Card":
        qqq = True    # for debugging

      content = html.unescape(remove_tags(content))
      content = "/ " + message_description + ": " + originalnames + (" " + links if links not in content else "") + " / " + content

    elif messagetype == "Text":   # raw text/code

      pass  # no conversion needed and allowed here

    elif messagetype == "RichText/Files":

      num_files = content.count("<file ")

      content = html.unescape(remove_tags(content)).strip()   # strip(): there is a newline in this message for some reason

      content = "/ Sent file" + ("s" if num_files > 1 else "") + ": / " + content

    elif (messagetype == "RichText/Media_CallRecording"
          or messagetype == "RichText/Media_AudioMsg"
          or messagetype == "RichText/Location"
        ):

      mesagetype_dict = {
        "RichText/Media_CallRecording": "Call recording link",
        "RichText/Media_AudioMsg": "Voicemail link",
        "RichText/Location": "Location",
      }
      message_description = mesagetype_dict[messagetype]

      links = re.findall(a_href_re, content)
      links = ", ".join([html.unescape(link) for link in links])

      content = html.unescape(remove_tags(content)).strip()
      content = "/ " + message_description + (": " + links if links not in content else "") + " / " + content

    elif messagetype == "Event/Call":

      # TODO: extract call duration on call type="ended" event

      event_type = re.findall(call_event_type_re, content)[0]
      names = re.findall(name_tag_re, content)
      names = ", ".join([html.unescape(remove_tags(name)) for name in names])
      content = "/ Call " + event_type + ": " + names + " /"

    elif messagetype == "RichText/ScheduledCallInvite":

      subjects = re.findall(subject_re, content)
      subjects = ", ".join([html.unescape(subject) for subject in subjects])

      content = "/ Call invitation. Subject: '" + subjects + "' / " + html.unescape(remove_tags(content))

    elif messagetype == "ThreadActivity/AddMember":

      target_names_list = re.findall(target_tag_re, content)
      target_names = ", ".join([parse_skype_username(name) for name in target_names_list])

      initiator_names_list = re.findall(initiator_tag_re, content)
      initiator_names = ", ".join([parse_skype_username(name) for name in initiator_names_list])

      if initiator_names == target_names or not initiator_names:
        content = "/ Group member has joined: " + target_names + " /"
      elif len(target_names_list) > 1:
        content = "/ Group members " + target_names + " have been added by " + initiator_names + " /"
      else:
        content = "/ Group member " + target_names + " has been added by " + initiator_names + " /"

    elif messagetype == "ThreadActivity/DeleteMember":

      target_names_list = re.findall(target_tag_re, content)
      target_names = ", ".join([parse_skype_username(name) for name in target_names_list])

      initiator_names_list = re.findall(initiator_tag_re, content)
      initiator_names = ", ".join([parse_skype_username(name) for name in initiator_names_list])

      if initiator_names == target_names or not initiator_names:
        content = "/ Group member has left: " + target_names + " /"
      elif len(target_names_list) > 1:
        content = "/ Group members " + target_names + " have been removed by " + initiator_names + " /"
      else:
        content = "/ Group member " + target_names + " has been removed by " + initiator_names + " /"

    elif messagetype == "ThreadActivity/TopicUpdate":

      values_list = re.findall(value_tag_re, content)
      values = ", ".join([html.unescape(remove_tags(value)) for value in values_list])

      initiator_names_list = re.findall(initiator_tag_re, content)
      initiator_names = ", ".join([parse_skype_username(name) for name in initiator_names_list])

      content = "/ The group topic has been set to '" + values + "' by " + initiator_names + " /"

    elif messagetype == "ThreadActivity/E2EEHandshakeInvite":

      target_names_list = re.findall(target_tag_re, content)
      target_names = ", ".join([parse_skype_username(name) for name in target_names_list])

      initiator_names_list = re.findall(initiator_tag_re, content)
      initiator_names = ", ".join([parse_skype_username(name) for name in initiator_names_list])

      content = "/ User " + target_names + " has been invited to encrypted conversation by " + initiator_names + " /"

    elif (messagetype == "ThreadActivity/E2EEHandshakeAccept" 
        or messagetype == "ThreadActivity/E2EEHandshakeComplete"    # one of these messages could probably be ignored since they duplicate each other
      ):

      target_names_list = re.findall(target_tag_re, content)
      target_names = ", ".join([parse_skype_username(name) for name in target_names_list])

      initiator_names_list = re.findall(initiator_tag_re, content)
      initiator_names = ", ".join([parse_skype_username(name) for name in initiator_names_list])

      content = "/ User " + target_names + " has accepted encrypted conversation invitation by " + initiator_names + " /"

    elif (messagetype == "ThreadActivity/E2EEHandshakeReject"
      ):

      target_names_list = re.findall(target_tag_re, content)
      target_names = ", ".join([parse_skype_username(name) for name in target_names_list])

      initiator_names_list = re.findall(initiator_tag_re, content)
      initiator_names = ", ".join([parse_skype_username(name) for name in initiator_names_list])

      content = "/ User " + target_names + " has rejected encrypted conversation invitation by " + initiator_names + " /"

    elif messagetype == "RichText/Contacts":

      parts = re.findall(contacts_re, content)
      if len(parts) == 0:
        qqq = True    # for debugging
      names = [(html.unescape(x[1]) + " (" + x[0] + ")").strip() for x in parts]
      names = ", ".join(names)

      content = "/ Contacts: " + names + " /"

    elif messagetype == "ThreadActivity/PictureUpdate":

      initiator_names_list = re.findall(initiator_tag_re, content)
      initiator_names = ", ".join([parse_skype_username(name) for name in initiator_names_list])

      content = "/ User " + initiator_names + " has changed their profile picture /"  # TODO: add filename?

    elif messagetype == "EndToEndEncryption/EncryptedText":

      content = "/ Encrypted message /"

    elif messagetype == "EndToEndEncryption/EncryptedMedia":

      content = "/ Encrypted media /"

    elif messagetype == "RichText/Media_Album":

      content = "/ Media album /" # there does not seem to be any detail info in this message besides the albumId

    elif messagetype == "Notice":  # TODO: aggregate this message with the actual user log. Currently it is under Skype concierge account log

      try:

        content2 = json.loads(content)[0]["attachments"][0]["content"]
    
        text = content2["text"]
        action_uri = content2["buttons"][0]["actionUri"]
        title = content2["buttons"][0]["title"]

        content = "/ Notice / " + text + " " + action_uri + " " + title

      except Exception: # except (KeyError, IndexError, json.decoder.JSONDecodeError):

        try:

          content2 = json.loads(content)[0]["attachments"][0]["content"]  # parse again since it might be that the exception was raised already here and then we want to catch that to ensure that no stale values of content2 variable are being used
    
          title = content2["title"]
          action_uri = content2["mainActionUri"]
          text = content2["text"]

          content = "/ Notice / " + title + " " + action_uri + " " + text # the changed order of title and text is on purpose here

        except Exception: # except (KeyError, IndexError, json.decoder.JSONDecodeError):

          content = "/ Notice: " + content + " /"

      #/ except (KeyError, IndexError, json.decoder.JSONDecodeError):

    elif messagetype == "PopCard":  # TODO: aggregate this message with the actual user log. Currently it is under Skype concierge account log

      try:

        content2 = json.loads(content)[0]["content"]
    
        title1 = content2["title"]
        action_uri = content2["buttons"][0]["actionUri"]
        title2 = content2["buttons"][0]["title"]
        media_url = content2["media"]["url"]

        content = "/ PopCard / " + title1 + " " + action_uri + " " + media_url + " " + title2

      except Exception: # except (KeyError, IndexError, json.decoder.JSONDecodeError):

        links = re.findall(a_href_re, content)
        links = ", ".join([html.unescape(link) for link in links])

        originalnames = re.findall(originalname_re, content)
        originalnames = ", ".join([html.unescape(name[0]) for name in originalnames])

        content = html.unescape(remove_tags(content))
        content = "/ PopCard: " + originalnames + (" " + links if links not in content else "") + " / " + content

    elif messagetype == "ThreadActivity/HistoryDisclosedUpdate":

      values_list = re.findall(value_tag_re, content)
      values = ", ".join([html.unescape(remove_tags(value)) for value in values_list])

      initiator_names_list = re.findall(initiator_tag_re, content)
      initiator_names = ", ".join([parse_skype_username(name) for name in initiator_names_list])

      if values.upper() == "TRUE":
        if not prev_historydisclosed:
          content = "/ History disclosed by " + initiator_names + " /"
        else:
          content = ""
        prev_historydisclosed = True
      elif values.upper() == "FALSE":
        if prev_historydisclosed:
          content = "/ History hidden by " + initiator_names + " /"
        else:
          content = ""
        prev_historydisclosed = False
      else:
        content = ""

    elif messagetype == "ThreadActivity/JoiningEnabledUpdate":

      values_list = re.findall(value_tag_re, content)
      values = ", ".join([html.unescape(remove_tags(value)) for value in values_list])

      initiator_names_list = re.findall(initiator_tag_re, content)
      initiator_names = ", ".join([parse_skype_username(name) for name in initiator_names_list])

      if values.upper() == "TRUE":
        if not prev_joiningenabled:
          content = "/ Joining enabled by " + initiator_names + " /"
        else:
          content = ""
        prev_joiningenabled = True
      elif values.upper() == "FALSE":
        if prev_joiningenabled:
          content = "/ Joining disabled by " + initiator_names + " /"
        else:
          content = ""
        prev_joiningenabled = False
      else:
        content = ""

    elif messagetype == "ThreadActivity/RoleUpdate":

      target_names_list = re.findall(id_tag_re, content)   # note, here target-id tag combination is being used, not just target
      target_names = ", ".join([parse_skype_username(name) for name in target_names_list])

      initiator_names_list = re.findall(initiator_tag_re, content)
      initiator_names = ", ".join([parse_skype_username(name) for name in initiator_names_list])

      roles_list = re.findall(role_tag_re, content)
      roles = ", ".join([html.unescape(remove_tags(role)) for role in roles_list])

      if target_names == initiator_names and roles == "user":
        content = ""     # usually this message does not seem to be worth of logging  # TODO: detect situations where the previous role was "admin" or something else "non-user"
      else:
        # TODO: is there need to list roles of each user separately - could the users have different roles per message? The message format indeed allows that, but is this used in practice?
        content = "/ Rule of user " + target_names + " updated to role '" + roles + "' by " + initiator_names + " /"

    else:

      content = "/ Unknown message type '" + messagetype + "' : " + content + " /"

    #/ if messagetype == ...

  except KeyboardInterrupt:   # still handle Ctrl+C

    raise

  except Exception:

    safeprint("Error processing a message" + str(message))
    content = "/ Error processing a message /" + str(message)


  text = "%s %s%s :\n%s" % (name, time, (" - " + edittime if edittime else ""), content)
  return text

#/ def format_skype_message(message):


def export_chat(data, username, output_filename):
  global prev_joiningenabled


  safeprint("Working on username: " + username)

  try:

    output_folder = os.path.dirname(output_filename)
    if not os.path.exists(output_folder):
      os.makedirs(output_folder)


    conversations = data["conversations"]
    selected_conversations = [conv for conv in conversations if parse_skype_username(conv["id"]) == username]
    if len(selected_conversations) == 0:
      safeprint("No conversations with username '%s' found" % username)
      sys.exit()

    selected_conversation = selected_conversations[0]["MessageList"]   # assume that there is one conversation per user in Skype history


    with Timer("Parsing message times"):
      for message in selected_conversation:
        parse_skype_times(message)

    with Timer("Sorting", quiet=True):
      selected_conversation.sort(key=lambda message: message["time"])    # the messages in Skype export are in reversed order

    with Timer("Formatting messages"):
      reset_conversation_state()
      rows = [format_skype_message(message) for message in selected_conversation]

    text = "\n\n".join([row for row in rows if row != ""]) + "\n"    # skip empty rows that represent deleted messages
    save_txt(output_filename, text, quiet=True, make_backup=True)

  except KeyboardInterrupt:   # still handle Ctrl+C

    raise

  except Exception:

    safeprint("Error in processing thread with " + username)


#/ def export_chat(data, username):


# https://stackoverflow.com/questions/7406102/create-sane-safe-filename-from-any-unsafe-string
# device names, '.', and '..' are invalid filenames in Windows.
device_names = set("CON,PRN,AUX,NUL,COM1,COM2,COM3,COM4," \
                "COM5,COM6,COM7,COM8,COM9,LPT1,LPT2," \
                "LPT3,LPT4,LPT5,LPT6,LPT7,LPT8,LPT9," \
                "CONIN$,CONOUT$,..,.".split())

def sanitise_filename(text, max_len=255, keep_ext=True, replace_device_names=True, check_filename_start_and_end=True):   # 255: # Maximum length of filename is 255 bytes in Windows and some *nix flavors.
  
  if keep_ext:
    ext = os.path.splitext(text)[1]

  filler = "_"

  # remove excluded characters.
  blacklist = set(chr(127) + r'<>:"/\|?*')   # 127 is unprintable, the rest are illegal in Windows.
  keepcharacters = { chr(x) for x in range(32, 256) } - blacklist    # 0-32, 127 are unprintable
  result = "".join([(chr if (chr.isalnum() or chr in keepcharacters) else filler) for chr in text])

  if replace_device_names:
    if result in device_names:
      result = filler + result
  #/ if replace_device_names:

  # truncate long files while preserving the file extension.
  if keep_ext:
    result = result[:max_len - len(ext)] + ext
  else:
    result = result[:max_len]

  if check_filename_start_and_end:
    # Windows does not allow filenames to begin with " " or end with "." or " ".
    result = re.sub(r"(^ |[. ]$)", filler, result)

  return result

#/ def sanitise_filename(text):


username_counts = {}
def get_output_filename(username):

  reserve_len = len("chat " + " (1234)" + ".txt" + ".old")
  username = sanitise_filename(username, max_len=255-reserve_len, keep_ext=False, replace_device_names=False, check_filename_start_and_end=False)


  result = "chat " + username  # prepend "chat" prefix to avoid stumbling on reserved filenames like con.txt etc


  username_count = username_counts.get(username, 0) + 1
  username_counts[username] = username_count

  if username_count > 1:    # handle filename collisions caused by filename sanitisation
    result += " (" + str(username_count) + ")"


  result = r"chats\\" + result + ".txt"
  return result

#/ def get_output_filename(username):


# config

# first argument is the python script name
username = sys.argv[1] if len(sys.argv) >= 2 else ""
input_file = sys.argv[2] if len(sys.argv) >= 3 else ""

if input_file == "": 

  safeprint('')
  safeprint('')
  safeprint('This software utility extracts chat logs into a human readable text format from Skype export archives.')
  safeprint('You can request a machine-readable archive export of your Skype chats from here: https://secure.skype.com/en/data-export')
  safeprint('After downloading the archive, provide the filename of that archive to this utility in the form indicated below in order to obtain the chat log files in text format.')
  safeprint('')
  safeprint('Usage:')
  safeprint('')
  safeprint('To extract a chat log with one particular user:')
  safeprint(r'python SkypeExportToText.py "username" "C:\path\to\export.tar"')
  safeprint('or')
  safeprint(r'python SkypeExportToText.py "username" "C:\path\to\messages.json"')
  safeprint('')
  safeprint('To extract chat logs with all users (note the empty quotes here):')
  safeprint(r'python SkypeExportToText.py "" "C:\path\to\export.tar"')
  safeprint('or')
  safeprint(r'python SkypeExportToText.py "" "C:\path\to\messages.json"')
  safeprint('')
  safeprint('The extracted chat logs are saved into a subfolder named "chats". The subfolder will be created where the Python script is located.') 
  safeprint('Each Skype chat or group chat log is saved into a separate file.')   # TODO: name group chat files also in human-readable form
  safeprint('If there are previously existing files with same names then these colliding old files will be backed up with names in the form "chat username.txt.old".')
  safeprint('')
  safeprint('')
  safeprint('A Python 3 installation is required. There are no package dependencies for this software.')
  safeprint('')
  safeprint('')
  safeprint('Version 1.0.5')
  safeprint('Copyright: Roland Pihlakas, 2022, roland@simplify.ee')
  safeprint('Licence: LGPL 2.1')
  safeprint('You can obtain a copy of this free software from https://github.com/levitation-opensource/SkypeExportArchiveToTextConverter/')
  safeprint('')
  safeprint('')
  safeprint('Alternative software for parsing Skype export achives:')
  safeprint('https://go.skype.com/skype-parser (it does not generate text files and does less comprehensive parsing of the messages)')
  safeprint('')
  safeprint('')
  safeprint('Note. The archive exported from Skype webpage will contain Skype chats starting from somewhere in the middle of year 2017.')
  safeprint('For exporting archives of older Skype chats there are various alternative software available. For example:') 
  safeprint('https://suurjaak.github.io/Skyperious/')
  safeprint('https://www.nirsoft.net/utils/skype_log_view.html')
  safeprint('https://www.bitrecover.com/free/skype-chat-viewer/')
  safeprint('')
  safeprint('')

  sys.exit()

#/ if len(sys.argv) < 3:


output_time_format = r"%Y.%m.%d %H:%M:%S %Z"
# output_timezone = datetime.timezone(datetime.timedelta(hours=2))  # NB! this will not consider summer times
output_timezone = datetime.timezone.utc


# main script

os.chdir(os.path.dirname(os.path.realpath(__file__)))

safeprint("Input file: " + input_file)


ext = os.path.splitext(input_file)[1]
if ext == ".tar":
  data = read_json("messages.json", tarfilename=input_file)
elif ext == ".json":
  data = read_json(input_file)
else:
  safeprint("Unknown file format")
  sys.exit()


if username:
  usernames = [username]
else:   # all chats
  conversations = data["conversations"]
  usernames = list(set([parse_skype_username(conv["id"]) for conv in conversations]))
  usernames.sort()  # make the colliding chat log filenames deterministic. It appears that the order of usernames in input data is changing


for index, username in enumerate(usernames):
  output_filename = get_output_filename(username)
  export_chat(data, username, output_filename)
  safeprint("Progress: %s / %s" % (index + 1, len(usernames)))


safeprint("")
safeprint("DONE")
sys.exit()


