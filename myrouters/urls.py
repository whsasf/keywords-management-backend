from fastapi import APIRouter, HTTPException, Path
from pydantic import BaseModel
import json
from typing import List, Optional, Dict
from datetime import date, datetime, time, timedelta
import time
from bson import ObjectId
from bson import json_util
from database.db_advanced import createUrlItems, findProjectIdFromProjectName,fetchUrlItems,updateUrlItems, deleteUrlItems

router = APIRouter()
dbPrefix = 'KWM'

class UrlExcludePath(BaseModel):
    path: str
    type: str

class UrlsItemInfo(BaseModel):
    # UpdateCategory body数据模型
    rootUrl: str
    category: List[str]
    status: str
    urlExcludePath: List
    urlIncludePath: List

#@router.patch("/{projectName}/{categoryId}")
#async def update_category(*,projectName,categoryId: str = Path(...), updateCategoryInfo: UpdateCategoryInfo):
#    # 修改特定数据库中的分类
#    # print(projectName,categoryId,updateCategoryInfo.dict())
#    
#    queryDict = {'_id': ObjectId(categoryId)}
#    setDict = updateCategoryInfo.dict()
#    setDict = {"$set": setDict }
#    result = await updateCategory(dbPrefix+'-'+projectName,'Categories',queryDict,setDict)
#    return (result)
#
#@router.delete("/{projectId}/{categoryId}")
#async def delete_category(*,projectId,categoryId: str = Path(...)):
#    # 删除特定项目中的特定目录: 
#    # print(projectName,categoryId)
#    queryDict = {'_id': ObjectId(categoryId)}
#    result = await deleteCategory(dbPrefix+'-'+projectId,'Categories',queryDict)
#    return (result)

@router.post("/{projectName}")
async def create_url(*,projectName: str = Path(...),urlsItemInfos:List[UrlsItemInfo]):
    # Url表中添加 数据 
    print(projectName, urlsItemInfos)
    urlsItemInfos = [urlsItem.dict() for urlsItem in urlsItemInfos]
    # 添加时间戳
    for urlItem in urlsItemInfos:
        urlItem['modifiedTime'] = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
    # projectName 转 projectId
    projectId = await findProjectIdFromProjectName(dbPrefix,'Project',queryDict={'projectName': projectName},showDict={'_id':1})
    result1 = await createUrlItems(dbPrefix+'-'+projectId,'Urls',urlsItemInfos)
    return (result1)



@router.get("/{projectName}")
async def get_urls(*,projectName: str = Path(...), keyword: Optional[str] = None , currentPage: int = 1, pageSize: int =10):
    # 查询 url表中的数据
    # print(projectName, keyword, currentPage,pageSize)
    # projectName 转 projectId
    projectId = await findProjectIdFromProjectName(dbPrefix,'Project',queryDict={'projectName': projectName},showDict={'_id':1})
    print(projectId)

    # 配置 queryDict 和 showDict ，依据 目的的不同
    if keyword == None:
        # 无关键词查询
        queryDict={}
        shownDict={}
    else:
        # 有关键词查询
        queryDict={'rootUrl':{'$regex':keyword,'$options':'i'}}  # 查询包含，且不区分大小写
        shownDict={'_id':1,'rootUrl':1}
    # print('queryDict',queryDict,shownDict)
    result = await fetchUrlItems(dbPrefix+'-'+projectId,'Urls',xfilter=queryDict,xshown =shownDict,  currentpage=currentPage,pagesize=pageSize)

    print(result)
    return (result)

@router.put("/{projectName}/{urlID}")
async def update_url(*,projectName,urlID : str = Path(...),urlsItemInfo:UrlsItemInfo):
    # Url表中添加 数据 
    # print(projectName, urlID, urlsItemInfo)
    urlsItemInfo = urlsItemInfo.dict()
    # 添加时间戳
    urlsItemInfo['modifiedTime'] = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
    # projectName 转 projectId
    projectId = await findProjectIdFromProjectName(dbPrefix,'Project',queryDict={'projectName': projectName},showDict={'_id':1})
    #result1 = await createUrlItems(dbPrefix+'-'+projectId,'Urls',urlsItemInfos)
    
    # 生成urlID, 构造 querydict
    urlID = ObjectId(urlID)
    # print('urlID',urlID)
    result1 = await updateUrlItems(dbPrefix+'-'+projectId,'Urls',queryDict={"_id":urlID},setDict={"$set":urlsItemInfo})
    return (result1)


@router.delete("/{projectName}")
async def delete_url(*,projectName: str = Path(...),urlID: List[str]):
    # 查询 url表中的数据,有可能有多个
    print(projectName, urlID)
    # projectName 转 projectId
    projectId = await findProjectIdFromProjectName(dbPrefix,'Project',queryDict={'projectName': projectName},showDict={'_id':1})
    deleteDictList = []
    for url in urlID:
        deleteDict = {'_id': ObjectId(url)}
        deleteDictList.append(deleteDict)
    result = await deleteUrlItems(dbPrefix+'-'+projectId,'Urls',deleteDictList)
    return (result)