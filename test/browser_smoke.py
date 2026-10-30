import os, subprocess, time, json
from playwright.sync_api import sync_playwright
root=os.path.dirname(os.path.dirname(__file__))
p=subprocess.Popen(['python','-m','http.server','8765','--directory',root],stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL)
try:
 time.sleep(1)
 with sync_playwright() as pw:
  browser=pw.chromium.launch(headless=True,executable_path='/usr/bin/chromium',args=['--no-sandbox'])
  page=browser.new_page(viewport={'width':1450,'height':950},device_scale_factor=1)
  sample={'items':[{'id':'fr:2026-12345','type':'PRORULE','stage':'Proposed rule','title':'Housing assistance public proposal','summary':'Proposed federal housing regulation','date':'2026-10-29','agency':'Department of Housing','url':'https://www.federalregister.gov/d/2026-12345','source':'Federal Register','scope':'Nationwide • not ZIP-specific','level':'federal','rins':['2026-AA01']},{'id':'fr:2026-12344','type':'RULE','stage':'Final rule','title':'Housing assistance final rule','summary':'Final federal housing regulation','date':'2026-10-28','agency':'Department of Housing','url':'https://www.federalregister.gov/d/2026-12344','source':'Federal Register','scope':'Nationwide • not ZIP-specific','level':'federal','rins':['2026-AA01']}], 'services':{'federal':'live','state':'not configured'},'updatedAt':'2026-10-30T14:00:00.000Z'}
  def route(req):
   if 'action=zip' in req.request.url: req.fulfill(status=200,content_type='application/json',body=json.dumps({'zip':'10001','city':'New York','state':'NY','stateName':'New York'}))
   else:req.fulfill(status=200,content_type='application/json',body=json.dumps(sample))
  page.route('**/api/data?*',route)
  errors=[];page.on('pageerror',lambda err:errors.append(str(err)))
  page.set_content(open(os.path.join(root,'index.html')).read().replace('<script type="module" src="/app.js"></script>',''))
  page.add_style_tag(content=open(os.path.join(root,'styles.css')).read().split(';',1)[1])
  page.evaluate("window.fetch = async (url) => new Response(JSON.stringify(String(url).includes('action=zip') ? {zip:'10001',city:'New York',state:'NY',stateName:'New York'} : {items:[{id:'fr:1',type:'PRORULE',stage:'Proposed rule',title:'Housing proposed rule',summary:'A housing proposal',date:'2026-10-29',agency:'Agency',url:'https://www.federalregister.gov/d/1',source:'Federal Register',scope:'Nationwide',level:'federal',rins:['2026-AA01']},{id:'fr:2',type:'RULE',stage:'Final rule',title:'Housing final rule',summary:'A housing final rule',date:'2026-10-28',agency:'Agency',url:'https://www.federalregister.gov/d/2',source:'Federal Register',scope:'Nationwide',level:'federal',rins:['2026-AA01']}],services:{federal:'live'},updatedAt:'2026-10-30T14:00:00.000Z'}), {status:200,headers:{'content-type':'application/json'}})")
  page.add_script_tag(content=open(os.path.join(root,'app.js')).read())
  page.get_by_role('heading',name='Your civic dashboard').wait_for()
  page.locator('#policyStat').get_by_text('2').wait_for()
  page.screenshot(path='/mnt/data/civicscope-preview.png',full_page=True)
  page.locator('#sampleZip').click();page.get_by_text('New York, New York',exact=True).wait_for()
  page.get_by_role('button',name='Policy explorer',exact=False).first.click()
  page.locator('#fullPolicyList .policy-item').first.wait_for()
  assert page.locator('#fullPolicyList .policy-item').count()==2
  page.locator('#fullPolicyList [data-save]').first.click()
  assert page.locator('#savedStat').inner_text()=='1'
  page.get_by_role('button',name='Policy comparison',exact=False).click()
  assert page.locator('.comparison-pair .compare-card').count()==2
  page.get_by_role('button',name='Saved & alerts',exact=False).click()
  assert page.locator('#savedList .policy-item').count()==1
  page.set_viewport_size({'width':390,'height':844})
  page.screenshot(path='/mnt/data/civicscope-mobile-preview.png',full_page=True)
  assert not errors,errors
  browser.close()
  print('PASS: desktop render, API responses, ZIP update, policy list, save, compare, saved, mobile viewport; no JS page errors')
finally:p.terminate();p.wait()
