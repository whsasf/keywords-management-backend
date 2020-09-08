from .db_basic import dbinit, insert_one, insert_many, find,findCount, find_one, update_one, copy_database, drop_database, delete_one
import json
from bson import json_util
from utilities.jwtTools import createJWT, verifyJWT

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
dbPrefix = 'KWM'

# Projects 相关 高级 函数

async def fetchAllProjects(currentpage = 1, pagesize =10 ,returnTotalCount=True):
    # 1- 获取 Project表内容
    result1 = await fetchTable(dbPrefix,'Project',currentpage=currentpage, pagesize =pagesize,returnTotalCount=True)
    #print('result1',type(result1),result1)
    # result1 形式:  result1 = {'count':count,'content':content}
    # 2- 因为category 跟 表 Project 是分开的，所以需要分开查找
    for project in result1['content']:
        #print('project',project)
        projectId = project['_id']['$oid']
        result2 = await fetchTable(dbPrefix + '-' + projectId, 'Categories',currentpage=0, pagesize=0, returnTotalCount=False)
        #print('xxxxxx',result2)
        project['categories'] = result2['content']
    return result1


async def createnewproject(dbName,collectionName,projectObjectData):
    # 1- 在Project表添加新项目，如果已经存在，则报错返回
    categotiesData =  projectObjectData.pop('categories')
    result1 = await insert_one(dbName,collectionName,projectObjectData)
    # result1 形式:  result1 = {'count':count,'content':content}
    if len(result1) == 1:
        # 2-项目创建成功，则创建以该项目命名的数据库，并将Categories 写入 Categories 表格 
        # dbName2 = projectObjectData['projectName']
        # 使用uuid代表真正的项目名称，并创建项目
        dbName2 = str(result1[0])
        print('dbName2',type(dbName2))
        if len(categotiesData) > 0:
            # 只有设置了目录元素的时候才进行插入，否则，什么都不做
            result2 = await insert_many(dbPrefix + '-' + dbName2,'Categories',categotiesData)
            print('result2',result2)
        else:
            result2 = 0
            print('result2',result2)
        if isinstance(result2,int):
            print('result25',result2)
            # 成功,则读取所有项目及目录信息并返回: result3: 项目 ，resukt4: 目录
            return await fetchAllProjects(currentpage=1, pagesize=10 ,returnTotalCount=True)
        else: 
            return result2
    else:
        return result1

async def fetchTable (dbName,collectionName,xfilter={},xshown={},xsort=[],currentpage=1, pagesize=10, returnTotalCount=True):
    # 1 读取所有项目数目
    if returnTotalCount:
        result1 = await findCount(dbName,collectionName,xfilter)
    else:
        result1 = ''
    # 2 读取所有的表信息
    skipValue = (currentpage -1) * pagesize
    limitValue = pagesize
    print('skipValue',skipValue,limitValue)
    result2 =  json.loads(await find(dbName,collectionName,xfilter=xfilter,xshown=xshown,xsort=xsort,skipValue = skipValue, limitValue = limitValue))
    # 添加 ID
    initID = 1
    for ele in result2:
        ele['id'] = skipValue + initID
        initID += 1
    #print('xxxx',result2)
    return ({'count':result1,'content':result2})

#async def fetchTable (dbName,collectionName,xfilter={},xshown={},xsort=[],currentpage=1, pagesize=10, returnTotalCount=True):
#    # 1 读取所有项目数目
#    if returnTotalCount:
#        result1 = await findCount(dbName,collectionName,xfilter)
#        print(f'{dbName}=>{collectionName}符合条件的项目总数为:{result1}')
#    else:
#        result1 = ''
#    # 2 读取所有的表信息
#    skipValue = (currentpage -1) * pagesize
#    limitValue = pagesize
#    print('skipValue',skipValue,limitValue)
#    result2 = json.loads(await find(dbName,collectionName,xfilter,xshown,xsort,skipValue = skipValue, limitValue = limitValue))
#    for element in result2:
#        projectname = element['projectName']
#        projectid = element['_id']
#        print(projectid)
#        # 获取该 项目中的目录信息
#        category = await find(dbPrefix + '-' +projectid['$oid'], 'Categories')
#        element['categories'] = json.loads(category)
#        # print(element)
#    return ({'count':result1,'content':result2})


async def updateProject(dbName,collectionName,queryDict,setDict):
    #print(setDict)
    
    # 1- 更新特定醒目名称信息
    result1 = await update_one(dbName,collectionName,queryDict,setDict)
    if result1 == 1:
        # 修改 项目数据库列表成功
        result2 = await fetchAllProjects(currentpage=1, pagesize=10 ,returnTotalCount=True)
        return (result2)
    else:
        return 'error'

async def deleteProject(dbName,collectionName,queryDict):
    projectId = queryDict['_id']
    # 1: 删除项目列表中的 项目名称
    result1 = await delete_one(dbName,collectionName,queryDict)
    if result1 == 1:
        # step1 修改成功
        # 2: 删除项目数据库
        projectid = json.loads(json_util.dumps(projectId))['$oid']
        result2 = await drop_database(dbPrefix + '-' + projectid)
        if not result2:
            # 删除数据库成功
            # 3- 拉取所有数据
            result3 = await fetchAllProjects(currentpage=1, pagesize=10 ,returnTotalCount=True)
            return (result3)
        else:
            return ('error')
    else:
        return ('error')


async def updateCategory(dbName,collectionName,queryDict,setDict):
    # 更新特定项目中的 目录
    # 1- 更新 对应项目，分类表中的数据
    result1 = await update_one(dbName,collectionName,queryDict,setDict)
    if result1 == 1:
        # 1- 修改 项目数据库列表成功
        # 2- 拉取所有数据
        result2 = await fetchAllProjects()
        return (result2)
    else:
        return 'error'


async def deleteCategory(dbName,collectionName,queryDict):
    # 1: 删除项目列表中的 项目名称
    result1 = await delete_one(dbName,collectionName,queryDict)
    if result1 == 1:
        # 2- 拉取所有数据
        result2 = await fetchAllProjects()
        return (result2)
    else:
        return ('error')

async def createCategory(dbName,collectionName,setDict):
    # 创建 目录
    result1 = await insert_one(dbName,collectionName,setDict)
    if len(result1) == 1:
        # 创建成功
        result2 = await fetchAllProjects(currentpage=1, pagesize=10 ,returnTotalCount=True)
        return (result2)
    else:
        return ('error')


async def handleSignup(dbName,collectionName,accountInfo):
    # 1- 检查账号是否已经注册，如果已注册，报错返回
    result1 = await find_one(dbName,collectionName,queryDict={'account':accountInfo['account']})
    print(result1)
    if result1 == 'null':
        # 2- 没有注册,现在来注册
        print("用户未注册")
        result2 = await insert_one(dbName,collectionName,accountInfo)
        print('result2',result2)
        if len(result2) == 1:
            # 用户信息保存成功
            return ('注册成功')
        else:
            return ('error')
    else: 
        # 账号已经注册
        print("用户已注册")
        return 'error:账号已注册'

async def handleSignin(dbName,collectionName,accountInfo):
    # 1-1 检查账号是否存在
    result1 = await find_one(dbName,collectionName,queryDict={'account':accountInfo['account']})
    if result1 == 'null':
        return ('error:用户未注册')
    else:
        # 用户已注册
        # 1-2 如果存在，检查账号密码是否一致
        result2 = await find_one(dbName,collectionName,queryDict={'account':accountInfo['account'],'shadow': accountInfo['shadow']})
        if result2 == 'null':
            return ('error:密码错误')
        else:
            # 3 获取用户 部门信息
            result3 = await find_one(dbName,collectionName,queryDict={'account':accountInfo['account']},showDict={'_id':0,'department': 1})
            #print(json.loads(result3),type(json.loads(result3)))
            if result3 == 'null':
                return ('error:没找到部门信息')
            else:
                return (json.loads(result3)['department'])



# Urls related high level functions

async def createUrlItems(dbName,collectionName,ItemInfos):
    # 直接使用 insert_many
    result1 = await insert_many(dbName,collectionName,ItemInfos)
    if isinstance(result1,int):
        print('插入成功')
        # 获取所有数据(首页) 返回
        # result2 = await fetchAllProjects(currentpage=1, pagesize=10 ,returnTotalCount=True)
        result2 = await fetchTable (dbName,collectionName,xfilter={},xshown={},xsort=[],currentpage=1, pagesize=10, returnTotalCount=True)
        return (result2)
    else:
        return('error')

async def findProjectIdFromProjectName(dbName,collectionName,queryDict={},showDict={}):
    result1 = json.loads(await find_one(dbName,collectionName,queryDict,showDict))
    #print('result1',result1['_id']['$oid'])
    projectId = result1['_id']['$oid']
    return projectId

async def fetchUrlItems(dbName,collectionName,currentpage = 1, pagesize = 10,returnTotalCount=True):
    # 获取 特定项目 Url表中符合条件的数据
    result1 = await fetchTable(dbName,collectionName,xfilter={},currentpage=currentpage, pagesize=pagesize, returnTotalCount=True)
    #print(result1,type(result1))
    return result1