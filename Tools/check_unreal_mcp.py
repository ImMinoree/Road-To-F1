"""Read-only native MCP handshake, discovery and selected tool verification."""
import json,urllib.request,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];OUT=ROOT/'Evidence/UnrealMCP';OUT.mkdir(exist_ok=True)
url='http://127.0.0.1:8000/mcp';headers={'Content-Type':'application/json','Accept':'application/json, text/event-stream'};serial=0
def rpc(method,params=None,notification=False):
 global serial
 serial+=1;body={'jsonrpc':'2.0','method':method}
 if not notification:body['id']=serial
 if params is not None:body['params']=params
 request=urllib.request.Request(url,json.dumps(body).encode(),headers,method='POST')
 with urllib.request.urlopen(request,timeout=30) as response:
  if response.headers.get('Mcp-Session-Id'):headers['Mcp-Session-Id']=response.headers['Mcp-Session-Id']
  data=response.read().decode()
 if not data:return None
 if data.startswith('event:') or data.startswith('data:'):data=next(line[5:].strip() for line in data.splitlines() if line.startswith('data:'))
 result=json.loads(data)
 if 'error' in result:raise RuntimeError(result['error'])
 return result.get('result')
initialized=rpc('initialize',{'protocolVersion':'2025-11-25','capabilities':{},'clientInfo':{'name':'codex-unreal-setup-verifier','version':'1.0'}})
headers['Mcp-Protocol-Version']=initialized['protocolVersion'];rpc('notifications/initialized',notification=True)
tools=rpc('tools/list',{});report={'initialize':initialized,'native_tools':tools}
name=sys.argv[1] if len(sys.argv)>1 else 'list_toolsets';arguments=json.loads(sys.argv[2]) if len(sys.argv)>2 else {}
result=rpc('tools/call',{'name':name,'arguments':arguments});report['tool_call']={'name':name,'arguments':arguments,'result':result}
assert not result.get('isError',False),result
suffix='_'+arguments.get('tool_name','') if name=='call_tool' else ''
file=OUT/('probe_'+name+suffix+'.json');file.write_text(json.dumps(report,indent=2),encoding='utf-8')
print(json.dumps({'server':initialized.get('serverInfo'),'protocol':initialized['protocolVersion'],'native_tool_names':[t['name'] for t in tools['tools']],'call':name,'result':result},ensure_ascii=False)[:10000])
