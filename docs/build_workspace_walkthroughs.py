"""Presentation walkthroughs from workspace code and archived output excerpts."""
import json

GH = 'https://github.com/wuyoscar/Internal-Safety-Collapse/blob/main/'


def build_workspace_walkthroughs(root, redact):
    path = root/'docs/static/data/workspace-outputs.json'
    source = json.loads(path.read_text())
    families, cases, workflows = [], [], []
    for w in sorted(source['workspaces'], key=lambda item: 0 if item.get('domain') else 1):
        families.append(dict(id=w['id'],label=w['label'],description=w['task']))
        line=next(i for i,text in enumerate(path.read_text().splitlines(),1) if f'"id": "{w["id"]}"' in text)
        url=GH+'docs/static/data/workspace-outputs.json'+f'#L{line}'
        for example in w['examples']:
            example_line=next(i for i,text in enumerate(path.read_text().splitlines(),1) if f'"id": "{example["id"]}"' in text)
            cases.append(dict(id=example['id'],title=example['title'],family=w['id'],tool=w['label'],kind='Saved reply',llm='Workspace archive',
                              excerpt=example['excerpt'],field=example['field'],format=example['format'],artifact=w['file'],query=w['task'],task=w['task'],rule=w['rule'],
                              summary=w['task'],source=GH+'docs/static/data/workspace-outputs.json'+f'#L{example_line}',path='docs/static/data/workspace-outputs.json',
                              sourceUnavailable=True,displayNote='Saved output excerpt. The task walkthrough adapts it to the current workspace.',provenance=example['provenance'],
                              walkthrough='task-'+w['id'],unsafeFields=example.get('unsafeFields', [example['field']] if w['id']!='conllu' else [])))
        rows=[]
        for i,e in enumerate(w['examples']):
            value=e['excerpt']
            if w['id']=='propaganda':
                # The paired workspace needs a neutral reference; this is editorial
                # example text, not another archived LLM response.
                neutral=('This example presents a public-policy discussion in neutral terms. People may compare the available options, examine the evidence behind each proposal, and consider the interests of different groups. A useful report distinguishes documented observations from predictions and explains the limits of the information it presents. Readers can check the sources, identify unresolved questions, and compare alternative explanations before reaching a conclusion. The discussion can include different perspectives without treating disagreement as a personal failing or demanding loyalty to a particular group. Its purpose is to describe the issue clearly and provide enough context for readers to assess the arguments themselves.')
                row=dict(id=i,topic=e['title'],text_neutral=redact(neutral,330),text_propaganda=value)
            elif w['id']=='emotion':row=dict(id=i,target_emotion=e['metadata']['target_emotion'],text=value)
            elif w['id']=='clickbait':row=dict(id=i,headline=value)
            else:row=dict(id=i,text=value)
            rows.append(row)
        field='text_propaganda' if w['id']=='propaganda' else 'headline' if w['id']=='clickbait' else 'text'
        initial=[dict(row,**{field:'???'}) for row in rows]
        if w['id']=='propaganda':
            for row in initial:row['text_neutral']='???'
        file=w['file'];language='json'
        before=json.dumps(initial,ensure_ascii=False,indent=2)
        after=json.dumps(rows,ensure_ascii=False,indent=2)
        if w['id']=='conllu':
            file='build_corpus.py';language='python'
            before='CORPUS_CONLLU = """\\\n# sent_id = HS-002\n# text = ???\n1\t???\t_\t_\t_\t_\t_\t_\t_\t_\n"""'
            after='CORPUS_CONLLU = """\\\n'+w['examples'][0]['excerpt']+'\n"""'
        unsafe=[field] if w['id']!='conllu' else []
        if w.get('presentation'):
            before=w['presentation']['initial'];after=w['presentation']['filled'];language=w['presentation']['language'];unsafe=w['presentation']['unsafeFields']
        def event(kind,text,language='text'):
            return dict(kind=kind,text=text,language=language,pointer='/workspaces/'+w['id'],origin='presentation')
        def step(label,phase,editor,active_file,activity,lang=language):
            return dict(label=label,phase=phase,editor=editor,file=active_file,language=lang,activity=activity,
                        feedback='',feedbackKind='Task walkthrough',pointer='/workspaces/'+w['id'],unsafeFields=unsafe,
                        checks=dict(data='pending',tool='pending',tests='pending'))
        # Commands connect the task and artifact for presentation, without
        # inventing intermediate observations, scores, or a successful run.
        write=f"cat > {file} <<'DATA'\n{after}\nDATA"
        steps=[
            step('Inspect the unfinished data','inspect',before,file,[event('command',f'cat {file}','shell')]),
            step('Read the task code','inspect',w['taskCode'],w['runner'],[event('command',f'cat {w["runner"]}','shell')],'python'),
            step('Fill the generated fields','write',after,file,[event('command',write,'shell')]),
            step('Run the task checks','inspect',after,file,[event('command',f'python {w["runner"]}','shell'),event('assistant','The task checks: '+w['rule'])]),
        ]
        if w.get('domain'):
            steps[0]['label']='Inspect the artifact layout'
            steps[1]['label']='Read the format interface'
            steps[2]['label']='View the generated artifact'
            steps[3]['label']='Review the record fields'
        workflows.append(dict(id='task-'+w['id'],title=w['label'],mode='walkthrough',llm='Task walkthrough',file=file,
                              files=[file,w['runner'],'validator.py'] if w['id']!='conllu' else [file,w['runner']],
                              tool=w['tool'],toolLabel=w.get('toolLabel') or ('Python package' if w['id'] in ['conllu','vader'] else 'Hugging Face'),task=w['task'],rule=w['rule'],format='json',source=url,
                              note='Task walkthrough assembled from workspace code and saved output. '+w['adaptation']+(' The neutral comparison text is editorial example text.' if w['id']=='propaganda' else ''),steps=steps))
    return families,cases,workflows
