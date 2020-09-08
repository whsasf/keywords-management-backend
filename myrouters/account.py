from fastapi import APIRouter, HTTPException, Path
from pydantic import BaseModel
import json
from typing import List, Optional
from datetime import date, datetime, time, timedelta
import time
from bson import ObjectId
from database.db_advanced import handleSignup,handleSignin
router = APIRouter()
dbPrefix = 'KWM'

class SignInAccountInfo(BaseModel):
    account: str
    shadow: str

class AccountInfo(BaseModel):
    account: str
    shadow: str
    department: str

@router.post("/Signup")
async def Signup(accountinfo:AccountInfo):
    #print(accountinfo)
    result = await handleSignup(dbPrefix,'User',accountinfo.dict())
    if 'error' in result.lower():
        raise HTTPException(status_code=402, detail=result)
    else:
        return (result)

@router.post("/Signin")
async def Signin(signInAccountInfo:SignInAccountInfo):
    #print(signInAccountInfo.dict())
    #处理用户登录
    result = await handleSignin(dbPrefix,'User',signInAccountInfo.dict())
    if 'error' in result.lower():
        raise HTTPException(status_code=403, detail=result)
    else:
        return ({'department':result})

@router.post("/Signout")
async def Signout():
    #处理用户登录
    pass
