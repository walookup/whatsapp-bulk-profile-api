"""Offline regression tests. Requests go only to a loopback mock with a synthetic key.

Run from this repository: python3 -m unittest discover -s tests -v
Python examples require requests; Node.js and Go checks run when available.
"""
from pathlib import Path
from email import policy
from email.parser import BytesParser
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
import contextlib, json, os, shutil, subprocess, sys, tempfile, threading, unittest

ROOT=Path(__file__).resolve().parents[1]
MANIFEST=json.loads((ROOT/'product.json').read_text())

class WireContract(unittest.TestCase):
    def run_client(self,language,mode='success',batch=False):
        state={'posts':0,'gets':0,'errors':[]}
        bulk=MANIFEST['mode']=='async-bulk'
        code=MANIFEST.get('product') if bulk else MANIFEST['products'][0]['type']
        class Handler(BaseHTTPRequestHandler):
            def log_message(self,*args):pass
            def reply(self,payload,status=200):
                data=json.dumps(payload,indent=2).encode()  # whitespace exposes brittle sed/grep parsing.
                self.send_response(status);self.send_header('Content-Type','application/json');self.send_header('Content-Length',str(len(data)));self.end_headers();self.wfile.write(data)
            def do_POST(self):
                state['posts']+=1
                try:
                    self.check_request()
                except Exception as error:
                    state['errors'].append(str(error));self.reply({'code':40000,'msg':str(error)},400);return
                if mode=='api_error':self.reply({'code':40000,'msg':'synthetic API-level error'});return
                if bulk:self.reply({'code':0,'msg':'ok','data':{'id':'mock-task','product':code,'status':'processing'}})
                elif batch:
                    identifiers=self.payload['identifiers']
                    self.reply({'code':0,'msg':'ok','data':{'service_type':code,'total':len(identifiers),'succeeded':1,'failed':len(identifiers)-1,'results':[{'identifier':identifiers[0],'exists':True,'registered':False},{'identifier':identifiers[1],'exists':False}]}})
                else:self.reply({'code':0,'msg':'ok','data':{'service_type':code,'identifier':self.payload.get('identifier','img:mock'),'registered':False}})
            def check_request(self):
                if self.headers.get('X-API-Key')!='test-local-only':raise ValueError('Expected the synthetic mock key')
                raw=self.rfile.read(int(self.headers.get('Content-Length',0)))
                if bulk:
                    if self.path!='/api/v1/bulk-tasks':raise ValueError('Wrong submit endpoint')
                    content=self.headers.get('Content-Type','')
                    message=BytesParser(policy=policy.default).parsebytes(('Content-Type: '+content+'\r\n\r\n').encode()+raw)
                    parts=list(message.iter_parts());names=[p.get_param('name',header='content-disposition') for p in parts]
                    expected=['service_type']+(['country'] if MANIFEST['requires_country'] else [])+['file']
                    if names!=expected:raise ValueError('Wrong multipart fields/order: '+repr(names))
                    values={p.get_param('name',header='content-disposition'):p.get_payload(decode=True) for p in parts}
                    if values['service_type'].decode()!=code:raise ValueError('Wrong product code')
                else:
                    expected='/api/v1/image/profile' if MANIFEST['mode']=='sync-image' else '/api/v1/batch-check' if batch else '/api/v1/check'
                    if self.path!=expected:raise ValueError('Wrong sync endpoint')
                    self.payload=json.loads(raw)
                    if self.payload.get('service_type')!=code or 'product' in self.payload:raise ValueError('Wrong public product code or request field')
                    if MANIFEST['mode']!='sync-image':
                        if ('identifiers' in self.payload)!=batch:raise ValueError('Wrong single/batch shape')
            def do_GET(self):
                state['gets']+=1
                if self.path!='/api/v1/bulk-tasks/mock-task':state['errors'].append('Wrong poll endpoint')
                data={'id':'mock-task','product':code,'status':'processing'}
                if mode=='failed':data.update(status='failed',reason='synthetic_failure')
                elif state['gets']>=2:
                    data.update(status='success',success_cnt=1,failure_cnt=0)
                    if state['gets']>=3:data['result_url']='https://example.invalid/synthetic.zip'
                self.reply({'code':0,'msg':'ok','data':data})
        server=ThreadingHTTPServer(('127.0.0.1',0),Handler)
        thread=threading.Thread(target=lambda:server.serve_forever(poll_interval=0.01),daemon=True);thread.start()
        try:
            with tempfile.TemporaryDirectory() as folder:
                cwd=Path(folder);(cwd/'examples').mkdir()
                for name in ['numbers.txt','emails.txt','usernames.txt']:(cwd/'examples'/name).write_text('14155550100\n')
                env=dict(os.environ);env[ROOT.parent.name.upper()+'_API_KEY']='test-local-only';env['API_BASE_URL']='http://127.0.0.1:'+str(server.server_port);env['MODE']='batch' if batch else 'single';env['GO111MODULE']='off'
                if language=='python':
                    source=next(ROOT.glob('examples/python/*.py'))
                    # Skip polling waits only in this isolated process; production scripts retain >=30s.
                    wrapper='import runpy,sys,time,requests\ntime.sleep=lambda _:None\noriginal=requests.sessions.Session.request\ndef checked(self,method,url,**kw):\n if "/batch-check" in url and kw.get("timeout",0)<300: raise RuntimeError("Batch timeout is too short")\n return original(self,method,url,**kw)\nrequests.sessions.Session.request=checked\nrunpy.run_path(sys.argv[1],run_name="__main__")'
                    command=[sys.executable,'-c',wrapper,str(source)]
                elif language=='nodejs':
                    source=next(ROOT.glob('examples/nodejs/*.js'))
                    command=['node','--input-type=module','-e','const original=setTimeout;globalThis.setTimeout=(fn,_delay,...args)=>original(fn,0,...args);await import(process.argv[1]);',source.as_uri()]
                elif language=='shell':
                    source=next(ROOT.glob('examples/shell/*.sh'));(cwd/'bin').mkdir();sleep=cwd/'bin/sleep';sleep.write_text('#!/bin/sh\nexit 0\n');sleep.chmod(0o755);env['PATH']=str(cwd/'bin')+os.pathsep+env['PATH'];command=['bash',str(source)]
                else:command=['go','run',str(next(ROOT.glob('examples/go/*.go')))]
                process=subprocess.run(command,cwd=cwd,env=env,capture_output=True,text=True,timeout=60)
                return process,state
        finally:server.shutdown();server.server_close();thread.join(timeout=2)

    def test_actual_clients_use_the_wire_contract(self):
        languages=['python']+(['nodejs'] if shutil.which('node') else [])
        if MANIFEST['mode']=='async-bulk':languages+=['shell']+(['go'] if shutil.which('go') else [])
        for language in languages:
            for batch in ([False,True] if MANIFEST['mode']=='sync-batch' else [False]):
                with self.subTest(language=language,batch=batch):
                    process,state=self.run_client(language,batch=batch)
                    self.assertEqual(process.returncode,0,process.stderr)
                    self.assertEqual(state['errors'],[])
                    self.assertEqual(state['posts'],1,'A missing download link must not trigger another submission')
                    if MANIFEST['mode']=='async-bulk' and language!='go':self.assertEqual(state['gets'],3)

    def test_api_error_is_not_a_successful_task(self):
        for language in ['python']+(['nodejs'] if shutil.which('node') else []):
            with self.subTest(language=language):
                process,state=self.run_client(language,mode='api_error')
                self.assertNotEqual(process.returncode,0)
                self.assertEqual(state['posts'],1)

    @unittest.skipUnless(MANIFEST['mode']=='async-bulk','Only asynchronous tasks have failed status')
    def test_failed_task_stops_without_resubmitting(self):
        for language in ['python','shell']+(['nodejs'] if shutil.which('node') else []):
            with self.subTest(language=language):
                process,state=self.run_client(language,mode='failed')
                self.assertNotEqual(process.returncode,0)
                self.assertEqual(state['posts'],1)
                self.assertEqual(state['gets'],1)

if __name__=='__main__':unittest.main()
