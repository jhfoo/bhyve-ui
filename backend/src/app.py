# core
import re
import json
# community
from typing import Union
from fastapi import FastAPI
from fastapi.responses import PlainTextResponse
from fabric import Connection
from asyncio import Future
import asyncio
import asyncssh

app = FastAPI()

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
  hosts = ['192.168.88.7','192.168.88.10','192.168.88.3']

  ret = []
  for host in hosts:
    conn = await asyncssh.connect(host, known_hosts=None)
    resp = await conn.run('sudo vm list')
    lines = resp.stdout.split('\n')
    FirstLine = lines.pop(0)
    (OrderedFieldNames, FieldProperties) = parseTableHeader(FirstLine)
    print (FieldProperties)

    VmList = []
    for line in lines:
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

@app.get("/")
def read_root():
  return {"Hello": "World"}


@app.get("/items/{item_id}")
def read_item(item_id: int, q: Union[str, None] = None):
  return {"item_id": item_id, "q": q}