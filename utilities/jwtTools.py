import jwt
import datetime
import json 

# 请求会向 dic 里面插入 'data' 字段, 内容为用户姓名

async def createJWT(newdata):
    secretKey = 'd261ea8ca4efb56c04f4d52333b217e515ea98718ef030e3e4d040dfdc8ec889'
    payload = {
        'exp': datetime.datetime.now() + datetime.timedelta(hours=1),  # jwt过期时间1小时
        'iat': datetime.datetime.now(),
        'iss': 'dianbaobao',  # 签名
    } 

    payload['data'] = newdata
    token = jwt.encode(payload, secretKey, algorithm='HS256')
    return (token)


async def verifyJWT(payload):
    secretKey = 'd261ea8ca4efb56c04f4d52333b217e515ea98718ef030e3e4d040dfdc8ec889'
    try:
        jwt.decode(payload, secretKey, issuer='dianbaobao', algorithms=['HS256'])
    except jwt.exceptions.ExpiredSignatureError as e:
        print(e)
        return 'expired'
    except Exception as e:
        print(e)
        return (e)
