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
from Music .utils .decorators .language import language
from Music .utils .pastebin import AnonyBin
from Music .core .mongo import mongodb
from Music import LOGGER
urllib3 .disable_warnings (urllib3 .exceptions .InsecureRequestWarning )

logger = LOGGER (__name__)

@app .on_message (filters .command (['logs'])&SUDOERS )
@language
async def log_ (client ,message ,_ ):
    try :
        await message .reply_document (document ='log.txt')
    except :
        await message .reply_text (_ ['server_1'])

@app .on_message (filters .command (['restart'])&filters .user (config .OWNER_ID ))
async def restart_ (_ ,message ):
    """Перезагрузка бота с ПОЛНОЙ очисткой всех баз данных MongoDB"""
    response =await message .reply_text ('🔄 **[ПОЛНАЯ ОЧИСТКА] Перезагрузка бота...**\n\n⏳ Этап 1/4: Закрытие сессий...')
    
    try :
        # Этап 1: Закрытие всех активных сессий
        logger .info ('Starting full restart with complete database cleanup')
        
        # Уведомляем активные чаты
        try :
            cursor = mongodb .streams .find ({})
            ac_chats = []
            async for doc in cursor :
                ac_chats .append (doc .get ('chat_id'))
            
            for chat_id in ac_chats :
                try :
                    await app .send_message (
                        chat_id =int (chat_id ),
                        text =f'{app .mention } **🔄 перезагружается с ПОЛНОЙ очисткой данных**\n\n⏳ Бот будет доступен через 30 секунд...\n\n✨ Все данные базы будут очищены!'
                    )
                except :
                    pass
        except Exception as e :
            logger .warning (f'Failed to notify active chats: {e }')
        
        await response .edit_text ('🔄 **[ПОЛНАЯ ОЧИСТКА] Перезагрузка бота...**\n\n✅ Этап 1/4: Сессии закрыты\n⏳ Этап 2/4: Очистка файловой системы...')
        
        # Этап 2: Удаляем ВСЕ кэш файлы
        deleted_dirs = []
        for dir_name in ['raw_files', 'cache', 'downloads', 'tmp', '__pycache__']:
            try :
                if os .path .exists (dir_name ):
                    shutil .rmtree (dir_name )
                    deleted_dirs .append (dir_name )
                    logger .info (f'Deleted directory: {dir_name }')
            except Exception as e :
                logger .warning (f'Failed to delete {dir_name}: {e }')
        
        await response .edit_text ('🔄 **[ПОЛНАЯ ОЧИСТКА] Перезагрузка бота...**\n\n✅ Этап 1/4: Сессии закрыты\n✅ Этап 2/4: Файлы удалены\n⏳ Этап 3/4: Очистка ВСЕХ MongoDB коллекций...')
        
        # Этап 3: ПОЛНАЯ очистка ALL MongoDB коллекций
        collections_to_clear = [
            'cache', 'cache_active_chats', 'cache_pause_state', 'cache_loop_state',
            'cache_skip_state', 'cache_playstyle', 'cache_downloads', 'cache_thumbnails',
            'cache_speed', 'cache_nonadmin', 'cache_channel_connect',
            'adminauth', 'authuser', 'autoend', 'assistants', 'blacklistChat',
            'blockedusers', 'chats', 'cplaymode', 'upcount', 'gban', 'language',
            'onoffper', 'playmode', 'playtypedb', 'skipmode', 'streams', 'calls',
            'tgusersdb', 'model'
        ]
        
        cleared_count = 0
        total_docs = 0
        
        for collection_name in collections_to_clear :
            try :
                collection = mongodb [collection_name ]
                # Получаем количество документов перед удалением
                doc_count = await collection .count_documents ({})
                if doc_count > 0 :
                    result = await collection .delete_many ({})
                    total_docs += result .deleted_count
                    cleared_count += 1
                    logger .info (f'Collection {collection_name}: deleted {result .deleted_count} documents')
            except Exception as e :
                logger .warning (f'Could not clear collection {collection_name}: {e }')
        
        # Переинициализируем sudoers с owner
        try :
            sudoersdb = mongodb .sudoers
            await sudoersdb .delete_many ({})
            await sudoersdb .insert_one ({'sudo':'sudo', 'sudoers':[config .OWNER_ID ]})
            logger .info (f'Reinitialized sudoers with OWNER_ID: {config .OWNER_ID }')
        except Exception as e :
            logger .error (f'Failed to reinitialize sudoers: {e }')
        
        await response .edit_text (f'🔄 **[ПОЛНАЯ ОЧИСТКА] Перезагрузка бота...**\n\n✅ Этап 1/4: Сессии закрыты\n✅ Этап 2/4: Файлы удалены ({len (deleted_dirs )} папок)\n✅ Этап 3/4: MongoDB очищена\n   📊 Очищено {cleared_count} коллекций\n   📝 Удалено {total_docs} документов\n⏳ Этап 4/4: Перезагрузка...')
        
        logger .info (f'Restart complete: cleared {cleared_count} collections, deleted {total_docs} documents')
        
        # Этап 4: Перезагружаем бот
        await asyncio .sleep (2)
        os .system (f'kill -9 {os .getpid ()} && bash start')
    
    except Exception as e :
        logger .error (f'Restart error: {e }')
        await response .edit_text (f'❌ **Ошибка при перезагрузке:**\n\n`{str(e)}`')