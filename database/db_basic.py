import  pymongo
import json
from bson import json_util

# 数据库结构概览: 
# 数据库: keywordsManagement
#  ->表: User ,存储账户信息
#  ->表: Project, 存储项目概要信息，但不包含分类信息
# 数据库: 项目x: 每个项目一个数据库，每个数据库包含如下表
#  ->表: Categories
#  ->表: Urls
#  ->表: Articles
#  ->表: BasicWords
#  ->表: ExtendedWords
#  ->表: ignoreDict
#  ->表: invalidDict
#  ->表: userDict

client = pymongo.MongoClient('mongodb://127.0.0.1:27017/')
dbPrefix = 'KWM' #keywordsManagement

def dbinit():
    """
    初始化一些数据库或collection,不是非得做，mongo会自动创建不存在的数据库和collection。
    但是为了流程考虑，暂时保留该步骤。具体如下:
    1 数据库: keywordsManagement  -> User | Project
    2 keywordsManagement -> Project 表中定义的各个数据库 
    """
    print('<<-dbinit begin ...')
    keywordsmanagementDbHandler = client[dbPrefix]
    # 1 数据库: keywordsManagement  -> User | Project
    keywordsManagementDbCollections = keywordsmanagementDbHandler.list_collection_names()
    for element in ['User', 'Project']:
        if element in keywordsManagementDbCollections:
            print(f"表{element}在数据库keywordsManagement中存在")
        else:
            print(f"表{element}在数据库keywordsManagement中不存在,创建中 ...")
            # 创建表
            try:
                keywordsmanagementDbHandler.create_collection(element)
            except Exception as e:
                print(e)
        
        # Project表 将 name设成唯一性索引, User 表，将account字段设成唯一索引
        keywordsmanagementDbHandler.Project.create_index([("projectName",1)],unique = True, background = True)
        keywordsmanagementDbHandler.User.create_index([("account",1)],unique = True, background = True)

    # 2 keywordsManagement -> Project 表中定义的各个数据库 
    # 获取所有项目名称列表
    projectNames = keywordsmanagementDbHandler['Project'].find({},{ "_id": 0, "projectName": 1}).sort('timestamp',-1)
    for element in projectNames:
        # 创建每一个数据库,如果不存在; 并将每个项目中， Categories 表设成 name 字段的唯一性索引
        client[dbPrefix + '-' + element['projectName']]['Categories'].create_index([("categoryName",1)],unique = True, background = True)
    print('dbinit end ...>>')

async def list_collection_names(dbName,collectionName):
    dbHandler = client[dbName]
    collectionHandler = dbHandler[collectionName]
    return collectionHandler.list_collection_names()

async def find (dbName,collectionName,skipValue = 0,limitValue = 10 ,queryDict={}):
    """
    查找所有符合条件的数据行
    """
    print('skip,limit',skipValue,limitValue)
    dbHandler = client[dbName]
    collectionHandler = dbHandler[collectionName]
    result = json_util.dumps(collectionHandler.find(queryDict).skip(skipValue).limit(limitValue))
    return result


async def find_one (dbName,collectionName,queryDict={},showDict={}):
    """
    查找第一个符合条件的数据行
    """
    dbHandler = client[dbName]
    collectionHandler = dbHandler[collectionName]
    if queryDict == {}:
        if showDict == {}:
            result = json_util.dumps(collectionHandler.find_one())
        else:
            result = json_util.dumps(collectionHandler.find_one({},showDict))
    else:
        if showDict == {}:
            result = json_util.dumps(collectionHandler.find_one(queryDict))
        else:
            result = json_util.dumps(collectionHandler.find_one(queryDict,showDict))
    return result


async def insert_one(dbName,collectionName,data):
    """
    数据库表中插入 单行数据
    """
    dbHandler = client[dbName]
    collectionHandler = dbHandler[collectionName]
    try:
        result =  collectionHandler.insert_one(data)
        # print(result.inserted_id)
        # 成功: 返回插入的数据个数,此处为1
        return ([result.inserted_id])
    except pymongo.errors.DuplicateKeyError as e:
        print('error:',e)
        return 'duplicateError-projectName'
    except Exception as e:
        print(e)
        return 'project-unknownError'

async def insert_many(dbName,collectionName,datalist):
    """
    数据库表中插入 多行数据
    """
    dbHandler = client[dbName]
    collectionHandler = dbHandler[collectionName]
    if collectionName == 'Categories':
        collectionHandler.create_index([('categoryName',1)],unique = True, background = True)
    elif collectionName == 'User':
        collectionHandler.create_index([('account',1)],unique = True, background = True)
    try:
        print('datalist',datalist)
        results =  collectionHandler.insert_many(datalist)
        # print(results.inserted_ids)
        # 成功: 返回插入的数据行数
        return len(results.inserted_ids)
    except pymongo.errors.BulkWriteError as e:
        print('error:',e)
        # 出现重复 category，返回错误信息
        return 'duplicateError-categoryName'
    except:
        # 其他报错
        return 'category-unknownError'

async def update_one(dbName,collectionName,queryDict,setDict):
    dbHandler = client[dbName]
    collectionHandler = dbHandler[collectionName]
    result1 = collectionHandler.update_one(queryDict,setDict)
    # modified_count 返回更新的条数
    # print(result1.modified_count)
    return (result1.modified_count)


async def update_many(dbName,collectionName,queryDict,setDict):
    dbHandler = client[dbName]
    collectionHandler = dbHandler[collectionName]
    result1 = collectionHandler.update_many(queryDict,setDict)
    # modified_count 返回更新的条数
    return (result1.modified_count)
    
async def copy_database(sourceDb,destDb):
    # 复制一个数据库， 该特性已经被 deprecated ，小心
    try:
        result = client.admin.command('copydb',fromdb=sourceDb, todb=destDb)
        # print('result',result)
        return (result)
        # result可能看起来这个样子
        # {'note': 'Support for the copydb command has been deprecated. See http://dochub.mongodb.org/core/copydb-clone-deprecation', 'ok': 1.0}
    except Exception as e:
        return 'copyDb-error'
        

async def drop_database(db2drop):
    try:
        result1 = client.drop_database(db2drop)
        return result1
    except:
        return 'error'

async def delete_one(dbName,collectionName,queryDict):
    dbHandler = client[dbName]
    collectionHandler = dbHandler[collectionName]
    try:
        result1 = collectionHandler.delete_one(queryDict)
        return result1.deleted_count
    except:
        return 'error'

async def delete_many(dbName,collectionName,queryDict):
    dbHandler = client[dbName]
    collectionHandler = dbHandler[collectionName]
    try:
        result1 = collectionHandler.delete_many(queryDict)
        return result1.deleted_count
    except:
        return 'error'