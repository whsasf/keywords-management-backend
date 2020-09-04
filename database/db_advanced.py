from .db_basic import dbinit, insert_one, insert_many, find, update_one
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

# 数据库部分初始化操作
dbinit()
dbPrefix = 'keywordsManagement'

# 新项目创建
async def createnewproject(dbName,collectionName,projectObjectData):
    #1- 在Project表添加新项目，如果已经存在，则报错返回
    categotiesData =  projectObjectData.pop('categories')
    result1 = await insert_one(dbName,collectionName,projectObjectData)
    if result1 == 1:
        #2-项目创建成功，则创建以该项目命名的数据库，并将Categories 写入 Categories 表格 
        dbName2 = projectObjectData['projectName']
        result2 = await insert_many(dbPrefix + '-' + dbName2,'Categories',categotiesData)
        #print(result2)
        if isinstance(result2,int):
            # 成功,则读取所有项目及目录信息并返回: result3: 项目 ，resukt4: 目录
            return await fetchAllProjects()
        else: 
            return result2
    else:
        return result1

async def fetchAllProjects ():
    # 读取所有的项目信息
    result1 = json.loads(await find(dbPrefix, 'Project'))
    for element in result1:
        projectname = element['projectName']
        # 获取该 项目中的目录信息
        category = await find(dbPrefix + '-' +projectname, 'Categories')
        element['categories'] = json.loads(category)
        #print(element)
    return result1

async def updateProject(dbName,collectionName,quertDict,setDict):
    # 1- 更新特定醒目名称信息
    result1 = await update_one(dbName,collectionName,quertDict,setDict)
    if result1 == 1:
        # 修改 项目数据库列表成功
        # 2- 修改项目对应的数据库名称
        await 

        # 3- 拉取所有数据
        result = await fetchAllProjects()
    else:
        pass
    return (result)