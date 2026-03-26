import asyncio
import os
import shutil
import socket
from datetime import datetime
import urllib3
from pyrogram import filters
import config
from Music import app
from Music .misc import SUDOERS
from Music .utils .database import (
    get_active_chats ,
    remove_active_chat ,
    remove_active_video_chat ,
    active ,
    activevideo ,
    assistantdict ,
    autoend ,
    count ,
    channelconnect ,
    langm ,
    loop ,
    maintenance ,
    nonadmin ,
    pause ,
    playmode ,
    playtype ,
    skipmode
)
from Music .utils .decorators .language import language
from Music .utils .pastebin import AnonyBin
from Music .core .mongo import mongodb
urllib3 .disable_warnings (urllib3 .exceptions .InsecureRequestWarning )

@app .on_message (filters .command (['logs'])&SUDOERS )
@language
async def log_ (client ,message ,_ ):
    try :
        await message .reply_document (document ='log.txt')
    except :
        await message .reply_text (_ ['server_1'])

@app .on_message (filters .command (['restart'])&filters .user (config .OWNER_ID ))
async def restart_ (_ ,message ):
    """Перезагрузка бота с полной очисткой баз данных и кэшей (только для owner)"""
    response =await message .reply_text ('🔄 **Перезагрузка с полной очисткой...**\n\n⏳ Принцип: Завершение сессий...')
    
    try :
        # Уведомляем активные чаты
        ac_chats =await get_active_chats ()
        for x in ac_chats :
            try :
                await app .send_message (
                    chat_id =int (x ),
                    text =f'{app .mention } **перезагружается с полной очисткой данных**\n\n⏳ Бот будет доступен через 20-30 секунд...'
                )
                await remove_active_chat (x )
                await remove_active_video_chat (x )
            except :
                pass
        
        await response .edit_text ('🔄 **Перезагрузка с полной очисткой...**\n\n✅ Сессии закрыты\n⏳ Очистка памяти...')
        
        # Очищаем все в памяти (RAM cache)
        active .clear ()
        activevideo .clear ()
        assistantdict .clear ()
        autoend .clear ()
        count .clear ()
        channelconnect .clear ()
        langm .clear ()
        loop .clear ()
        maintenance .clear ()
        nonadmin .clear ()
        pause .clear ()
        playmode .clear ()
        playtype .clear ()
        skipmode .clear ()
        
        await response .edit_text ('🔄 **Перезагрузка с полной очисткой...**\n\n✅ Сессии закрыты\n✅ Память очищена\n⏳ Очистка файлов...')
        
        # Удаляем кэш и временные файлы
        try :
            if os .path .exists ('raw_files'):
                shutil .rmtree ('raw_files')
            if os .path .exists ('cache'):
                shutil .rmtree ('cache')
            if os .path .exists ('downloads'):
                shutil .rmtree ('downloads')
        except Exception as e :
            pass
        
        await response .edit_text ('🔄 **Перезагрузка с полной очисткой...**\n\n✅ Сессии закрыты\n✅ Память очищена\n✅ Файлы удалены\n⏳ Очистка баз данных...')
        
        # Очищаем ВСЕ базы данных MongoDB
        try :
            # Очищаем все кэш-коллекции
            await mongodb .cache .delete_many ({})
            await mongodb .cache_active_chats .delete_many ({})
            await mongodb .cache_pause_state .delete_many ({})
            await mongodb .cache_loop_state .delete_many ({})
            await mongodb .cache_skip_state .delete_many ({})
            await mongodb .cache_playstyle .delete_many ({})
            await mongodb .cache_downloads .delete_many ({})
            await mongodb .cache_thumbnails .delete_many ({})
            await mongodb .cache_speed .delete_many ({})
            await mongodb .cache_nonadmin .delete_many ({})
            await mongodb .cache_channel_connect .delete_many ({})
            # Очищаем основные БД
            await mongodb .adminauth .delete_many ({})
            await mongodb .authuser .delete_many ({})
            await mongodb .autoend .delete_many ({})
            await mongodb .assistants .delete_many ({})
            await mongodb .blacklistChat .delete_many ({})
            await mongodb .blockedusers .delete_many ({})
            await mongodb .chats .delete_many ({})
            await mongodb .cplaymode .delete_many ({})
            await mongodb .upcount .delete_many ({})
            await mongodb .gban .delete_many ({})
            await mongodb .language .delete_many ({})
            await mongodb .onoffper .delete_many ({})
            await mongodb .playmode .delete_many ({})
            await mongodb .playtypedb .delete_many ({})
            await mongodb .skipmode .delete_many ({})
            await mongodb .streams .delete_many ({})
            await mongodb .calls .delete_many ({})
            # sudoers оставляем с owner
            sudoersdb = mongodb .sudoers
            await sudoersdb .delete_one ({'sudo':'sudo'})
            await sudoersdb .update_one ({'sudo':'sudo'},{'$set':{'sudoers':[config .OWNER_ID ]}},upsert =True )
            await mongodb .tgusersdb .delete_many ({})
            await mongodb .model .delete_many ({})
        except Exception as e :
            pass
        
        await response .edit_text ('🔄 **Перезагрузка с полной очисткой...**\n\n✅ Сессии закрыты\n✅ Память очищена\n✅ Файлы удалены\n✅ Базы данных очищены\n⏳ Перезагрузка бота...')
        
        # Перезагружаем бот
        os .system (f'kill -9 {os .getpid ()} && bash start')
    
    except Exception as e :
        await response .edit_text (f'❌ **Ошибка при перезагрузке:**\n\n`{str(e)}`')