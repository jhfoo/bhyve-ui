# core
import re
import json
# community
from typing import Union
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import PlainTextResponse
from fabric import Connection
from asyncio import Future
import asyncio
import asyncssh

app = FastAPI()
app.add_middleware(
  CORSMiddleware,
  allow_origins = ['*'],
  allow_credentials = True,
  allow_methods = ['*'],
  allow_headers = ['*']
)

hosts = [
  '192.168.88.7',
  '192.168.88.10',
  '192.168.88.3'
]

def parseTableHeader(HeaderStr):
  matches = re.findall('(\S+\s*)', HeaderStr)

  OrderedFieldNames = []
  FieldProperties = {}
  StartIndex = 0
  for match in matches:
    FieldName = match.strip()
    OrderedFieldNames.append(FieldName)

    FieldProperties[FieldName] = {
      'StartIndex': StartIndex,
      'length': StartIndex + len(match),
      'isLast': False,
    }
    StartIndex += len(match)

  FieldProperties[OrderedFieldNames[-1]]['isLast'] = True

  return (OrderedFieldNames, FieldProperties)

@app.get("/api/bhyve/vm/list", response_class=PlainTextResponse)
async def getVmList():
  print ('getVmList: SSHing')
  
  ret = []
  for host in hosts:
    print (f'Connecting to {host}...')
    conn = await asyncssh.connect(host, known_hosts=None)
    resp = await conn.run('sudo vm list')
    lines = resp.stdout.split('\n')
    FirstLine = lines.pop(0)
    (OrderedFieldNames, FieldProperties) = parseTableHeader(FirstLine)
    print (FieldProperties)

    VmList = []
    for line in lines:
      if len(line) > 0:
        VmInfo = {}
        for FieldName in OrderedFieldNames:
          if FieldProperties[FieldName]['isLast']:
            VmInfo[FieldName] = line[FieldProperties[FieldName]['StartIndex']:].strip()
          else:
            VmInfo[FieldName] = line[FieldProperties[FieldName]['StartIndex']:FieldProperties[FieldName]['length']].strip()
        VmList.append(VmInfo)

    ret.append({
      "host": host,
      "vms": VmList
    })

  return json.dumps(ret, indent=2)

@app.get("/api/bhyve/vm/destroy", response_class=PlainTextResponse)
async def unlockVm(host: str, vm: str):
  conn = await asyncssh.connect(host, known_hosts=None)
  resp = await conn.run(f'sudo vm destroy -f {vm}')
  print (resp)
  return {
    'message': resp.stdout,
    'code': resp.returncode
  }

@app.get("/api/bhyve/vm/unlock", response_class=PlainTextResponse)
async def unlockVm(host: str, vm: str):
  conn = await asyncssh.connect(host, known_hosts=None)
  resp = await conn.run(f'sudo rm /zroot/vm/{vm}/run.lock')
  print (resp)
  return resp.stdout

@app.get("/api/bhyve/vm/start")
async def stopVm(host: str, vm: str):
  print ('startVm: SSHing')

  conn = await asyncssh.connect(host, known_hosts=None)
  resp = await conn.run(f'sudo vm start {vm}')

  return {
    'message': resp.stdout,
    'code': resp.returncode
  }

@app.get("/api/bhyve/vm/stop")
async def stopVm(host: str, vm: str):
  print ('stopVm: SSHing')

  try:
    conn = await asyncssh.connect(host, known_hosts=None)
    resp = await conn.run(f'sudo vm stop {vm}')
    return {
      'message': resp.stdout,
      'code': resp.returncode
    }
  except Exception as err:
    return err

@app.get("/")
def read_root():
  return {"Hello": "World"}


@app.get("/items/{item_id}")
def read_item(item_id: int, q: Union[str, None] = None):
  return {"item_id": item_id, "q": q}