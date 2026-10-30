import test from 'node:test';
import assert from 'node:assert/strict';
import {isZip,topicTerm,normalizeRegister,normalizeStateBill} from '../api/data.js';
test('ZIP validation keeps leading zero and rejects injection',()=>{assert.equal(isZip('00501'),true);for(const s of ['1000','100001','1<script>','10001%00','ABCDE'])assert.equal(isZip(s),false)});
test('topic allowlist rejects arbitrary upstream query',()=>{assert.equal(topicTerm('land'),'land use');assert.equal(topicTerm('unknown'),null)});
test('Federal Register mapping preserves provenance and stage',()=>{const d=normalizeRegister({document_number:'2026-12345',title:'A proposed rule',type:'PRORULE',publication_date:'2026-10-30',html_url:'https://www.federalregister.gov/d/2026-12345',agencies:[{name:'Agency'}],regulation_id_numbers:['1234-AA01']});assert.equal(d.stage,'Proposed rule');assert.equal(d.scope,'Nationwide • not ZIP-specific');assert.deepEqual(d.rins,['1234-AA01'])});
test('state bills are statewide, never labeled as neighborhood issues',()=>{const d=normalizeStateBill({id:'ocd-1',title:'School bill'},'NY');assert.equal(d.level,'state');assert.match(d.scope,/not district-verified/)});
