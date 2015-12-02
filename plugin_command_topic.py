#
#  This file is part of Magnet2.
#  Copyright (c) 2011  Grom PE
#
#  Magnet2 is free software: you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation, either version 3 of the License, or     
#  (at your option) any later version.                                   
#
#  Magnet2 is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with Magnet2.  If not, see <http://www.gnu.org/licenses/>.
#
import xmpp, random, time
from magnet_api import *
from magnet_utils import *

topic_db = {}

def gettopic(bot, room, number):
  if not room in topic_db: return
  if number > len(topic_db[room]) or number < 1: return
  return topic_db[room][number-1]

def addtopic(bot, room, topicdic):
  if not room in topic_db: topic_db[room] = []
  if topicdic:
    topic_db[room].append(topicdic)

def deltopic(bot, room, number):
  if not room in topic_db: return
  if number > len(topic_db[room]) or number < 1: return
  del topic_db[room][number-1]

def command_topic(bot, room, nick, access_level, parameters, message):
  if not room in topic_db or len(topic_db[room]) == 0:
    return 'No topics added yet!'
  if not parameters:
    number = random.randint(1, len(topic_db[room]))
  else:
    try:
      number = int(parameters)
    except:
      search = parameters.lower()
      found = []
      for i in xrange(len(topic_db[room])):
        if search in topic_db[room][i]['topic'].lower():
          found.append(i)
      if len(found) == 0:
        return "No such text found in topics."
      elif len(found) == 1:
        number = found[0]+1
      else:
        return "Text found in topics %s."%(', '.join(['#%d'%(x+1) for x in found]))

  existent_topic = gettopic(bot, room, number)
  if not existent_topic:
    return "There's no topic #%d, and there are %d topics."%(number, len(topic_db[room]))

  res = 'Topic #%d: %s'%(number, existent_topic['topic'])
  bot.client.send(xmpp.Message(room, None, 'groupchat', res))
  if message.getType() != 'groupchat' and access_level >= LEVEL_ADMIN:
    t = timeformat(time.time()-existent_topic['time'])
    res = '%s\n(added by %s %s ago)'%(res, existent_topic['jid'], t)
  return res

def command_addtopic(bot, room, nick, access_level, parameters, message):
  if not parameters: return 'Expected topic text to add.'
  topic = parameters

  jid = bot.roster[room][nick][ROSTER_JID]
  if jid != None: jid = xmpp.JID(jid).getStripped().lower()

  topicdic = {
    'topic': topic,
    'jid': jid,
    'time': time.time(),
  }
  addtopic(bot, room, topicdic)
  number = len(topic_db[room])
  return "topic #%d added."%(number)

def command_deltopic(bot, room, nick, access_level, parameters, message):
  try: number = int(parameters)
  except: return 'Expected topic number to delete.'

  jid = bot.roster[room][nick][ROSTER_JID]
  if jid != None: jid = xmpp.JID(jid).getStripped().lower()

  if not room in topic_db or len(topic_db[room]) == 0:
    return 'No topics added yet!'
    
  existent_topic = gettopic(bot, room, number)
  if not existent_topic:
    return "There's no topic #%d, and there is total of %d topics."%(number, len(topic_db[room]))
  
  if access_level < LEVEL_ADMIN:
    if not jid or existent_topic['jid'] != jid or time.time() - existent_topic['time'] > 3600:
      return "You can't delete topic #%d."%(number)
    
  deltopic(bot, room, number)
  return "topic #%d deleted."%(number)

def load(bot):
  global topic_db
  topic_db = bot.load_database('topic') or {}
  bot.add_command('topic', command_topic, LEVEL_GUEST, 'topic')
  bot.add_command('addtopic', command_addtopic, LEVEL_MEMBER, 'topic')
  bot.add_command('deltopic', command_deltopic, LEVEL_MEMBER, 'topic')


def save(bot):
  bot.save_database('topic', topic_db)

def unload(bot):
  pass
