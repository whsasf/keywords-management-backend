from fastapi import APIRouter, HTTPException, Path
from pydantic import BaseModel
import json
from typing import List, Optional
from datetime import date, datetime, time, timedelta
import time
from bson import ObjectId
from database.db_advanced import createnewproject, fetchAllProjects,updateProject, deleteProject, fetchAllProjectsCount, updateCategory, deleteCategory, createCategory

router = APIRouter()
dbPrefix = 'KWM'

class Category(BaseModel):
    categoryName: str = None
class Project(BaseModel):
    # create_project 请求body数据模型
    projectName: str
    creater: str
    categories: List[Category] = None

class UpdateProjectInfo(BaseModel):
    # update_project body数据模型
    projectName: str

class UpdateCategoryInfo(BaseModel):
    # UpdateCategory body数据模型
    categoryName: str


class CreateCategoryInfo(BaseModel):
    # createCategory body数据模型
    categoryName: str


@router.post("/")
async def create_project(project: Project):
    # 操作流程:
    # 1. 插入时间戳
    # 2: 将项目名称 写入 keywordsManagement ->Project 表
    # 3: 将项目对应分类列表写入 项目名 -> Categories 表
    # 应该返回全部的 projects-> categories 对象
    # [{projectname: 'xx',creater: '', timestamp: '',categories:[1,2,3]},{},{}]
    
    # 1 插入时间戳
    projectnew = project.dict()
    projectnew['timestamp'] = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()) #getBJTime()
    # print(project.dict())
    # 2 写入数据库
    result = await createnewproject(dbPrefix,'Project',projectnew)
    # print(result)
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
        # else:
        #    raise HTTPException(status_code=503, detail="服务端错误!")

@router.get("/")
async def fetch_project(currentPage: int = 1, pageSize: int =10):
    # -返回 所有项目数据
    result = await fetchAllProjects(currentpage=currentPage, pagesize=pageSize ,returnTotalCount=True)
    return (result)


@router.patch("/{projectId}")
async def update_project(*,projectId: str = Path(...), updateProjectInfo: UpdateProjectInfo):
    # 修改 项目名称，同时会触发修改 项目对应的 数据库的名称修改
    # print('projectId',projectId,updateProjectInfo.dict())
    
    queryDict = {'_id': ObjectId(projectId)}
    setDict = updateProjectInfo.dict()
    # oldProjectName = setDict.pop('oldprojectName')
    #newProjectName = setDict['projectName']
    setDict = {"$set": setDict }
    result = await updateProject(dbPrefix,'Project',queryDict,setDict)
    return (result)

@router.delete("/{projectId}")
async def delete_project(*,projectId: str = Path(...)):
    # 删除项目: 
    print('projectId',projectId)
    
    queryDict = {'_id': ObjectId(projectId)}
    result = await deleteProject(dbPrefix,'Project',queryDict)
    return (result)



@router.patch("/{projectId}/Categories/{categoryId}")
async def update_category(*,projectId,categoryId: str = Path(...), updateCategoryInfo: UpdateCategoryInfo):
    # 修改特定数据库中的分类
    # print(projectName,categoryId,updateCategoryInfo.dict())
    
    queryDict = {'_id': ObjectId(categoryId)}
    setDict = updateCategoryInfo.dict()
    setDict = {"$set": setDict }
    result = await updateCategory(dbPrefix+'-'+projectId,'Categories',queryDict,setDict)
    return (result)

@router.delete("/{projectId}/Categories/{categoryId}")
async def delete_category(*,projectId,categoryId: str = Path(...)):
    # 删除特定项目中的特定目录: 
    # print(projectName,categoryId)
    queryDict = {'_id': ObjectId(categoryId)}
    result = await deleteCategory(dbPrefix+'-'+projectId,'Categories',queryDict)
    return (result)

@router.post("/{projectId}/Categories")
async def create_category(*,projectId: str = Path(...),createCategoryInfo:CreateCategoryInfo):
    # 特定项目中，添加特定目录: 
    # print(projectName,createCategoryInfo.dict())
    setDict = createCategoryInfo.dict()
    result = await createCategory(dbPrefix+'-'+projectId,'Categories',setDict)
    return (result)