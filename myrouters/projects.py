from fastapi import APIRouter, HTTPException, Path
from pydantic import BaseModel
import json
from typing import List, Optional
from datetime import date, datetime, time, timedelta
import time
from bson import ObjectId
from database.db_advanced import createnewproject, fetchAllProjects,updateProject

router = APIRouter()

class Category(BaseModel):
    categoryName: str = None
class Project(BaseModel):
    #create_project 请求body数据模型
    projectName: str
    creater: str
    categories: List[Category] = None

class UpdateProjectInfo(BaseModel):
    # update_project body数据模型
    before: str
    after: str

@router.post("/")
async def create_project(project: Project):
    # 操作流程:
    # 1. 插入时间戳
    # 2: 将项目名称 写入 keywordsManagement ->Project 表
    # 3: 将项目对应分类列表写入 项目名 -> Categories 表
    # 应该返回全部的 projects-> categories 对象
    # [{projectname: 'xx',creater: '', timestamp: '',categories:[1,2,3]},{},{}]
    
    #1 插入时间戳
    projectnew = project.dict()
    projectnew['timestamp'] = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()) #getBJTime()
    #print(project.dict())
    #2 写入数据库
    result = await createnewproject('keywordsManagement','Project',projectnew)
    #print(result)
    if result:
        if result == 'duplicateError-projectName':
            # 重复项目
            raise HTTPException(status_code=500, detail="重复项目,请检查!")
        elif result == 'duplicateError-categoryName':
            # 重复目录 
            raise HTTPException(status_code=500, detail="目录目录,请检查!")
        else:
            #成功,并返回所有项目数据
            return (result)
        #else:
        #    raise HTTPException(status_code=503, detail="服务端错误!")

@router.get("/")
async def fetch_project():
    # 默认返回 所有项目数据
    result = await fetchAllProjects()
    return (result)


@router.patch("/{projectId}")
async def update_project(*,projectId: str = Path(...), updateProjectInfo: UpdateProjectInfo):
    # 修改 项目名称，同时会触发修改 项目对应的 数据库的名称修改
    print('projectId',projectId,updateProjectInfo.dict())
    quertDict = {'_id': ObjectId(projectId)}
    setDict = {"$set": updateProjectInfo.dict() }
    result = await updateProject('keywordsManagement','Project',quertDict,setDict)
    return (result)


