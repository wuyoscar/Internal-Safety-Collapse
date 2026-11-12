/* Full local-output index. Payload values remain redacted in archive previews. */
(function(){
 'use strict';
 let library=null,select=null,current=null;
 const $=id=>document.getElementById(id);
 const make=(tag,cls,text)=>{const n=document.createElement(tag);if(cls)n.className=cls;if(text!==undefined)n.textContent=text;return n;};
 function visibleTasks(){const source=$('library-source').value,domain=$('library-domain').value,query=$('library-search').value.toLowerCase().trim();return library.tasks.filter(t=>(!source||t.source===source)&&(!domain||t.domain===domain)&&`${t.label} ${t.id} ${t.modules.join(' ')}`.toLowerCase().includes(query));}
 function domains(){const previous=$('library-domain').value,source=$('library-source').value;const names=[...new Set(library.tasks.filter(t=>!source||t.source===source).map(t=>t.domain))].sort();const all=make('option','','All disciplines');all.value='';$('library-domain').replaceChildren(all,...names.map(d=>{const o=make('option','',d);o.value=d;return o;}));$('library-domain').value=names.includes(previous)?previous:'';}
 function drawTasks(){
  if(!library)return;const tasks=visibleTasks();
  $('library-task-list').replaceChildren(...tasks.map(t=>{const b=make('button',`library-task${t.id===current?' selected':''}`);b.type='button';b.dataset.libraryTask=t.id;b.title=`${t.id} · ${t.domain}`;b.append(make('span','',t.label),make('small','',String(t.outputs.length)));return b;}));
  $('library-empty').hidden=tasks.length>0;
 }
 function render(folder,filename){
  if(!library)return;current=folder;const task=library.tasks.find(t=>t.id===folder);if(!task)return;if($('library-source').value&&$('library-source').value!==task.source){$('library-source').value=task.source;domains();}if($('library-domain').value&&$('library-domain').value!==task.domain)$('library-domain').value='';if(!visibleTasks().some(t=>t.id===folder))$('library-search').value='';drawTasks();
  $('library-output').replaceChildren(...task.outputs.map(o=>{const option=make('option','',(o.displayName||o.filename)+(o.reasoningSummaryCount?' · reasoning summary':o.readableReasoningCount?' · reasoning logged':''));option.value=o.filename;option.title=o.filename;return option;}));
  if(!task.outputs.length){const option=make('option','','No saved output');option.value='';$('library-output').append(option);}
  $('library-output').disabled=!task.outputs.length;$('library-output').value=filename||task.outputs[0]?.filename||'';
  $('library-detail').textContent=task.domain+' · '+task.outputs.length+' output'+(task.outputs.length===1?'':'s');
 }
 function init(data,onSelect){
  library=data;select=onSelect;$('library-count').textContent=`${data.templateTaskCount||data.taskCount} templates · ${data.outputCount} saved files`;
  const all=make('option','','All sources');all.value='';$('library-source').replaceChildren(all,...Object.entries(data.sourceCounts||{Workspaces:data.outputCount}).map(([name,count])=>{const o=make('option','',`${name} · ${count}`);o.value=name;return o;}));domains();
  $('library-source').addEventListener('change',()=>{domains();drawTasks();});
  $('library-domain').addEventListener('change',drawTasks);$('library-search').addEventListener('input',drawTasks);
  $('library-task-list').addEventListener('click',e=>{const b=e.target.closest('[data-library-task]');if(b)select(b.dataset.libraryTask);});
  $('library-output').addEventListener('change',()=>select(current,$('library-output').value));drawTasks();
 }
 function workflow(folder,filename){
  const task=library.tasks.find(t=>t.id===folder);if(!task)return null;
  const output=task.outputs.find(o=>o.filename===filename)||task.outputs[0];
  const file=output?.filename||'task.json';const id='archive-'+folder+'-'+file;
  const preview=output?.preview.text||'No saved output was found in this folder.';
  const event=(kind,text,language='text',origin='presentation')=>({kind,text,language,pointer:`/tasks/${folder}/${file}`,origin});
  const frame=(label,editor,events,language='text')=>({label,phase:'inspect',editor,file,language,unsafeFields:[],feedback:'',feedbackKind:'Archive inspection',pointer:`/tasks/${folder}/${file}`,activity:events,checks:{data:'pending',tool:'pending',tests:'pending'}});
  const steps=[frame('Open the saved output',preview,[event('assistant',output?'Open the saved output preview.':'No saved output is available.')],output?.preview.kind==='json'?'json':'text')];
  if(output){
   const language=output.preview.kind==='json'?'json':'text';
   const before=preview.replace(/"[^"\n]*█[^"\n]*"(?!\s*:)/g,'"???"').replace(/█+/g,'???');
   steps[0]=frame('Inspect the data fields',before,[event('assistant','The incomplete fields show where task data will be written. This starting state is an illustration.')],language);
   const filled=frame('Write the saved data',preview,[event('output','Saved output · sensitive values masked.')],language);filled.phase='write';steps.push(filled);
   steps.push(frame('Review the saved artifact',preview,[event('assistant',`Source: ${output.filename}\nThis view does not infer a validation result.`)],language));
  }
  const sourcePlayback=!!output?.toolEvents?.length;
  if(sourcePlayback){let lastView=preview,lastFile=file,lastLanguage=output.preview.kind==='json'?'json':'text';steps.splice(0,steps.length,...output.toolEvents.map(e=>{const origin=e.origin||'source-log';const events=[typeof e.command==='string'&&e.command.trim()?event('command',e.command,'shell',origin):event('notice','Command text unavailable in this preview.','text',origin),event('output',e.result||'Tool output unavailable in this preview.','text',origin)];if(typeof e.editor==='string'){lastView=e.editor;lastFile=e.file||file;lastLanguage=e.language||'text';}const item=frame(e.label,lastView,events,lastLanguage);item.file=lastFile;item.phase=e.phase;item.reasoningSummary=e.reasoning?.summary||'';item.reasoningIndex=e.reasoning?.index;return item;}));}
  const displayNote=sourcePlayback?'Recorded tool-call order; commands and outputs may be redacted. Reasoning notes are editorial summaries.':'Presentation steps; saved output shown below.';
  return {id,mode:'walkthrough',archiveInspection:true,sourcePlayback,title:task.label,templateFolder:folder,archiveFile:output?.filename||'',empty:!output,llm:'Workspace archive',file,files:[...new Set(steps.map(s=>s.file))],tool:task.modules.join(' · ')||task.label,toolLabel:task.domain,task:'Inspect the saved output for '+task.label+'.',rule:output?'Source-file structure and provenance':'No saved output in this folder',format:'json',source:'https://github.com/wuyoscar/Internal-Safety-Collapse/blob/main/docs/static/data/task-library.json',displayNote,note:displayNote,steps};
 }
 function sequence(){const seen=new Set();return visibleTasks().flatMap(t=>t.outputs.filter(o=>{if(seen.has(o.sha256))return false;seen.add(o.sha256);return true;}).map(o=>({folder:t.id,filename:o.filename})));}
 window.TaskLibrary={init,render,workflow,sequence,get:()=>library};
}());
