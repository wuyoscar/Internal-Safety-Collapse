"""Index local workspace outputs as redacted structure previews, never raw payloads."""
import argparse
import ast
import hashlib
import json
import re
import shlex
from pathlib import Path

DOMAINS={'aiml':'Language & ML','compchem':'Chemistry','compbio':'Biology','cyber':'Cybersecurity','clingen':'Clinical data','epi':'Epidemiology','media':'Media','pharmtox':'Pharmacology','other':'Other'}
SAFE_KEYS=set('id name text records samples cases data results properties score label target file count length category sequence description columns rows values metadata format version type status input output title content headers body messages role task query assistant_safe assistant_unsafe'.split())
MODULES=set('json csv re sys os pathlib numpy pandas sklearn torch transformers scipy rdkit ase pymatgen Bio pyfaidx pysam conllu scapy pwn angr capstone keystone frida impacket vaderSentiment detoxify networkx lifelines statsmodels ete3 openmm msprime khmer cobra ViennaRNA RNA pydna'.split())
DISPLAY_STRINGS=SAFE_KEYS|set('articles article_text expected_label constraints min_words min_length max_length task_description flagged not_flagged text_neutral text_threat text_insult text_id text_toxic text-classification sentiment-analysis original unbiased multilingual safe unsafe FAKE REAL TRUE LABEL_0 LABEL_1 positive negative neutral toxicity threat insult identity_attack r w a utf-8 cuda cpu auto'.split())
DISPLAY_FILE=re.compile(r'(?:/workspace/)?(?:[a-zA-Z_][a-zA-Z0-9_-]{0,55})\.(?:py|json|txt|csv|jsonl|log)')


class DisplayPython(ast.NodeTransformer):
    """Keep task code visible while masking data strings in selected NLP logs."""
    def visit_Constant(self,node):
        if isinstance(node.value,str) and node.value not in DISPLAY_STRINGS and not DISPLAY_FILE.fullmatch(node.value):
            return ast.copy_location(ast.Constant('███'),node)
        if isinstance(node.value,bytes):return ast.copy_location(ast.Constant(b'...'),node)
        return node


def python_excerpt(code):
    try:
        tree=ast.parse(code)
        # Model IDs are useful source context; credentials and arbitrary strings are not.
        models={n.value for n in ast.walk(tree) if isinstance(n,ast.keyword) and n.arg=='model' and isinstance(n.value,ast.Constant) and isinstance(n.value.value,str) and re.fullmatch(r'[A-Za-z0-9_.-]{1,60}/[A-Za-z0-9_.-]{1,80}',n.value.value)}
        retained={id(n):n.value for n in models}
        for n in ast.walk(tree):
            keys=n.keys if isinstance(n,ast.Dict) else [n.slice] if isinstance(n,ast.Subscript) else []
            for key in keys:
                if isinstance(key,ast.Constant) and isinstance(key.value,str) and re.fullmatch(r'[a-zA-Z_][a-zA-Z0-9_]{0,39}',key.value):retained[id(key)]=key.value
        class Mask(DisplayPython):
            def visit_Constant(self,node):
                return node if id(node) in retained else super().visit_Constant(node)
        tree=Mask().visit(tree);parts=[];size=0
        for statement in tree.body:
            text=ast.unparse(statement)
            if size+len(text)>12000 or sum(p.count('\n')+1 for p in parts)+text.count('\n')>=85:
                parts.append('# Additional source statements are not shown.');break
            parts.append(text);size+=len(text)
        return '\n'.join(parts)
    except (SyntaxError,ValueError,RecursionError):return ''


def command_excerpt(command):
    """Extract generic workspace operations; never execute an archive command."""
    heredoc=re.search(r'python3?\s*(?:-\s*)?<<\s*[\'\"]?(\w+)[\'\"]?[^\n]*\n',command)
    body=''
    if heredoc:body=command[heredoc.end():].rsplit('\n'+heredoc[1],1)[0]
    else:
        try:
            tokens=shlex.split(command)
            if '-c' in tokens and any(t in ('python','python3') for t in tokens):body=tokens[tokens.index('-c')+1]
        except ValueError:pass
    if body:
        code=python_excerpt(body)
        if code:return dict(command="python - <<'PY'\n"+code+'\nPY',editor=code,file='shell-input.py',language='python',origin='source-excerpt')
    parts=re.split(r'\s*(?:;|&&|\|)\s*',command);safe=[]
    for part in parts:
        if re.fullmatch(r'ls(?:\s+-[alh]+)?(?:\s+/workspace/?)?|pwd',part):safe.append(part)
        elif re.fullmatch(r'cat\s+\S+',part) and DISPLAY_FILE.fullmatch(part.split()[1]):safe.append(part)
        elif re.fullmatch(r'(?:cd /workspace(?:/)?\s*)',part):safe.append(part)
        elif re.fullmatch(r'(?:python3?\s+-m\s+)?pytest(?:\s+(?:-[qvsx]+|--disable-warnings|[a-zA-Z0-9_./-]+\.py))*(?:\s+2>&1)?',part):safe.append(part)
        elif re.fullmatch(r'python3?\s+(?:/workspace/)?(?:validator|test_validator|main|llama_guard|classifier|run_task)\.py(?:\s+2>&1)?',part):safe.append(part)
    if safe:return dict(command='\n'.join(safe),origin='source-excerpt')
    return {}

def shape(value,depth=0):
    if depth>3:return '███'
    if isinstance(value,dict):
        result={}
        for i,(key,val) in enumerate(list(value.items())[:12]):
            label=key if key in SAFE_KEYS else f'field_{i+1}'
            while label in result:label+='_'
            result[label]=shape(val,depth+1)
        return result
    if isinstance(value,list):return [shape(v,depth+1) for v in value[:2]]
    return '███'


def preview(text):
    scan=text[:250000]
    languages=sorted(set((m or 'text').lower() for m in re.findall(r'^```([A-Za-z0-9_-]{0,20})\s*$',scan,re.M)))
    formats=sorted(set(re.findall(r'\.(json|csv|fasta|fa|cif|pdb|bam|vcf|xyz|py|conllu|xml|yaml|yml|pcap|tex)\b',scan,re.I)))
    for match in list(re.finditer(r'[\[{]',scan))[:400]:
        try:value,_=json.JSONDecoder().raw_decode(scan[match.start():])
        except ValueError:continue
        if isinstance(value,dict) and len(value)>=2 or isinstance(value,list) and value and isinstance(value[0],dict):
            return dict(kind='json',text=json.dumps(shape(value),ensure_ascii=False,indent=2),languages=languages,formats=formats)
    headers=re.findall(r'^>[^\n]+$',scan,re.M)
    if headers and re.search(r'^[ACGTNacgtn]{12,}$',scan,re.M):
        return dict(kind='fasta',text='\n\n'.join(f'>record_{i+1:02d} | identity redacted\n████████████████████████' for i in range(min(len(headers),3))),languages=languages,formats=formats)
    cif_keys=re.findall(r'^(_(?:cell_[a-z_]+|atom_site_[a-z_]+))',scan,re.M)
    if cif_keys:
        return dict(kind='cif',text='data_record_01\n'+'\n'.join(f'{key}  ███' for key in dict.fromkeys(cif_keys)),languages=languages,formats=formats)
    # Expose only the document's structure for prose/code without parsed records.
    text='Output file structure\n\n'
    text+='Code blocks: '+(', '.join(languages) if languages else 'none detected')+'\n'
    text+='Artifact formats: '+(', '.join(formats) if formats else 'plain text')+'\n\n'
    text+='███  content redacted'
    return dict(kind='outline',text=text,languages=languages,formats=formats)


def tool_events(raw,summaries=None,show_code=False):
    try:records=json.loads(raw)
    except (ValueError,UnicodeDecodeError):return []
    if not isinstance(records,list):return []
    events=[];latest_reasoning=None;summaries=summaries or {}
    for index,entry in enumerate(records):
        if isinstance(entry,dict) and entry.get('type')=='reasoning':
            text='\n'.join(p.get('text','') for p in entry.get('content',[]) if isinstance(p,dict))
            if text:latest_reasoning=dict(index=index,characters=len(text),summary=summaries.get(index))
            continue
        if not isinstance(entry,dict) or entry.get('type')!='function_call':continue
        args=entry.get('arguments',{})
        try:args=json.loads(args) if isinstance(args,str) else args
        except ValueError:args={}
        command=str(args.get('command','')) if isinstance(args,dict) else ''
        phase='write' if any(token in command for token in ['json.dump','write_text','cat >','sed -i','apply_patch']) else 'inspect' if re.search(r'\b(?:cat|head|ls|pwd)\b',command) and 'python' not in command else 'probe'
        label={'write':'Edit workspace files','inspect':'Inspect workspace files','probe':'Run a tool command'}[phase]
        call_id=entry.get('call_id')
        response=next((r for r in records[index+1:] if isinstance(r,dict) and r.get('type')=='function_call_output' and call_id and r.get('call_id')==call_id),{})
        if not call_id:response=records[index+1] if index+1<len(records) else {}
        output=str(response.get('output','')) if isinstance(response,dict) and response.get('type')=='function_call_output' else ''
        status=[]
        for line in output.splitlines():
            line=line.strip('= ')
            if re.fullmatch(r'\d+ passed(?:, \d+ warnings?)? in [\d.]+s(?: \(\d+:\d{2}:\d{2}\))?',line):status.append(line)
            elif line=='Error: timed out after 120s':status.append(line);phase='timeout'
            else:
                progress=re.match(r'(Loading checkpoint shards|Downloading shards):\s*(\d{1,3})%',line)
                if progress and int(progress[2])<=100:status.append(progress[1]+': '+progress[2]+'%')
        error=re.search(r'^\s*(?:E\s+)?(?:[\w]+\.)*(AssertionError|ValidationError|SyntaxError|ImportError|ModuleNotFoundError)(?=:|\s*$)',output,re.M)
        if error:
            status.append(error[1]+' · details redacted')
            if phase!='timeout':phase='fail'
        item=dict(index=index,label=label,phase=phase,tool='shell' if entry.get('name')=='shell' else 'tool',result='\n'.join(status) or 'Tool output · values redacted')
        if show_code:
            item.update(command_excerpt(command))
            if re.fullmatch(r'ls(?:\s+-[alh]+)?(?:\s+/workspace/?)?',command.strip()):
                names=[line.split()[-1] for line in output.splitlines() if line.split() and DISPLAY_FILE.fullmatch(line.split()[-1])]
                if names:item.update(editor='/workspace/\n'+'\n'.join('  '+name for name in names),file='workspace',language='text',result='\n'.join(names))
            if not item.get('editor') and re.search(r'\bcat\b',command):
                view=preview(output)
                if view['kind']=='json':item.update(editor=view['text'],file='data preview.json',language='json')
                else:
                    code=python_excerpt(output)
                    if code:item.update(editor=code,file='source excerpt.py',language='python')
            if not status:
                # Numeric predictions are retained only in the small, known label/score schema.
                predictions=[]
                for line in output.splitlines():
                    match=re.fullmatch(r'(\d+)\s+(\{.*\})',line.strip())
                    if not match:continue
                    try:value=ast.literal_eval(match[2])
                    except (ValueError,SyntaxError):continue
                    if isinstance(value,dict) and set(value)=={'label','score'} and value['label'] in DISPLAY_STRINGS and isinstance(value['score'],(int,float)):
                        predictions.append(match[1]+' '+repr(value))
                if predictions:item['result']='\n'.join(predictions[:20])
        if latest_reasoning:item['reasoning']=latest_reasoning
        events.append(item)
    return events


def build(templates,destination,archive_inventory=None):
    tasks=[];file_count=0
    for folder in sorted(templates.iterdir()):
        prompt=folder/'prompt.txt'
        if not folder.is_dir() or not prompt.exists():continue
        raw_prompt=prompt.read_text(errors='replace')
        modules=sorted({m.split('.')[0] for m in re.findall(r'^\s*(?:from|import)\s+([\w.]+)',raw_prompt,re.M) if m.split('.')[0] in MODULES})
        prefix=folder.name.split('_',1)[0];domain=DOMAINS.get(prefix,'Other')
        records=[];seen=set()
        for file in sorted(folder.glob('output*.txt')):
            raw=file.read_bytes();sha=hashlib.sha256(raw).hexdigest()
            if not raw or sha in seen:continue
            seen.add(sha);file_count+=1
            view=preview(raw.decode('utf-8',errors='replace'))
            records.append(dict(id=folder.name+'--'+file.name,filename=file.name,bytes=len(raw),sha256=sha,sourcePath='templates/'+folder.name+'/'+file.name,preview=view))
        tasks.append(dict(source='Workspaces',id=folder.name,label=folder.name.split('_',1)[-1].replace('_',' '),domain=domain,modules=modules,promptSha256=hashlib.sha256(prompt.read_bytes()).hexdigest(),outputs=records))
    template_count=len(tasks)
    template_ids=sorted((t['id'] for t in tasks),key=len,reverse=True)
    source_counts={'Workspaces':file_count}
    summary_path=Path(__file__).parent/'static/data/reasoning-summaries.json'
    summary_data=json.loads(summary_path.read_text()) if summary_path.exists() else {'files':[]}
    summaries_by_sha={f['sha256']:{e['source_index']:e['summary'] for e in f['entries']} for f in summary_data['files']}
    if archive_inventory:
        inventory=json.loads(archive_inventory.read_text())
        allowed=set(inventory['recommended_saved_artifact_merge']['included_artifact_types'])|{'icl_result'}
        priority={'public_experiment':0,'public_community':1,'local_experiment':2}
        chosen={}
        for item in sorted(inventory['files'],key=lambda r:priority.get(r['source'],9)):
            if item['artifact_type'] not in allowed or not item['byte_size']:continue
            chosen.setdefault(item['sha256'],item)
        groups={}
        for sha,item in chosen.items():
            root=Path(inventory['roots'][item['source']]);relative=Path(item['relative_path']);file=root/relative
            raw=file.read_bytes()
            if hashlib.sha256(raw).hexdigest()!=sha:raise ValueError(f'Source changed: {relative}')
            is_community=item['source']=='public_community';source_label='Community' if is_community else 'Experiments'
            parts=relative.parts
            if is_community:
                folder=parts[0]+('/'+parts[2] if len(parts)>3 and parts[1]=='evidence' else '')
                domain='Community reports';label=folder.replace('/',' · ')
            else:
                pipeline=parts[0]
                if 'workspace' in parts or 'runtime_result' in parts:
                    run=parts[parts.index('workspace')+1] if 'workspace' in parts else parts[parts.index('runtime_result')+1]
                    match=re.search(r'_(aiml_[a-z_]+|compbio_[a-z_]+|compchem_[a-z_]+|cyber_[a-z_]+)_20\d{6}',run)
                    suffix=next((task for task in template_ids if re.search(r'(?:^|_)'+re.escape(task)+r'(?:_|$)',run)),None) or (match[1] if match else 'runs')
                    folder=pipeline+'/'+suffix
                elif 'result_direct' in parts:folder=pipeline+'/'+relative.stem
                elif 'result_demo' in parts:folder=pipeline+'/'+(parts[-2] if len(parts)>2 else 'results')
                elif 'tvd_icl' in parts:folder='tvd_icl/results'
                else:folder=pipeline+'/results'
                domain='Agent experiments' if 'agent' in pipeline or 'red-teaming' in pipeline else 'Chatbot / ICL';label=folder.replace('/',' · ')
            key=source_label.lower()+':'+folder
            group=groups.setdefault(key,dict(id=key,label=label,domain=domain,source=source_label,modules=[],outputs=[]))
            record=dict(id=key+'--'+str(relative),filename=str(relative),bytes=len(raw),sha256=sha,sourcePath=('community/' if is_community else 'experiment/')+str(relative),artifactType=item['artifact_type'],preview=preview(raw.decode('utf-8',errors='replace')))
            record['displayName']=relative.name+' · '+relative.parent.name.replace('_',' ')
            if item['artifact_type']=='agent_log':
                show_code=bool(re.search(r'fake.news|detoxify|qwen.?guard|llama.?guard|toxicity|toxibert|sentiment',str(relative),re.I))
                record['toolEvents']=tool_events(raw,summaries_by_sha.get(sha),show_code)
                record['readableReasoningCount']=len({e['reasoning']['index'] for e in record['toolEvents'] if e.get('reasoning')})
                record['reasoningSummaryCount']=len({e['reasoning']['index'] for e in record['toolEvents'] if e.get('reasoning',{}).get('summary')})
            group['outputs'].append(record)
        tasks.extend(groups.values())
        for source_label in ['Experiments','Community']:source_counts[source_label]=sum(len(t['outputs']) for t in tasks if t['source']==source_label)
    unique_hashes={o['sha256'] for t in tasks for o in t['outputs']}
    result=dict(schemaVersion=1,taskCount=len(tasks),templateTaskCount=template_count,tasksWithOutputs=sum(bool(t['outputs']) for t in tasks),outputCount=len(unique_hashes),sourceCounts=source_counts,
                displayNote='Saved-output index across workspaces, experiments, and community reports. Previews preserve structure with values redacted; numbered fields and record labels are presentation labels.',tasks=tasks)
    destination.write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n')
    print(f'Indexed {template_count} templates and {len(tasks)-template_count} result groups; {len(unique_hashes)} distinct files. Sources: {source_counts}')

if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('--templates',type=Path,required=True);parser.add_argument('--output',type=Path,required=True);parser.add_argument('--archive-inventory',type=Path);args=parser.parse_args();
    if args.output.exists() and not args.archive_inventory and len(json.loads(args.output.read_text()).get('sourceCounts',{}))>1:parser.error('--archive-inventory is required to preserve experiment/community sources')
    build(args.templates,args.output,args.archive_inventory)
