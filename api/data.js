// CivicScope serverless data adapter. No account, no stored address, no client-side API keys.
const TOPIC_TERMS = Object.freeze({
  all:'',housing:'housing',land:'land use',planning:'urban development',education:'education',
  transport:'transportation',law:'civil rights',environment:'environmental',taxes:'tax',
  health:'health care',safety:'public safety',jobs:'employment'
});
const STATE_NAMES=Object.freeze({AL:'Alabama',AK:'Alaska',AZ:'Arizona',AR:'Arkansas',CA:'California',CO:'Colorado',CT:'Connecticut',DE:'Delaware',DC:'District of Columbia',FL:'Florida',GA:'Georgia',HI:'Hawaii',ID:'Idaho',IL:'Illinois',IN:'Indiana',IA:'Iowa',KS:'Kansas',KY:'Kentucky',LA:'Louisiana',ME:'Maine',MD:'Maryland',MA:'Massachusetts',MI:'Michigan',MN:'Minnesota',MS:'Mississippi',MO:'Missouri',MT:'Montana',NE:'Nebraska',NV:'Nevada',NH:'New Hampshire',NJ:'New Jersey',NM:'New Mexico',NY:'New York',NC:'North Carolina',ND:'North Dakota',OH:'Ohio',OK:'Oklahoma',OR:'Oregon',PA:'Pennsylvania',RI:'Rhode Island',SC:'South Carolina',SD:'South Dakota',TN:'Tennessee',TX:'Texas',UT:'Utah',VT:'Vermont',VA:'Virginia',WA:'Washington',WV:'West Virginia',WI:'Wisconsin',WY:'Wyoming',PR:'Puerto Rico'});
export function isZip(zip){return typeof zip==='string' && /^\d{5}$/.test(zip)}
export function topicTerm(topic){return TOPIC_TERMS[topic] ?? null}
export function normalizeRegister(d){
 const type={PRORULE:'Proposed rule',RULE:'Final rule',NOTICE:'Notice'}[d.type]||'Other document';
 return {id:'fr:'+String(d.document_number||''),type:d.type||'OTHER',stage:type,title:String(d.title||'Untitled document'),summary:String(d.abstract||d.action||'') .slice(0,550),date:String(d.publication_date||''),deadline:d.comments_close_on||null,effective:d.effective_on||null,agency:(d.agencies||[]).map(a=>a.name).filter(Boolean).slice(0,2).join(', ')||'Federal agency',url:d.html_url||'',source:'Federal Register',scope:'Nationwide • not ZIP-specific',rins:Array.isArray(d.regulation_id_numbers)?d.regulation_id_numbers:[],level:'federal'};
}
export function normalizeStateBill(d,state){return {id:'state:'+String(d.id||d.identifier||''),type:'BILL',stage:'State bill',title:String(d.title||d.identifier||'State bill'),summary:String(d.abstracts?.[0]?.abstract||'Review the source for bill text, votes and actions.').slice(0,550),date:String(d.latest_action_date||d.updated_at||'').slice(0,10),deadline:null,effective:null,agency:`${STATE_NAMES[state]||state} legislature`,url:(Array.isArray(d.sources)&&d.sources[0]?.url)||`https://open.pluralpolicy.com/${state.toLowerCase()}/bills/`,source:'Open States',scope:'Statewide • not district-verified',rins:[],level:'state'};}
async function getJSON(url,options={}){const r=await fetch(url,{...options,signal:AbortSignal.timeout(9000),headers:{Accept:'application/json',...(options.headers||{})}});if(!r.ok)throw Error(`Source returned HTTP ${r.status}`);return r.json()}
function response(res,status,payload,ttl=300){res.statusCode=status;res.setHeader('Content-Type','application/json; charset=utf-8');res.setHeader('Cache-Control',`public, s-maxage=${ttl}, stale-while-revalidate=120`);return res.end(JSON.stringify(payload))}
export default async function handler(req,res){
 if(req.method!=='GET')return response(res,405,{error:'Only GET is supported'},0);
 const action=String(req.query?.action||'');
 if(action==='health')return response(res,200,{ok:true,service:'CivicScope',timestamp:new Date().toISOString()},0);
 if(action==='zip'){
  const zip=String(req.query?.zip||'');if(!isZip(zip))return response(res,400,{error:'Enter a valid 5-digit U.S. ZIP code.'},0);
  try{const d=await getJSON(`https://api.zippopotam.us/us/${zip}`);const p=d.places?.[0];if(!p)throw Error('No ZIP location found');return response(res,200,{zip,city:String(p['place name']||''),state:String(p['state abbreviation']||''),stateName:String(p.state||''),allPlaces:d.places?.map(x=>x['place name']).slice(0,10)||[],precision:'ZIP-level approximate, not voting or zoning district verified'},86400)}
  catch{return response(res,502,{error:'ZIP lookup unavailable or ZIP not found. Check the ZIP and try again.'},0)}
 }
 if(action==='policies'){
  const topic=String(req.query?.topic||'all');const term=topicTerm(topic);if(term===null)return response(res,400,{error:'Unknown policy topic'},0);
  const state=String(req.query?.state||'').toUpperCase();if(state && !STATE_NAMES[state])return response(res,400,{error:'Invalid state'},0);
  const url=new URL('https://www.federalregister.gov/api/v1/documents.json');url.searchParams.set('per_page','35');url.searchParams.set('order','newest');if(term)url.searchParams.set('conditions[term]',term);
  const services={federal:'unavailable',state:'not configured',congress:'not configured'};const items=[];
  const sources=[getJSON(url.toString()).then(x=>{services.federal='live';items.push(...(x.results||[]).map(normalizeRegister).filter(i=>i.id!=='fr:'&&/^https:\/\//.test(i.url)));}).catch(()=>{services.federal='unavailable'})];
  if(state&&process.env.OPENSTATES_API_KEY){
   const q=new URL('https://v3.openstates.org/bills');q.searchParams.set('jurisdiction',STATE_NAMES[state]);q.searchParams.set('per_page','12');if(term)q.searchParams.set('q',term);
   sources.push(getJSON(q.toString(),{headers:{'X-API-KEY':process.env.OPENSTATES_API_KEY}}).then(x=>{services.state='live';items.push(...(x.results||[]).map(d=>normalizeStateBill(d,state)).filter(i=>i.id!=='state:'&&/^https:\/\//.test(i.url)));}).catch(()=>{services.state='unavailable'}));
  }
  if(process.env.CONGRESS_API_KEY){
   const q=new URL('https://api.congress.gov/v3/bill');q.searchParams.set('format','json');q.searchParams.set('limit','20');q.searchParams.set('api_key',process.env.CONGRESS_API_KEY);
   sources.push(getJSON(q.toString()).then(x=>{services.congress='live';const bills=(x.bills||[]).filter(b=>!term||`${b.title||''}`.toLowerCase().includes(term.toLowerCase()));items.push(...bills.map(b=>({id:`congress:${b.congress}:${b.type}:${b.number}`,type:'BILL',stage:'Congressional bill',title:b.title||`${b.type} ${b.number}`,summary:'Federal legislation. Confirm its status and text on Congress.gov.',date:b.latestAction?.actionDate||'',deadline:null,effective:null,agency:'U.S. Congress',url:`https://www.congress.gov/search?q=${encodeURIComponent(b.title||b.number||'')}`,source:'Congress.gov',scope:'Nationwide • not ZIP-specific',rins:[],level:'federal'})));}).catch(()=>{services.congress='unavailable'}));
  }
  await Promise.all(sources);if(services.federal==='unavailable'&&services.state!=='live'&&services.congress!=='live')return response(res,502,{error:'Live public-policy sources are temporarily unavailable.',services},0);
  items.sort((a,b)=>String(b.date).localeCompare(String(a.date)));return response(res,200,{items:items.slice(0,70),services,updatedAt:new Date().toISOString(),coverage:'Recent samples, not an exhaustive search or legal determination',topic,state},300);
 }
 return response(res,400,{error:'Unknown action'},0);
}
