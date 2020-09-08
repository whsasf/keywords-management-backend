from fastapi import APIRouter, HTTPException, Path
from pydantic import BaseModel
import json
from typing import List, Optional, Dict
from datetime import date, datetime, time, timedelta
import time
from bson import ObjectId
from database.db_advanced import createUrlItems, findProjectIdFromProjectName,fetchUrlItems

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
async def create_category(*,projectName: str = Path(...),urlsItemInfos:List[UrlsItemInfo]):
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
async def create_category(*,projectName: str = Path(...), currentPage: int = 1, pageSize: int =10):
    # 查询 url表中的数据
    #print(projectName, currentPage,pageSize)
    # projectName 转 projectId
    projectId = await findProjectIdFromProjectName(dbPrefix,'Project',queryDict={'projectName': projectName},showDict={'_id':1})
    print(projectId)

    result = await fetchUrlItems(dbPrefix+'-'+projectId,'Urls',currentpage=currentPage,pagesize=pageSize)
    return (result)
