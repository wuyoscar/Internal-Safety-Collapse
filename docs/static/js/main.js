/* A single TVD workspace: recorded execution and archived data, never live inference. */
'use strict';
const $=id=>document.getElementById(id);
const reduced=matchMedia('(prefers-reduced-motion: reduce)');
let evidence=null,mode='workflow',workflowIndex=0,step=0,outputIndex=0,family='llamaguard',reading='read';
let pickerMatches=[],pickerActive=-1;
let playing=false,timer=null,renderVersion=0,previousText='',autoStarted=false,userTouched=false;
const node=(tag,cls,text)=>{const n=document.createElement(tag);if(cls)n.className=cls;if(text!==undefined)n.textContent=text;return n;};
const workflow=()=>evidence.workflows[workflowIndex];
const outputs=()=>evidence.cases.filter(c=>family==='all'||c.family===family);
function syntax(text){
 const fragment=document.createDocumentFragment();let pos=0;
 const pattern=/"(?:\\.|[^"\\])*"|\b\d+(?:\.\d+)?\b|\b(?:true|false|null)\b/g;
 for(const m of text.matchAll(pattern)){fragment.append(document.createTextNode(text.slice(pos,m.index)));const after=text.slice(m.index+m[0].length).trimStart();let cls=m[0].startsWith('"')?(after.startsWith(':')?'code-key':'code-string'):'code-number';if(m[0].includes('???'))cls+=' code-placeholder';fragment.append(node('span',cls,m[0]));pos=m.index+m[0].length;}
 fragment.append(document.createTextNode(text.slice(pos)));return fragment;
}
function paintEditor(text,animate){
 const version=++renderVersion,pre=$('editor-code');
 let prefix=0;if(animate)while(prefix<previousText.length&&prefix<text.length&&previousText[prefix]===text[prefix])prefix++;
 previousText=text;pre.scrollTop=0;
 if(!animate||reduced.matches||reading==='read'||prefix===text.length){pre.replaceChildren(syntax(text));return;}
 const start=performance.now(),duration=950/Number($('studio-speed').value);
 const draw=now=>{if(version!==renderVersion)return;const ratio=Math.min(1,(now-start)/duration);const end=prefix+Math.floor((text.length-prefix)*ratio);pre.replaceChildren(syntax(text.slice(0,end)));if(ratio<1)requestAnimationFrame(draw);};
 requestAnimationFrame(draw);
}
function textFields(text){
 try{
  const d=JSON.parse(text);
  if(Array.isArray(d.articles))return d.articles.map((r,i)=>({label:`Article ${i+1}`,text:r.article_text}));
  if(Array.isArray(d.test_cases))return d.test_cases.map(r=>({label:r.category.replaceAll('_',' '),text:r.text}));
  if(typeof d.article_text==='string')return [{label:'Article',text:d.article_text}];
  const labels={assistant_safe:'Safe response',assistant_unsafe:'Unsafe response',text_threat:'Threat',text_insult:'Insult',text_id:'Identity attack',text:'Candidate'};
  const fields=Object.entries(d).filter(([k,v])=>typeof v==='string'&&(k.startsWith('text')||k.startsWith('assistant_'))).map(([label,text])=>({label:labels[label]||label,text,safe:label==='assistant_safe'}));
  return fields.length?fields:[{label:'',text}];
 }catch{return [{label:'',text}];}
}
function reader(text,format,animate){
 const target=$('editor-preview');target.className=`reading-preview ${format==='article'?'article-text':'response-text'}`;
 const fields=textFields(text),version=renderVersion+1;
 target.replaceChildren(...fields.map(item=>{
  const block=node('section',`reading-block${item.safe?' safe':''}${item.label==='Unsafe response'?' unsafe':''}`);
  if(item.label)block.append(node('h4','',item.label));
  const p=node('p',item.text==='???'?'unfinished':'');block.append(p);
  if(!animate||reduced.matches||item.text==='???'){p.textContent=item.text;return block;}
  const start=performance.now(),duration=750/Number($('studio-speed').value);
  const draw=now=>{if(version!==renderVersion)return;const ratio=Math.min(1,(now-start)/duration);p.textContent=item.text.slice(0,Math.floor(item.text.length*ratio));if(ratio<1)requestAnimationFrame(draw);};requestAnimationFrame(draw);
  return block;
 }));
 target.scrollTop=0;
}
function setChecks(checks){
 document.querySelectorAll('[data-check]').forEach(el=>{
  const status=checks[el.dataset.check]||'pending';el.dataset.state=status;el.querySelector('i').textContent=status==='pass'||status==='written'?'✓':status==='fail'?'×':'';
  el.setAttribute('aria-label',`${el.querySelector('span').textContent}: ${status}`);
 });
}
function status(phase){
 const names={inspect:'Reading',write:'Editing',probe:'Testing',fail:'Needs revision',complete:'Completed',archive:'Response'};
 $('run-status').textContent=names[phase]||phase;$('run-status').className=`run-status ${phase}`;
 $('editor-state').textContent=phase==='write'?'Writing…':phase==='complete'?'Saved':phase==='fail'?'Revision needed':phase==='archive'?'':'Reading';
 $('editor-state').className=`editor-state ${phase}`;
}
function timeline(frames){
 $('step-timeline').replaceChildren(...frames.map((s,i)=>{
  const b=node('button',`timeline-step${i===step?' active':''}${i<step?' done':''}`);b.type='button';b.dataset.step=i;b.setAttribute('aria-label',`Step ${i+1}: ${s.label}`);b.setAttribute('aria-current',i===step?'step':'false');b.append(node('span','',String(i+1).padStart(2,'0')),node('span','',s.label));return b;
 }));
}
function writtenPreview(text,phase){
 const target=$('written-preview');let items=[];
 try{
  const data=JSON.parse(text);
  if(Array.isArray(data.articles))items=data.articles.map(r=>({label:`article_text · ${r.id}`,text:r.article_text}));
  else if(Array.isArray(data.test_cases))items=data.test_cases.map(r=>({label:r.category,text:r.text}));
  else items=Object.entries(data).filter(([k,v])=>typeof v==='string'&&(k==='text'||k.startsWith('text_')||k.startsWith('assistant_'))).map(([label,text])=>({label,text}));
 }catch{if(mode==='outputs'&&text.trim())items=[{label:'Response',text}];}
 items=items.filter(i=>i.text.trim()&&i.text!=='???');target.hidden=!items.length;
 const title=phase==='archive'?'RESPONSE':phase==='write'?'WRITING':phase==='complete'?'SAVED':'CHECKING';
 target.replaceChildren(node('p','mono-caption',title),...items.map(i=>{const block=node('div',`written-item${i.label==='assistant_safe'?' safe':''}`);block.append(node('span','written-field',i.label),node('p','',i.text));return block;}));
 document.querySelector('.feedback-body').scrollTop=0;
}
function renderReports(){
 if(!evidence?.modelReports)return;
 const query=$('model-search').value.toLowerCase().trim();
 const matches=evidence.modelReports.filter(r=>r.name.toLowerCase().includes(query));
 $('reported-models').replaceChildren(...matches.map(r=>{
  const row=node('div','reported-model');const a=node('a','model-primary');a.href=r.links[0];
  if(r.icon){const img=node('img');img.src=r.icon;img.alt='';img.width=15;img.height=15;img.loading='lazy';a.append(img);}
  a.append(node('span','',r.name));a.title=r.name;row.append(a);
  if(r.links.length>1){const extra=node('div','extra-evidence');r.links.slice(1).forEach((url,i)=>{const more=node('a','',String(i+2));more.href=url;more.setAttribute('aria-label',`${r.name}: evidence ${i+2}`);extra.append(more);});row.append(extra);}
  return row;
 }));
 $('model-count').textContent=`${matches.length} LLM${matches.length===1?'':'s'}`;$('model-empty').hidden=!!matches.length;
}
function render(animate=true){
 if(!evidence)return;
 $('workflow-options').hidden=mode!=='workflow';$('archive-options').hidden=mode!=='outputs';$('step-timeline').hidden=mode!=='workflow';$('cycle-tasks').closest('label').hidden=mode!=='workflow';
 document.querySelectorAll('[data-mode]').forEach(b=>{const active=b.dataset.mode===mode;b.classList.toggle('selected',active);b.setAttribute('aria-pressed',String(active));});
 document.querySelectorAll('.workspace-files .file-row:not(.current)').forEach(n=>n.hidden=mode==='outputs');
 document.querySelector('.workspace-files .completion-list').hidden=mode==='outputs';
 document.querySelector('.workspace-files .directory').textContent=mode==='workflow'?'▱ /workspace':'▱ /archive';
 let text,total,position,format='prose',hasPicture=false;
 if(mode==='workflow'){
  const w=workflow(),s=w.steps[step];text=s.editor;total=w.steps.length;position=step;format=w.format;
  $('studio-task').textContent=w.task;$('studio-rule').textContent=w.rule;$('studio-artifact').textContent=w.file;
  $('workspace-data-file').textContent=w.file;$('studio-llm').textContent=`${w.llm}\n${w.tool}`;
  const kindLabels={'Recorded output':'Tool response','Recorded agent message':'Agent','Action summary':'Action','Source summary':'Task','Recorded instruction':'Instruction'};
  $('editor-file').textContent=s.file;$('step-label').textContent=s.label;$('feedback-type').textContent=kindLabels[s.feedbackKind]||s.feedbackKind;
  $('feedback-output').dataset.kind=s.feedbackKind==='Recorded output'?'terminal':'prose';
  $('feedback-output').textContent=s.feedback;$('feedback-pointer').textContent=w.llm;
  $('studio-source').href=w.source;$('studio-source').textContent='Source ↗';$('studio-source').title=w.note;
  $('studio-note').textContent=w.id==='news'?'TRUE and FAKE are classifier predictions.':w.id==='toxicity'?'The agent tests candidates, then saves the data and runs the final checks.':'';
  $('record-indicator').textContent=w.toolLabel;$('editor-caption').textContent='███ redacted · … shortened';$('feedback-title').textContent='FEEDBACK';
  $('editor-picture').hidden=true;$('editor-code').hidden=false;status(s.phase);setChecks(s.checks);timeline(w.steps);
  writtenPreview(s.editor,s.phase);
  document.querySelectorAll('[data-workflow]').forEach(b=>{const active=Number(b.dataset.workflow)===workflowIndex;b.classList.toggle('selected',active);b.setAttribute('aria-pressed',String(active));});
 }else{
  const all=outputs(),c=all[outputIndex];if(!c)return;text=c.safe?JSON.stringify({assistant_safe:c.safe,assistant_unsafe:c.excerpt},null,2):c.excerpt;total=all.length;position=outputIndex;format=c.format||'prose';
  $('studio-task').textContent=c.task||c.query||c.title;$('studio-rule').textContent=c.rule||(c.kind==='Agent'?'See the task checks':c.kind==='Chat API'?'Task supplied as text':c.kind==='Web chat'?'Web-chat task':'Follow-up generation');
  $('studio-artifact').textContent=c.field||c.artifact;$('workspace-data-file').textContent=c.artifact;$('studio-llm').textContent=`${c.llm}\n${c.kind}`;
  $('editor-file').textContent=c.field||c.artifact;$('step-label').textContent=c.title;$('feedback-type').textContent=c.checks?'Task checks':'Task';
  $('feedback-output').dataset.kind=c.checks?'terminal':'prose';
  $('feedback-output').textContent=c.checks||c.query||c.summary;$('feedback-pointer').textContent=`${c.llm} · ${c.kind}`;
  $('studio-source').href=c.artifactSource||c.source;$('studio-source').textContent=c.sourceUnavailable?'Source excerpt ↗':'Source ↗';$('studio-source').title=c.ruleDetail||'';
  $('studio-note').textContent=c.kind==='Chat API'?'Single-turn response: commands in the reply are text, not executed tool calls.':c.kind==='Notebook'?'Chat-based generation.':c.kind==='Web chat'?'Web-chat screenshot.':'';
  $('record-indicator').textContent=c.tool||evidence.families.find(f=>f.id===c.family)?.label||'';$('editor-caption').textContent=c.display||'███ redacted · … shortened';$('feedback-title').textContent=c.checks?'CHECKS':'CONTEXT';status('archive');
  if($('example-list').hidden)$('example-search').value=c.title;
  $('example-count').textContent=`${position+1} / ${total}`;$('example-prev').disabled=position===0;$('example-next').disabled=position===total-1;
  const picture=$('editor-picture');hasPicture=c.panel!==undefined;picture.hidden=!hasPicture;$('editor-code').hidden=hasPicture;
  if(c.panel!==undefined){picture.style.setProperty('--x',c.panel%2?'100%':'0%');picture.style.setProperty('--y',`${Math.floor(c.panel/2)*50}%`);picture.setAttribute('role','img');picture.setAttribute('aria-label',`${c.llm} archived screenshot, redacted in the paper`);}
  if(c.panel===undefined&&c.kind!=='Notebook')writtenPreview(text,'archive');else $('written-preview').hidden=true;
 }
 $('run-status').hidden=mode==='outputs';$('reading-mode').hidden=hasPicture;
 $('editor-preview').hidden=hasPicture||reading!=='read';$('editor-code').hidden=hasPicture||reading!=='raw';
 document.querySelectorAll('[data-reading]').forEach(b=>{b.classList.toggle('selected',b.dataset.reading===reading);b.setAttribute('aria-pressed',String(b.dataset.reading===reading));});
 document.querySelector('[data-reading="raw"]').textContent=mode==='workflow'?'JSON':'Raw';
 $('step-number').textContent=String(position+1).padStart(2,'0');$('editor-position').textContent=mode==='workflow'?`${position+1} / ${total} steps`:`${position+1} / ${total} examples`;
 $('studio-progress').max=String(total-1);$('studio-progress').value=String(position);$('playback-label').textContent=`${position+1} / ${total}`;
 $('studio-prev').disabled=position===0;$('studio-next').disabled=position===total-1;
 reader(text,format,animate);paintEditor(text,animate);$('studio-play').textContent=playing?'Pause Ⅱ':'Play ▶';
}
function clearTimer(){clearTimeout(timer);timer=null;}
function pause(){playing=false;clearTimer();$('studio-play').textContent='Play ▶';}
function schedule(){
 clearTimer();if(!playing)return;
 timer=setTimeout(()=>{
  if(mode==='workflow'){
   if(step<workflow().steps.length-1)step++;
   else if($('cycle-tasks').checked){workflowIndex=(workflowIndex+1)%evidence.workflows.length;step=0;previousText='';}
   else{pause();return;}
  }else outputIndex=(outputIndex+1)%outputs().length;
  render();schedule();
 },(mode==='workflow'?3800:5500)/Number($('studio-speed').value));
}
function play(){if(!evidence)return;playing=true;if(mode==='workflow'&&step===workflow().steps.length-1){step=0;render();}$('studio-play').textContent='Pause Ⅱ';schedule();}
function renderTaskFilters(){
 const options=[...evidence.families,{id:'all',label:'All',description:'Every task'}].filter(f=>f.id==='all'||evidence.cases.some(c=>c.family===f.id));
 $('task-filters').replaceChildren(...options.map(f=>{const b=node('button',`task-filter${f.main?' main-task':''}${family===f.id?' selected':''}`);b.type='button';b.dataset.family=f.id;b.setAttribute('aria-pressed',String(family===f.id));b.append(node('span','',f.label));if(f.main)b.append(node('small','',f.description));return b;}));
}
function pickerRows(query=''){
 pickerMatches=outputs().filter(c=>`${c.title} ${c.query||''} ${c.tool||''} ${c.llm}`.toLowerCase().includes(query.toLowerCase()));pickerActive=-1;
 const current=outputs()[outputIndex]?.id;
 $('example-list').replaceChildren(...pickerMatches.map((c,i)=>{const b=node('button','example-option');b.type='button';b.id=`example-option-${i}`;b.dataset.example=c.id;b.setAttribute('role','option');b.setAttribute('aria-selected',String(c.id===current));b.append(node('span','',c.title),node('small','',`${c.field||c.artifact} · ${c.llm}`));return b;}));
 if(!pickerMatches.length)$('example-list').append(node('p','no-examples','No matching example. Try another word.'));
 $('example-search').removeAttribute('aria-activedescendant');
}
function openPicker(){pause();pickerRows();$('example-list').hidden=false;$('example-search').setAttribute('aria-expanded','true');}
function closePicker(){if(!evidence)return;$('example-list').hidden=true;$('example-search').setAttribute('aria-expanded','false');$('example-search').removeAttribute('aria-activedescendant');$('example-search').value=outputs()[outputIndex]?.title||'';}
function selectExample(id){const index=outputs().findIndex(c=>c.id===id);if(index<0)return;outputIndex=index;userTouched=true;pause();$('example-search').focus({preventScroll:true});closePicker();render();}
function chooseMode(value){userTouched=true;mode=value;previousText='';step=0;outputIndex=0;closePicker();renderTaskFilters();render();if(playing)schedule();}
async function load(){
 $('load-error').hidden=true;
 try{
  const response=await fetch('static/data/evidence.json');if(!response.ok)throw new Error(`HTTP ${response.status}`);
  evidence=await response.json();if(evidence.schemaVersion!==2||!evidence.workflows?.length||!evidence.cases?.length)throw new Error('Missing recorded workflows');
  $('workflow-options').replaceChildren(...evidence.workflows.map((w,i)=>{const b=node('button',i===0?'selected':'');b.dataset.workflow=i;b.type='button';b.append(node('span','',w.title),node('small','',w.toolLabel));b.setAttribute('aria-pressed',String(i===0));return b;}));
  $('archive-count').textContent=String(evidence.cases.length);renderTaskFilters();render(false);renderReports();
  const observer=new IntersectionObserver(entries=>{if(entries.some(e=>e.isIntersecting)&&!autoStarted&&!userTouched&&!reduced.matches){autoStarted=true;play();}},{threshold:.25});observer.observe(document.querySelector('.workspace-body'));
 }catch(error){$('load-error').hidden=false;pause();console.error('Could not load recorded workspaces.',error);}
}
$('workflow-options').addEventListener('click',e=>{const b=e.target.closest('[data-workflow]');if(!b)return;userTouched=true;workflowIndex=Number(b.dataset.workflow);step=0;previousText='';render();if(!reduced.matches)play();});
document.querySelectorAll('[data-mode]').forEach(b=>b.addEventListener('click',()=>chooseMode(b.dataset.mode)));
$('task-filters').addEventListener('click',e=>{const b=e.target.closest('[data-family]');if(!b)return;family=b.dataset.family;outputIndex=0;previousText='';closePicker();renderTaskFilters();render();if(playing)schedule();});
$('example-search').addEventListener('focus',()=>{openPicker();$('example-search').select();});
$('example-search').addEventListener('click',()=>{if($('example-list').hidden)openPicker();});
$('example-search').addEventListener('input',e=>{pickerRows(e.target.value);$('example-list').hidden=false;$('example-search').setAttribute('aria-expanded','true');});
$('example-toggle').addEventListener('click',()=>{if($('example-list').hidden){$('example-search').focus();openPicker();}else closePicker();});
$('example-list').addEventListener('mousedown',e=>e.preventDefault());
$('example-list').addEventListener('click',e=>{const b=e.target.closest('[data-example]');if(b)selectExample(b.dataset.example);});
$('example-search').addEventListener('keydown',e=>{
 if(e.key==='Escape'||e.key==='Tab'){closePicker();return;}
 if(e.key==='Enter'&&pickerActive>=0){e.preventDefault();selectExample(pickerMatches[pickerActive].id);return;}
 if(e.key==='ArrowDown'||e.key==='ArrowUp'){
  e.preventDefault();if($('example-list').hidden)openPicker();if(!pickerMatches.length)return;
  pickerActive=Math.max(0,Math.min(pickerMatches.length-1,pickerActive+(e.key==='ArrowDown'?1:-1)));
  [...$('example-list').querySelectorAll('[role="option"]')].forEach((b,i)=>b.classList.toggle('focused',i===pickerActive));
  const b=$(`example-option-${pickerActive}`);$('example-search').setAttribute('aria-activedescendant',b.id);b.scrollIntoView({block:'nearest'});
 }
});
document.addEventListener('click',e=>{if(!$('example-picker').contains(e.target))closePicker();});
$('example-prev').addEventListener('click',()=>{pause();outputIndex=Math.max(0,outputIndex-1);closePicker();render();});
$('example-next').addEventListener('click',()=>{pause();outputIndex=Math.min(outputs().length-1,outputIndex+1);closePicker();render();});
document.querySelectorAll('[data-reading]').forEach(b=>b.addEventListener('click',()=>{reading=b.dataset.reading;render(false);}));
$('studio-play').addEventListener('click',()=>{userTouched=true;playing?pause():play();});
$('studio-prev').addEventListener('click',()=>{userTouched=true;pause();if(mode==='workflow')step=Math.max(0,step-1);else outputIndex=Math.max(0,outputIndex-1);render();});
$('studio-next').addEventListener('click',()=>{userTouched=true;pause();if(mode==='workflow')step=Math.min(workflow().steps.length-1,step+1);else outputIndex=Math.min(outputs().length-1,outputIndex+1);render();});
$('studio-progress').addEventListener('input',e=>{userTouched=true;pause();if(mode==='workflow')step=Number(e.target.value);else outputIndex=Number(e.target.value);render(false);});
$('step-timeline').addEventListener('click',e=>{const b=e.target.closest('[data-step]');if(b){userTouched=true;pause();step=Number(b.dataset.step);render();}});
$('studio-speed').addEventListener('change',()=>{if(playing)schedule();});
$('retry-load').addEventListener('click',load);
document.addEventListener('visibilitychange',()=>{if(document.hidden)pause();});
reduced.addEventListener('change',()=>{if(reduced.matches)pause();});
$('model-search').addEventListener('input',renderReports);
$('copy-citation').addEventListener('click',async()=>{try{await navigator.clipboard.writeText($('bibtex').textContent);$('copy-status').textContent='Citation copied.';}catch{const range=document.createRange();range.selectNodeContents($('bibtex'));const selection=getSelection();selection.removeAllRanges();selection.addRange(range);$('copy-status').textContent='Citation selected. Press Ctrl/Cmd+C to copy.';}});
const legacy={demos:'workspace',outputs:'workspace',about:'results'};if(legacy[location.hash.slice(1)])location.replace(`#${legacy[location.hash.slice(1)]}`);
load();
