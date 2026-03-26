"""
Система кэширования на MongoDB - все данные хранятся ТОЛЬКО в MongoDB
"""
from Music .core .mongo import mongodb
from Music import LOGGER
import time

logger =LOGGER (__name__ )


class MongoCache :
    """Класс для работы с кэшем в MongoDB"""

    def __init__ (self ):
        self .cache_db =mongodb .cache
        self .metadata_db =mongodb .cache_metadata

    async def set (_ ,key :str ,value ,ttl :int =None ):
        """Сохранить значение в MongoDB с опциональным TTL"""
        try :
            data ={
                '_id':key ,
                'value':value ,
                'timestamp':time .time ()
            }
            if ttl :
                data ['expires_at ']=time .time ()+ttl
            await _ .cache_db .update_one ({'_id':key },{'$set':data },upsert =True )
            return True
        except Exception as e :
            logger .error (f'Ошибка при сохранении в MongoDB кэш: {e }')
            return False

    async def get (_ ,key :str ):
        """Получить значение из MongoDB"""
        try :
            data =await _ .cache_db .find_one ({'_id':key })
            if not data :
                return None
            #Проверяем TTL
            if 'expires_at ' in data :
                if time .time ()> data ['expires_at ']:
                    await _ .cache_db .delete_one ({'_id':key })
                    return None
            return data .get ('value')
        except Exception as e :
            logger .error (f'Ошибка при чтении из MongoDB кэш: {e }')
            return None

    async def delete (_ ,key :str ):
        """Удалить значение из MongoDB"""
        try :
            await _ .cache_db .delete_one ({'_id':key })
            return True
        except Exception as e :
            logger .error (f'Ошибка при удалении из MongoDB кэш: {e }')
            return False

    async def clear (_ ):
        """Очистить весь кэш"""
        try :
            await _ .cache_db .delete_many ({})
            return True
        except Exception as e :
            logger .error (f'Ошибка при очистке MongoDB кэш: {e }')
            return False

    async def get_all (_ ):
        """Получить все ключи кэша"""
        try :
            cursor =_ .cache_db .find ({})
            keys =[]
            async for doc in cursor :
                #Проверяем TTL
                if 'expires_at ' in doc :
                    if time .time ()> doc ['expires_at ']:
                        await _ .cache_db .delete_one ({'_id':doc ['_id']})
                        continue
                keys .append (doc ['_id'])
            return keys
        except Exception as e :
            logger .error (f'Ошибка при получении ключей из MongoDB кэш: {e }')
            return []


class MongoDictCache :
    """Кэш для работы с dictionary-аналогом в MongoDB (для chat_id-основанных данных)"""

    def __init__ (self ,collection_name :str ):
        self .collection =mongodb [collection_name ]

    async def set_for_chat (self ,chat_id :int ,data :dict ):
        """Сохранить данные для чата"""
        try :
            await self .collection .update_one (
                {'chat_id':chat_id },
                {'$set':{'data':data ,'timestamp':time .time ()}},
                upsert =True
            )
            return True
        except Exception as e :
            logger .error (f'Ошибка при сохранении данных чата: {e }')
            return False

    async def get_for_chat (self ,chat_id :int ):
        """Получить данные для чата"""
        try :
            doc =await self .collection .find_one ({'chat_id':chat_id })
            if not doc :
                return {}
            return doc .get ('data',{})
        except Exception as e :
            logger .error (f'Ошибка при получении данных чата: {e }')
            return {}

    async def get_value (self ,chat_id :int ,key :str ):
        """Получить одно значение для чата"""
        try :
            doc =await self .collection .find_one ({'chat_id':chat_id })
            if not doc :
                return None
            return doc .get ('data',{}) .get (key)
        except Exception as e :
            logger .error (f'Ошибка при получении значения чата: {e }')
            return None

    async def set_value (self ,chat_id :int ,key :str ,value ):
        """Установить одно значение для чата"""
        try :
            doc =await self .collection .find_one ({'chat_id':chat_id })
            if doc :
                current_data =doc .get ('data',{})
                current_data [key ]=value
                await self .collection .update_one (
                    {'chat_id':chat_id },
                    {'$set':{'data':current_data ,'timestamp':time .time ()}}
                )
            else :
                await self .collection .insert_one ({
                    'chat_id':chat_id ,
                    'data':{key :value },
                    'timestamp':time .time ()
                })
            return True
        except Exception as e :
            logger .error (f'Ошибка при установке значения чата: {e }')
            return False

    async def delete_for_chat (self ,chat_id :int ):
        """Удалить все данные для чата"""
        try :
            await self .collection .delete_one ({'chat_id':chat_id })
            return True
        except Exception as e :
            logger .error (f'Ошибка при удалении данных чата: {e }')
            return False

    async def clear_all (self ):
        """Очистить коллекцию"""
        try :
            await self .collection .delete_many ({})
            return True
        except Exception as e :
            logger .error (f'Ошибка при очистке коллекции: {e }')
            return False


# Инициализируем глобальные кэши
mongo_cache =MongoCache ()
active_cache =MongoDictCache ('cache_active_chats ')
pausestate_cache =MongoDictCache ('cache_pause_state ')
loopstate_cache =MongoDictCache ('cache_loop_state ')
skipstate_cache =MongoDictCache ('cache_skip_state ')
playstylecache =MongoDictCache ('cache_playstyle ')
download_cache =MongoDictCache ('cache_downloads ')
thumbnail_cache =MongoDictCache ('cache_thumbnails ')
speed_cache =MongoDictCache ('cache_speed ')
nonadmin_cache =MongoDictCache ('cache_nonadmin ')
channel_connect_cache =MongoDictCache ('cache_channel_connect ')
# NEW: Metadata cache for storing video title/thumbnail by video_id (global cache, not per-chat)
metadata_cache =mongo_cache

logger .info ('✓ MongoDB кэш система инициализирована')

