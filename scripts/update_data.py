#!/usr/bin/env python3
"""Descarga el catálogo estático de TFT y genera un JSON liviano para GitHub Pages."""
import json, datetime, pathlib, urllib.request
URL='https://raw.communitydragon.org/latest/cdragon/tft/es_ar.json'
ROOT=pathlib.Path(__file__).resolve().parents[1]
with urllib.request.urlopen(urllib.request.Request(URL,headers={'User-Agent':'TFTPlannerPersonal/0.2'}),timeout=90) as response:
    data=json.load(response)
sets=[s for s in data.get('setData',[]) if str(s.get('number'))=='18']
if not sets: raise ValueError('No se encuentra el Set 18; revisar manualmente la estructura antes de actualizar')
# Puede haber varios mutadores del mismo set; preferimos el principal y preservamos la variante elegida.
sets.sort(key=lambda s:(bool(s.get('mutator')), -len(s.get('champions',[]))))
s=sets[0]
items_by_api={str(i.get('apiName')):i for i in data.get('items',[])}
def compact_item(i):
 return {'id':str(i.get('apiName') or i.get('id') or ''),'name':i.get('name') or '', 'icon':i.get('icon') or '', 'desc':i.get('desc') or '', 'composition':[str(x) for x in (i.get('composition') or [])]}
def resolve(seq):
 out=[]
 for i in seq:
  ob=items_by_api.get(i) if isinstance(i,str) else i
  if isinstance(ob,dict) and ob.get('name'):
   out.append(compact_item(ob))
 return out
champs=[]
for c in s.get('champions',[]):
 if c.get('name') and isinstance(c.get('cost'),int) and 1<=c['cost']<=5 and c.get('traits') and not c.get('isSpawn'):
  champs.append({'id':c.get('apiName'), 'name':c['name'],'cost':c['cost'],'traits':c.get('traits',[]),'icon':c.get('icon') or c.get('squareIcon') or ''})
traits=[{'name':t.get('name') or '', 'apiName':t.get('apiName') or ''} for t in s.get('traits',[]) if isinstance(t,dict)]
augments=resolve(s.get('augments',[]))
items=resolve(s.get('items',[]))
# Algunos sets no incluyen todos los componentes en el listado específico.
if not items: items=[compact_item(x) for x in data.get('items',[]) if x.get('composition') and not x.get('isAugment')]
if not augments: raise ValueError('No se encontraron aumentos del set; revisar esquema')
if len(champs)<30 or len(items)<20: raise ValueError(f'Catálogo sospechosamente incompleto: {len(champs)} campeones, {len(items)} objetos')
out={'set':18,'name':s.get('name','Set 18'),'updated':datetime.datetime.now(datetime.timezone.utc).isoformat(timespec='seconds'),'source':URL,'champions':champs,'traits':traits,'items':items,'augments':augments}
(ROOT/'tft-data.json').write_text(json.dumps(out,ensure_ascii=False,separators=(',',':')),encoding='utf8')
print('Generado:',len(champs),'campeones,',len(items),'objetos,',len(augments),'aumentos')
