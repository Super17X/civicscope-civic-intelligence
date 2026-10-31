"""Full new UI smoke test against a local static server; all upstream responses are mocked."""
import os, subprocess, time, json
from playwright.sync_api import sync_playwright
root=os.path.dirname(os.path.dirname(__file__))
p=subprocess.Popen(['python','-m','http.server','8771','--bind','127.0.0.1','--directory',root],stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL)
sample={'items':[{'id':'fr:1','type':'PRORULE','stage':'Proposed rule','title':'Housing assistance proposal','summary':'Proposed housing assistance policy','date':'2026-10-29','deadline':'2026-11-15','agency':'HUD','url':'https://www.federalregister.gov/d/2026-1111','source':'Federal Register','scope':'Nationwide • not ZIP-specific','level':'federal','rins':['1234-AA01']},{'id':'fr:2','type':'RULE','stage':'Final rule','title':'Housing assistance final rule','summary':'Adopted housing policy','date':'2026-10-30','effective':'2026-11-16','agency':'HUD','url':'https://www.federalregister.gov/d/2026-2222','source':'Federal Register','scope':'Nationwide • not ZIP-specific','level':'federal','rins':['1234-AA01']}], 'services':{'federal':'live','state':'not configured','congress':'not configured'}, 'updatedAt':'2026-10-30T18:00:00Z','nextPage':None}
try:
 time.sleep(1)
 with sync_playwright() as pw:
  browser=pw.chromium.launch(headless=True,executable_path='/usr/bin/chromium',args=['--no-sandbox'])
  page=browser.new_page(viewport={'width':1440,'height':900})
  errors=[];page.on('pageerror',lambda err:errors.append(str(err)))
  def api(route):
   url=route.request.url
   if 'action=zip' in url: obj={'zip':'10001','city':'New York','state':'NY','stateName':'New York'};status=200
   elif 'action=local' in url:obj={'items':[{'id':'nyc-zap:202','type':'LOCAL','stage':'Filed','title':'New York rezoning application','summary':'Planning filing','date':'2026-10-30','agency':'NYC Planning','url':'https://zap.planning.nyc.gov/projects','source':'NYC ZAP','scope':'NYC citywide • not ZIP verified','level':'local'}],'services':{'nycZoning':'live','nycCouncil':'requires token'},'coverage':'NYC citywide; not ZIP-specific'};status=200
   elif 'action=elections' in url:obj={'events':[{'title':'2026 federal general election','date':'2026-11-03','url':'https://www.fec.gov/','scope':'Nationwide','source':'FEC'}],'coverage':'National date only'};status=200
   elif 'action=history' in url:obj={'items':sample['items'],'coverage':'Matching RIN official records'};status=200
   elif '/api/assist' in url:obj={'answer':'Official records found. [1]','mode':'source-search','limits':'Nationwide only','citations':[{'title':'Housing assistance proposal','url':'https://www.federalregister.gov/d/2026-1111','stage':'Proposed rule','scope':'Nationwide','date':'2026-10-29'}]};status=200
   elif '/api/jurisdiction' in url:obj={'matchedAddress':'123 EXAMPLE ST, NEW YORK, NY','precision':'Census estimate only, not a precinct','source':'Census','geographies':[{'type':'Congressional Districts','name':'District 12','geoid':'3612'}]};status=200
   elif '/api/subscribe' in url:obj={'error':'Email alerts have not been activated.'};status=503
   else:obj=sample;status=200
   route.fulfill(status=status,content_type='application/json',body=json.dumps(obj))
  import re
  html=open(root+'/index.html').read()
  html=re.sub(r'<script type="module" src="/[^" ]+"></script>','',html)
  html=html.replace('<link rel="stylesheet" href="/styles.css" />','')
  page.set_content(html)
  page.add_style_tag(content=open(root+'/styles.css').read().split(';',1)[1])
  mocks={"policies":sample,"zip":{"zip":"10001","city":"New York","state":"NY","stateName":"New York"},"local":{"items":[{"id":"nyc-zap:202","type":"LOCAL","stage":"Filed","title":"New York rezoning application","summary":"Planning filing","date":"2026-10-30","agency":"NYC Planning","url":"https://zap.planning.nyc.gov/projects","source":"NYC ZAP","scope":"NYC citywide • not ZIP verified","level":"local"}],"services":{"nycZoning":"live","nycCouncil":"requires token"},"coverage":"NYC citywide; not ZIP-specific"},"elections":{"events":[{"title":"2026 federal general election","date":"2026-11-03","url":"https://www.fec.gov/","scope":"Nationwide","source":"FEC"}],"coverage":"National date only"},"history":{"items":sample['items'],"coverage":"Matching RIN official records"},"assist":{"answer":"Official records found. [1]","mode":"source-search","limits":"Nationwide only","citations":[{"title":"Housing assistance proposal","url":"https://www.federalregister.gov/d/2026-1111","stage":"Proposed rule","scope":"Nationwide","date":"2026-10-29"}]},"jurisdiction":{"matchedAddress":"123 EXAMPLE ST, NEW YORK, NY","precision":"Census estimate only, not a precinct","source":"Census","geographies":[{"type":"Congressional Districts","name":"District 12","geoid":"3612"}]}}
  page.evaluate("window.__mocks = "+json.dumps(mocks)+"; window.fetch = async (url,opts) => { let key= String(url).includes('/api/jurisdiction')?'jurisdiction':String(url).includes('/api/assist')?'assist':new URL(String(url),'https://civicscope.local').searchParams.get('action')||'policies'; const data=window.__mocks[key]||window.__mocks.policies; return new Response(JSON.stringify(data),{status:200,headers:{'Content-Type':'application/json'}}) };")
  page.add_script_tag(content=open(root+'/app.js').read(), type='module')
  page.add_script_tag(content=open(root+'/v2.js').read(), type='module')
  page.locator('#policyStat').get_by_text('2').wait_for()
  assert page.get_by_role('heading',name='Your civic dashboard').is_visible()
  assert page.locator('#daysToElection').inner_text() != '—'
  page.locator('#sampleZip').click();page.get_by_text('New York, New York',exact=True).wait_for()
  page.get_by_role('button',name='Local intelligence').click()
  page.locator('#localResults .policy-item').first.wait_for(timeout=6000)
  assert page.locator('#localResults .policy-item').count()==1
  page.get_by_role('button',name='Civic calendar').click()
  assert page.locator('#calendarResults .date-event').count()>=1
  page.get_by_role('button',name='Policy timeline').click()
  assert page.locator('#timelineResults .timeline-event').count()>=2
  page.get_by_role('button',name='Research assistant').click()
  page.locator('#researchQuestion').fill('What recent housing proposals were issued?')
  page.get_by_role('button',name='Research official documents').click()
  page.get_by_text('Official records found. [1]').wait_for()
  page.get_by_role('button',name='Verify district').click()
  page.locator('#streetAddress').fill('123 Example Street')
  page.locator('#addressConsent').check()
  page.get_by_role('button',name='Verify Census geography').click()
  page.get_by_text('District 12').wait_for()
  assert page.locator('#streetAddress').input_value()==''
  page.get_by_role('button',name='Policy comparison').click()
  page.locator('#rinInput').fill('1234-AA01')
  page.get_by_role('button',name='Search full RIN history').click()
  page.get_by_text('Matching RIN official records').wait_for()
  page.screenshot(path='/mnt/data/CivicScope_v2_desktop.png',full_page=True)
  page.set_viewport_size({'width':390,'height':844})
  page.screenshot(path='/mnt/data/CivicScope_v2_mobile.png',full_page=True)
  assert page.evaluate('document.documentElement.scrollWidth <= window.innerWidth + 2'), 'Mobile horizontal overflow'
  assert errors==[],f'Browser errors: {errors}'
  browser.close()
  print('PASS: live frontend scripts, ZIP, local intelligence, civic calendar, policy timeline, assistant, POST address, RIN search, mobile; no errors; all external API responses mocked')
finally:
 p.terminate();p.wait()
