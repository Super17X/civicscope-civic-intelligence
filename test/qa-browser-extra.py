import os, subprocess, time, json
from playwright.sync_api import sync_playwright
root=os.path.dirname(os.path.dirname(__file__))
server=subprocess.Popen(['python','-m','http.server','8766','--bind','127.0.0.1','--directory',root],stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL)
sample={'items':[{'id':'fr:proposed','title':'Housing reform proposed rule','type':'PRORULE','stage':'Proposed rule','summary':'Affordable housing program','date':'2026-10-28','agency':'Agency','url':'https://www.federalregister.gov/d/example','source':'Federal Register','scope':'Nationwide • not ZIP-specific','level':'federal','rins':['2026-AA01']},{'id':'fr:final','title':'Housing reform final rule','type':'RULE','stage':'Final rule','summary':'Housing program implemented','date':'2026-10-30','agency':'Agency','url':'https://www.federalregister.gov/d/final','source':'Federal Register','scope':'Nationwide • not ZIP-specific','level':'federal','rins':['2026-AA01']}],'services':{'federal':'live','state':'not configured','congress':'not configured'},'updatedAt':'2026-10-30T19:00:00.000Z'}
errors=[]
try:
 time.sleep(1)
 with sync_playwright() as pw:
  browser=pw.chromium.launch(headless=True,executable_path='/usr/bin/chromium',args=['--no-sandbox'])
  context=browser.new_context(viewport={'width':1365,'height':900})
  page=context.new_page();page.on('pageerror',lambda e:errors.append(str(e)))
  hits={'policies':0,'zip':0}
  def route(r):
   url=r.request.url
   if 'action=zip' in url:
    hits['zip']+=1
    r.fulfill(status=200,content_type='application/json',body=json.dumps({'zip':'10001','city':'New York','state':'NY','stateName':'New York'}))
   else:
    hits['policies']+=1
    r.fulfill(status=200,content_type='application/json',body=json.dumps(sample))
  def all_routes(r):
   u=r.request.url
   if '/api/data?' in u: return route(r)
   if u.endswith('/app.js'): return r.fulfill(status=200,content_type='application/javascript',body=open(root+'/app.js').read())
   if u.endswith('/styles.css'): return r.fulfill(status=200,content_type='text/css',body=open(root+'/styles.css').read())
   if u.startswith('https://civicscope.example/'): return r.fulfill(status=200,content_type='text/html',body=open(root+'/index.html').read())
   return r.abort()
  page.route('**/*',all_routes)
  resp=page.goto('https://civicscope.example/',wait_until='networkidle')
  assert resp.status==200
  assert page.get_by_role('heading',name='Your civic dashboard').is_visible()
  page.locator('#policyStat').get_by_text('2').wait_for()
  assert hits['policies']>=1
  page.locator('#sampleZip').click();page.get_by_text('New York, New York',exact=True).wait_for()
  assert hits['zip']==1
  page.get_by_role('button',name='Policy explorer',exact=False).first.click()
  assert page.locator('#fullPolicyList .policy-item').count()==2
  page.locator('#statusSelect').select_option('PRORULE')
  assert page.locator('#fullPolicyList .policy-item').count()==1
  page.locator('#policySearch').fill('nonexistent')
  assert page.locator('#fullPolicyList .policy-item').count()==0
  page.locator('#clearFilters').click();page.locator('#fullPolicyList .policy-item').first.wait_for()
  assert page.locator('#fullPolicyList .policy-item').count()==2
  page.locator('#fullPolicyList [data-save]').first.click()
  assert page.locator('#savedStat').inner_text()=='1'
  page.reload(wait_until='networkidle');page.locator('#policyStat').get_by_text('2').wait_for()
  assert page.locator('#savedStat').inner_text()=='1','Local storage persistence failed'
  page.get_by_role('button',name='Saved & alerts',exact=False).click()
  assert page.locator('#savedList .policy-item').count()==1
  page.set_viewport_size({'width':375,'height':812})
  assert page.evaluate('document.documentElement.scrollWidth <= window.innerWidth + 1'),f'horizontal overflow viewport={page.evaluate("innerWidth")}, width={page.evaluate("document.documentElement.scrollWidth")}'
  page.locator('#mobileMenu').click()
  assert page.locator('#mobileMenu').get_attribute('aria-expanded')=='true'
  assert not errors, errors
  print('PASS: served page, external JS/CSS, ZIP, filter, search, reset, watchlist persistence, reload, mobile menu, width, no JS errors; API requests mocked')
  print('Intercepted API calls:',hits)
  context.close();browser.close()
finally:
 server.terminate();server.wait()
