"""Offline consistency checks; optional anonymous legacy-catalog comparison."""
from pathlib import Path
import argparse,json,subprocess,sys,urllib.request
import yaml
from openapi_spec_validator import validate_spec
ROOT=Path(__file__).resolve().parents[1]
def check():
 parser=argparse.ArgumentParser();parser.add_argument('--live',action='store_true');args=parser.parse_args()
 m=json.loads((ROOT/'product.json').read_text());spec=yaml.safe_load((ROOT/'openapi.yaml').read_text());validate_spec(spec)
 assert m.get('status')!='retired','Retired products must not advertise active operations'
 assert m['base_url'].rstrip('/') in [x['url'].rstrip('/') for x in spec['servers']], 'API base URL differs'
 for name,ep in m.get('endpoints',{}).items():
  assert ep['method'].lower() in spec['paths'].get(ep['path'],{}),f'Endpoint mismatch: {name}'
 products=m.get('products',[])
 if m['mode']=='async' and products:
  props=spec['paths']['/v1/tasks']['post']['requestBody']['content']['multipart/form-data']['schema']['properties']
  codes={x.get('task_type',x.get('type')) for x in products}
  assert 'tg_username_full' not in codes,'Retired task type advertised'
  assert set(props['task_type']['enum'])==codes,'Supported task selectors differ'
  for p in products:
   code=p.get('task_type',p.get('type'));lo=p.get('min_numbers',p.get('min'));hi=p.get('max_numbers',p.get('max'))
   assert 0<lo<=hi and p['min_billable_numbers']>=0, f'Invalid limits: {code}'
   if 'x-product-limits' in spec:
    assert spec['x-product-limits'][code]=={'product_id':p['product_id'],'min_items':lo,'max_items':hi,'min_billable_numbers':p['min_billable_numbers']}, f'OpenAPI limits differ: {code}'
   fields=p.get('result_fields',p.get('fields'))
   declared=spec.get('x-result-csv-columns',{}).get(code)
   if declared is not None:assert declared==fields,f'CSV columns differ: {code}'
   row=spec.get('components',{}).get('schemas',{}).get('ResultRow',{})
   if len(products)==1 and 'x-csv-columns' in row:assert row['x-csv-columns']==fields,'CSV column order/case differs'
   # Ensure both human and machine-readable documentation state the reviewed bounds.
   expected=f'| `{code}` | {lo:,} | {hi:,} | {p["min_billable_numbers"]:,} |'
   for filename in ['README.md','llms.txt']:
    text=(ROOT/filename).read_text()
    if 'x-product-limits' in spec:assert expected in text,f'{filename} limits differ: {code}'
  if args.live:
   host='platform.numberchecker.ai' if m['brand']=='NumberChecker' else 'platform.checknumber.ai'
   with urllib.request.urlopen('https://'+host+'/api/products/configs',timeout=30) as r:catalog={x['id']:x for x in json.load(r)['products']}
   for p in products:
    c=catalog.get(p['product_id']);assert c is not None,f'Product removed: {p["product_id"]}'
    assert c['available'],f'Product unavailable: {p["product_id"]}'
    expected=(p.get('min_numbers',p.get('min')),p.get('max_numbers',p.get('max')),p['min_billable_numbers'])
    assert expected==(c['min_numbers'],c['max_numbers'],c['min_billable_numbers']),f'Live limits changed: {p["product_id"]}'
   print('Live legacy catalog matches; no task submitted.')
 elif args.live:print('Live catalog comparison unavailable for this API family; offline validation only.')
 test=ROOT/'tests/test_contract.py'
 if test.exists():subprocess.run([sys.executable,str(test)],cwd=ROOT,check=True)
 print('Contract checks passed.')
if __name__=='__main__':check()
