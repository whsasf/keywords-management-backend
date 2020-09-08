from fastapi import APIRouter, HTTPException, Path
from pydantic import BaseModel
import json
from typing import List, Optional
from datetime import date, datetime, time, timedelta
import time
from bson import ObjectId
from database.db_advanced import updateCategory, deleteCategory, createCategory

router = APIRouter()
dbPrefix = 'KWM'

class UpdateCategoryInfo(BaseModel):
    # UpdateCategory body数据模型
    categoryName: str


class CreateCategoryInfo(BaseModel):
    # createCategory body数据模型
    categoryName: str


@router.patch("/{projectName}/{categoryId}")
async def update_category(*,projectName,categoryId: str = Path(...), updateCategoryInfo: UpdateCategoryInfo):
    # 修改特定数据库中的分类
    # print(projectName,categoryId,updateCategoryInfo.dict())
    
    queryDict = {'_id': ObjectId(categoryId)}
    setDict = updateCategoryInfo.dict()
    setDict = {"$set": setDict }
    result = await updateCategory(dbPrefix+'-'+projectName,'Categories',queryDict,setDict)
    return (result)

@router.delete("/{projectId}/{categoryId}")
async def delete_category(*,projectId,categoryId: str = Path(...)):
    # 删除特定项目中的特定目录: 
    # print(projectName,categoryId)
    queryDict = {'_id': ObjectId(categoryId)}
    result = await deleteCategory(dbPrefix+'-'+projectId,'Categories',queryDict)
    return (result)

@router.post("/{projectId}")
async def create_category(*,projectId: str = Path(...),createCategoryInfo:CreateCategoryInfo):
    # 特定项目中，添加特定目录: 
    # print(projectName,createCategoryInfo.dict())
    setDict = createCategoryInfo.dict()
    result = await createCategory(dbPrefix+'-'+projectId,'Categories',setDict)
    return (result)
