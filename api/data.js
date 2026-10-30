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
 return {id:'fr:'+String(d.docu¶»§q«^