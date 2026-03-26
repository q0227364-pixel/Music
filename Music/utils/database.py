import random
from typing import Dict ,List ,Union
from Music import userbot
from Music .core .mongo import mongodb
from Music import LOGGER
from Music .utils .mongo_cache import (
    mongo_cache ,
    active_cache ,
    pausestate_cache ,
    loopstate_cache ,
    skipstate_cache ,
    playstylecache ,
    download_cache ,
    thumbnail_cache ,
    speed_cache ,
    nonadmin_cache ,
    channel_connect_cache
)

logger =LOGGER (__name__ )
authdb =mongodb .adminauth
authuserdb =mongodb .authuser
autoenddb =mongodb .autoend
assdb =mongodb .assistants
blacklist_chatdb =mongodb .blacklistChat
blockeddb =mongodb .blockedusers
chatsdb =mongodb .chats
channeldb =mongodb .cplaymode
countdb =mongodb .upcount
gbansdb =mongodb .gban
langdb =mongodb .language
onoffdb =mongodb .onoffper
playmodedb =mongodb .playmode
playtypedb =mongodb .playtypedb
skipdb =mongodb .skipmode
sudoersdb =mongodb .sudoers
usersdb =mongodb .tgusersdb
modeldb =mongodb .model
# Больше НЕ используем локальные переменные - всё на MongoDB!
# Все кэши теперь через mongo_cache объекты

async def get_assistant_number (chat_id :int )->str :
    """Получить номер ассистента из MongoDB"""
    assistant =await assdb .find_one ({'chat_id':chat_id })
    if not assistant :
        return None
    return assistant .get ('assistant')

async def get_client (assistant :int ):
    if int (assistant )==1 :
        return userbot .one
    elif int (assistant )==2 :
        return userbot .two
    elif int (assistant )==3 :
        return userbot .three
    elif int (assistant )==4 :
        return userbot .four
    elif int (assistant )==5 :
        return userbot .five

async def set_assistant_new (chat_id ,number ):
    number =int (number )
    await assdb .update_one ({'chat_id':chat_id },{'$set':{'assistant':number }},upsert =True )

async def set_assistant (chat_id ):
    from Music .core .userbot import assistants
    if not assistants :
        logger .error ('No assistants available - cannot set assistant for chat')
        return None
    ran_assistant =random .choice (assistants )
    await assdb .update_one ({'chat_id':chat_id },{'$set':{'assistant':ran_assistant }},upsert =True )
    userbot =await get_client (ran_assistant )
    return userbot

async def get_assistant (chat_id :int )->str :
    from Music .core .userbot import assistants
    dbassistant =await assdb .find_one ({'chat_id':chat_id })
    if not dbassistant :
        userbot =await set_assistant (chat_id )
        return userbot
    else :
        got_assis =dbassistant ['assistant']
        if got_assis in assistants :
            userbot =await get_client (got_assis )
            return userbot
        else :
            userbot =await set_assistant (chat_id )
            return userbot

async def set_calls_assistant (chat_id ):
    from Music .core .userbot import assistants
    ran_assistant =random .choice (assistants )
    await assdb .update_one ({'chat_id':chat_id },{'$set':{'assistant':ran_assistant }},upsert =True )
    return ran_assistant

async def group_assistant (self ,chat_id :int )->int :
    from Music .core .userbot import assistants
    dbassistant =await assdb .find_one ({'chat_id':chat_id })
    if not dbassistant :
        assis =await set_calls_assistant (chat_id )
    else :
        assis =dbassistant ['assistant']
        if assis not in assistants :
            assis =await set_calls_assistant (chat_id )
    if int (assis )==1 :
        return self .one
    elif int (assis )==2 :
        return self .two
    elif int (assis )==3 :
        return self .three
    elif int (assis )==4 :
        return self .four
    elif int (assis )==5 :
        return self .five

async def is_skipmode (chat_id :int )->bool :
    user =await skipdb .find_one ({'chat_id':chat_id })
    if not user :
        return True
    return False

async def skip_on (chat_id :int ):
    user =await skipdb .find_one ({'chat_id':chat_id })
    if user :
        return await skipdb .delete_one ({'chat_id':chat_id })

async def skip_off (chat_id :int ):
    user =await skipdb .find_one ({'chat_id':chat_id })
    if not user :
        return await skipdb .insert_one ({'chat_id':chat_id })

async def get_upvote_count (chat_id :int )->int :
    mode =await countdb .find_one ({'chat_id':chat_id })
    if not mode :
        return 5
    return mode .get ('mode',5 )

async def set_upvotes (chat_id :int ,mode :int ):
    await countdb .update_one ({'chat_id':chat_id },{'$set':{'mode':mode }},upsert =True )

async def is_autoend ()->bool :
    chat_id =1234
    user =await autoenddb .find_one ({'chat_id':chat_id })
    if not user :
        return False
    return True

async def autoend_on ():
    chat_id =1234
    await autoenddb .insert_one ({'chat_id':chat_id })

async def autoend_off ():
    chat_id =1234
    await autoenddb .delete_one ({'chat_id':chat_id })

async def get_loop (chat_id :int )->int :
    loop_val =await loopstate_cache .get_value (chat_id ,'loop')
    if not loop_val :
        return 0
    return loop_val

async def set_loop (chat_id :int ,mode :int ):
    await loopstate_cache .set_value (chat_id ,'loop',mode )

async def get_cmode (chat_id :int )->int :
    mode =await channeldb .find_one ({'chat_id':chat_id })
    if not mode :
        return None
    return mode .get ('mode')

async def set_cmode (chat_id :int ,mode :int ):
    await channeldb .update_one ({'chat_id':chat_id },{'$set':{'mode':mode }},upsert =True )

async def get_playtype (chat_id :int )->str :
    mode =await playtypedb .find_one ({'chat_id':chat_id })
    if not mode :
        return 'Everyone'
    return mode .get ('mode','Everyone')

async def set_playtype (chat_id :int ,mode :str ):
    await playtypedb .update_one ({'chat_id':chat_id },{'$set':{'mode':mode }},upsert =True )

async def get_playmode (chat_id :int )->str :
    mode =await playmodedb .find_one ({'chat_id':chat_id })
    if not mode :
        return 'Direct'
    return mode .get ('mode','Direct')

async def set_playmode (chat_id :int ,mode :str ):
    await playmodedb .update_one ({'chat_id':chat_id },{'$set':{'mode':mode }},upsert =True )

async def get_lang (chat_id :int )->str :
    return 'en'

async def set_lang (chat_id :int ,lang :str ):
    await langdb .update_one ({'chat_id':chat_id },{'$set':{'lang':lang }},upsert =True )

async def is_music_playing (chat_id :int )->bool :
    mode =await pausestate_cache .get_value (chat_id ,'paused')
    if not mode :
        return False
    return mode

async def music_on (chat_id :int ):
    await pausestate_cache .set_value (chat_id ,'paused',True )

async def music_off (chat_id :int ):
    await pausestate_cache .set_value (chat_id ,'paused',False )

async def get_active_chats ()->list :
    """Получить все активные чаты из MongoDB"""
    active_list =[]
    async for doc in mongodb .streams .find ({}):
        active_list .append (doc .get ('chat_id'))
    return active_list

async def is_active_chat (chat_id :int )->bool :
    """Проверить активен ли чат"""
    chat =await mongodb .streams .find_one ({'chat_id':chat_id })
    return chat is not None

async def add_active_chat (chat_id :int ):
    """Добавить активный чат в MongoDB"""
    is_active =await is_active_chat (chat_id )
    if not is_active :
        await mongodb .streams .insert_one ({'chat_id':chat_id })

async def remove_active_chat (chat_id :int ):
    """Удалить активный чат из MongoDB"""
    await mongodb .streams .delete_one ({'chat_id':chat_id })

async def get_active_video_chats ()->list :
    """Получить все активные видео чаты из MongoDB"""
    active_list =[]
    async for doc in mongodb .calls .find ({}):
        active_list .append (doc .get ('chat_id'))
    return active_list

async def is_active_video_chat (chat_id :int )->bool :
    """Проверить активно ли видео в чате"""
    chat =await mongodb .calls .find_one ({'chat_id':chat_id })
    return chat is not None

async def add_active_video_chat (chat_id :int ):
    """Добавить активный видео чат в MongoDB"""
    is_active =await is_active_video_chat (chat_id )
    if not is_active :
        await mongodb .calls .insert_one ({'chat_id':chat_id })

async def remove_active_video_chat (chat_id :int ):
    """Удалить активный видео чат из MongoDB"""
    await mongodb .calls .delete_one ({'chat_id':chat_id })

async def check_nonadmin_chat (chat_id :int )->bool :
    user =await authdb .find_one ({'chat_id':chat_id })
    if not user :
        return False
    return True

async def is_nonadmin_chat (chat_id :int )->bool :
    user =await authdb .find_one ({'chat_id':chat_id })
    if not user :
        return False
    return True

async def add_nonadmin_chat (chat_id :int ):
    is_admin =await check_nonadmin_chat (chat_id )
    if is_admin :
        return
    return await authdb .insert_one ({'chat_id':chat_id })

async def remove_nonadmin_chat (chat_id :int ):
    is_admin =await check_nonadmin_chat (chat_id )
    if not is_admin :
        return
    return await authdb .delete_one ({'chat_id':chat_id })

async def is_on_off (on_off :int )->bool :
    onoff =await onoffdb .find_one ({'on_off':on_off })
    if not onoff :
        return False
    return True

async def add_on (on_off :int ):
    is_on =await is_on_off (on_off )
    if is_on :
        return
    return await onoffdb .insert_one ({'on_off':on_off })

async def add_off (on_off :int ):
    is_off =await is_on_off (on_off )
    if not is_off :
        return
    return await onoffdb .delete_one ({'on_off':on_off })

async def is_maintenance ():
    get =await onoffdb .find_one ({'on_off':1 })
    if not get :
        return True
    else :
        return False

async def maintenance_off ():
    is_off =await is_on_off (1 )
    if not is_off :
        return
    return await onoffdb .delete_one ({'on_off':1 })

async def maintenance_on ():
    is_on =await is_on_off (1 )
    if is_on :
        return
    return await onoffdb .insert_one ({'on_off':1 })

async def is_served_user (user_id :int )->bool :
    user =await usersdb .find_one ({'user_id':user_id })
    if not user :
        return False
    return True

async def get_served_users ()->list :
    users_list =[]
    async for user in usersdb .find ({'user_id':{'$gt':0 }}):
        users_list .append (user )
    return users_list

async def add_served_user (user_id :int ):
    is_served =await is_served_user (user_id )
    if is_served :
        return
    return await usersdb .insert_one ({'user_id':user_id })

async def get_served_chats ()->list :
    chats_list =[]
    async for chat in chatsdb .find ({'chat_id':{'$lt':0 }}):
        chats_list .append (chat )
    return chats_list

async def is_served_chat (chat_id :int )->bool :
    chat =await chatsdb .find_one ({'chat_id':chat_id })
    if not chat :
        return False
    return True

async def add_served_chat (chat_id :int ):
    is_served =await is_served_chat (chat_id )
    if is_served :
        return
    return await chatsdb .insert_one ({'chat_id':chat_id })

async def blacklisted_chats ()->list :
    chats_list =[]
    async for chat in blacklist_chatdb .find ({'chat_id':{'$lt':0 }}):
        chats_list .append (chat ['chat_id'])
    return chats_list

async def blacklist_chat (chat_id :int )->bool :
    if not await blacklist_chatdb .find_one ({'chat_id':chat_id }):
        await blacklist_chatdb .insert_one ({'chat_id':chat_id })
        return True
    return False

async def whitelist_chat (chat_id :int )->bool :
    if await blacklist_chatdb .find_one ({'chat_id':chat_id }):
        await blacklist_chatdb .delete_one ({'chat_id':chat_id })
        return True
    return False

async def _get_authusers (chat_id :int )->Dict [str ,int ]:
    _notes =await authuserdb .find_one ({'chat_id':chat_id })
    if not _notes :
        return {}
    return _notes ['notes']

async def get_authuser_names (chat_id :int )->List [str ]:
    _notes =[]
    for note in await _get_authusers (chat_id ):
        _notes .append (note )
    return _notes

async def get_authuser (chat_id :int ,name :str )->Union [bool ,dict ]:
    name =name
    _notes =await _get_authusers (chat_id )
    if name in _notes :
        return _notes [name ]
    else :
        return False

async def save_authuser (chat_id :int ,name :str ,note :dict ):
    name =name
    _notes =await _get_authusers (chat_id )
    _notes [name ]=note
    await authuserdb .update_one ({'chat_id':chat_id },{'$set':{'notes':_notes }},upsert =True )

async def delete_authuser (chat_id :int ,name :str )->bool :
    notesd =await _get_authusers (chat_id )
    name =name
    if name in notesd :
        del notesd [name ]
        await authuserdb .update_one ({'chat_id':chat_id },{'$set':{'notes':notesd }},upsert =True )
        return True
    return False

async def get_gbanned ()->list :
    results =[]
    async for user in gbansdb .find ({'user_id':{'$gt':0 }}):
        user_id =user ['user_id']
        results .append (user_id )
    return results

async def is_gbanned_user (user_id :int )->bool :
    user =await gbansdb .find_one ({'user_id':user_id })
    if not user :
        return False
    return True

async def add_gban_user (user_id :int ):
    is_gbanned =await is_gbanned_user (user_id )
    if is_gbanned :
        return
    return await gbansdb .insert_one ({'user_id':user_id })

async def remove_gban_user (user_id :int ):
    is_gbanned =await is_gbanned_user (user_id )
    if not is_gbanned :
        return
    return await gbansdb .delete_one ({'user_id':user_id })

async def get_sudoers ()->list :
    sudoers =await sudoersdb .find_one ({'sudo':'sudo'})
    if not sudoers :
        return []
    return sudoers ['sudoers']

async def add_sudo (user_id :int )->bool :
    sudoers =await get_sudoers ()
    sudoers .append (user_id )
    await sudoersdb .update_one ({'sudo':'sudo'},{'$set':{'sudoers':sudoers }},upsert =True )
    return True

async def remove_sudo (user_id :int )->bool :
    sudoers =await get_sudoers ()
    sudoers .remove (user_id )
    await sudoersdb .update_one ({'sudo':'sudo'},{'$set':{'sudoers':sudoers }},upsert =True )
    return True

async def get_banned_users ()->list :
    results =[]
    async for user in blockeddb .find ({'user_id':{'$gt':0 }}):
        user_id =user ['user_id']
        results .append (user_id )
    return results

async def get_banned_count ()->int :
    users =blockeddb .find ({'user_id':{'$gt':0 }})
    users =await users .to_list (length =100000 )
    return len (users )

async def is_banned_user (user_id :int )->bool :
    user =await blockeddb .find_one ({'user_id':user_id })
    if not user :
        return False
    return True

async def add_banned_user (user_id :int ):
    is_gbanned =await is_banned_user (user_id )
    if is_gbanned :
        return
    return await blockeddb .insert_one ({'user_id':user_id })

async def remove_banned_user (user_id :int ):
    is_gbanned =await is_banned_user (user_id )
    if not is_gbanned :
        return
    return await blockeddb .delete_one ({'user_id':user_id })

async def get_model_settings ()->dict :
    settings =await modeldb .find_one ({'model':'settings'})
    if not settings :
        return {'tts':'athena','image':'stable-diffusion','ai':'GPT4'}
    return settings ['settings']

async def update_model_settings (settings :dict )->bool :
    current_settings =await get_model_settings ()
    updated_settings ={**current_settings ,**settings }
    await modeldb .update_one ({'model':'settings'},{'$set':{'settings':updated_settings }},upsert =True )
    return True