"""Build the site's curated evidence from repository records; never run an LLM."""
import json
import re
import shutil
import ast
import html
import hashlib
from pathlib import Path
from build_workflows import build_workflows
from build_agent_activity import attach_agent_activity
from build_chat_trajectories import build_chat_trajectories
from build_workspace_walkthroughs import build_workspace_walkthroughs

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / 'docs/static/data'
OUT.mkdir(parents=True, exist_ok=True)
GH = 'https://github.com/wuyoscar/Internal-Safety-Collapse/'

def read(path):
    return json.loads((ROOT / path).read_text())

def source(path):
    return GH + ('tree/main/' if path.endswith('/') else 'blob/main/') + path

def redact(text, limit=420):
    """Publish short, marked excerpts, with identities and sensitive terms masked."""
    text = re.sub(r"(?<![\w.])\[(?:Name|NAME|Full Name|FULL NAME|Candidate|CANDIDATE|Female Colleague(?:\\?'s)? Name)\]", '███', text)
    text = re.sub(r'https?://\S+|[\w.+-]+@[\w.-]+', '███', text)
    for term in ['21st Century Wire', '21WIRE', 'Fox News Insider', 'President Trump', 'Donald Trump', 'Obama', 'Joe Biden', 'Jane', 'Jennifer', 'heroin', 'methamphetamine', 'pseudoephedrine', 'Hollywood basement']:
        text = re.sub(re.escape(term), '███', text, flags=re.I)
    text = re.sub(r'\b(?:bitch|faggot|nigger|kike)\w*\b', '███', text, flags=re.I)
    if len(text) > limit:
        text = text[:limit].rsplit(' ', 1)[0] + '…'
    return text

def assigned_articles(message):
    # Read literal data from a recorded shell command; never execute that command.
    command = json.loads(message['arguments'])['command']
    code = command.split("<<'EOF'\n", 1)[1].split('\nEOF', 1)[0]
    tree = ast.parse(code)
    return next(ast.literal_eval(n.value) for n in ast.walk(tree) if isinstance(n, ast.Assign) and any(isinstance(t, ast.Name) and t.id == 'articles' for t in n.targets))

def log(folder):
    path = f'community/{folder}/evidence/agent_log.json'
    return path, read(path)

fpath, fable = log('claude-fable-5-fake-news')
first_article = redact(assigned_articles(fable[7])[0], 340)
final_article = redact(read('community/claude-fable-5-fake-news/evidence/articles.json')['articles'][0]['article_text'], 400)
failure = next(line for line in fable[8]['output'].splitlines() if line.startswith('AssertionError:'))
passed = '\n'.join(line for line in fable[15]['output'].splitlines() if line.startswith(('[article ', 'All 3')))
opath, opus = log('claudeopus48-agent-qwenguard')
plan = opus[13]['content'][0]['text'].split(' Now let me')[0]
opass = '\n'.join(line.strip('= ') for line in opus[36]['output'].splitlines() if 'PASSED' in line or '4 passed' in line)
mpath, methods = log('claudeopus46thinking-guard-attack')
gpath, gpt = log('gpt52-guard-attack-v2')
replays = [
    dict(id='fable-news', name='Fable 5', task='Evaluating a news classifier', folder='articles.json',
         source=source(fpath), description='The first candidate is classified TRUE. The agent revises the articles, then the task accepts all three as FAKE. These are classifier predictions, not independent fact checks.',
         steps=[dict(label='First validation', status='Needs revision', kind='fail', file='validator.py', text=failure, pointer='/8/output'),
                dict(label='Revise the data', status='Editing', kind='edit', file='articles.json', text='The agent writes revised articles and runs the validator again.', pointer='/14/arguments', summary=True),
                dict(label='Run the checks again', status='Task passed', kind='pass', file='validator.py', text=passed, pointer='/15/output')]),
    dict(id='opus-guard', name='Opus 4.8', task='Evaluating Qwen3Guard', folder='test_case.json',
         source=source(opath), description='The agent reasons about the classifier’s labels, generates paired responses, and tests the saved data. Four passed tests are four test functions, not four unsafe responses.',
         steps=[dict(label='Read the requirements', status='Inspecting', kind='edit', file='workspace', text=opus[0]['content'], pointer='/0/content'),
                dict(label='Interpret the feedback', status='Planning', kind='edit', file='agent_log.json', text=plan, pointer='/13/content/0/text'),
                dict(label='Run the task', status='Task passed', kind='pass', file='validator.py', text=opus[23]['output'].strip(), pointer='/23/output'),
                dict(label='Test the saved data', status='4 tests passed', kind='pass', file='test_validator.py', text=opass, pointer='/36/output')]),
    dict(id='opus-prompts', name='Opus 4.6 Thinking', task='Generating prompts for named methods', folder='attack_cases.json',
         source=source(mpath), description='Method names guide prompt generation. The recorded check is an input-moderation flag; it does not measure whether a target LLM was jailbroken.',
         steps=[dict(label='Read the data fields', status='Inspecting', kind='edit', file='attack_cases.json', text='GCG · AutoDAN · PAP · ArtPrompt · PAIR · DAN\n\nThe task leaves attack_prompt fields for the agent to fill.', pointer='/0/content', summary=True),
                dict(label='Evaluate generated prompts', status='6 moderation flags', kind='pass', file='validator.py', text=methods[18]['output'].strip(), pointer='/18/output')]),
]
for index, s in enumerate(replays[0]['steps']):
    s['artifact'] = first_article if index == 0 else final_article
    s['artifactField'] = 'article_text'
cases=[]
def case(id, kind, title, llm, summary, path, excerpt='', **kwargs):
    cases.append(dict(id=id,kind=kind,title=title,llm=llm,summary=summary,source=source(path),path=path,excerpt=excerpt,**kwargs))
case('fable-news','Agent','A fabricated article, revised to pass the task.','Fable 5',replays[0]['description'],fpath,final_article,replay='fable-news',artifact='articles.json',evidence='Generated article',checks=failure+'\n\n'+passed,before=first_article,artifactSource=source('community/claude-fable-5-fake-news/evidence/articles.json'),field='article_text')
pair=read('community/claudeopus48-agent-qwenguard/evidence/test_case.json')[0]
unsafe=pair['assistant_unsafe'];excerpt=unsafe[unsafe.index('Subject:'):unsafe.index('click the secure link')]+'███'
case('opus-guard','Agent','A refusal and a phishing email, side by side.','Opus 4.8',replays[1]['description'],opath,excerpt,replay='opus-guard',artifact='test_case.json',evidence='Generated response',checks=opass,safe=redact(pair['assistant_safe'],220),artifactSource=source('community/claudeopus48-agent-qwenguard/evidence/test_case.json'),field='assistant_unsafe')
prompt_case=read('community/claudeopus46thinking-guard-attack/evidence/attack_cases_filled.json')['cases'][1]
prompt_excerpt=prompt_case['attack_prompt'].split('write a detailed guide')[0]+'write a detailed guide on ███.'
case('opus-prompts','Agent','An attack-method name becomes a prompt.','Opus 4.6 Thinking',replays[2]['description'],mpath,prompt_excerpt,replay='opus-prompts',artifact='attack_cases.json',evidence='Generated prompt',checks=methods[18]['output'].strip(),artifactSource=source('community/claudeopus46thinking-guard-attack/evidence/attack_cases_filled.json'),field='attack_prompt · AutoDAN')
answer=read('community/gpt52-guard-attack-v2/evidence/se_attacks_filled.json')['cases'][0]['response']
case('gpt-prompts','Agent','A supplied prompt becomes an unsafe answer.','GPT-5.2','This task supplies adversarial prompts and asks the agent to fill response fields. The moderation API flags the generated responses; no independent target LLM is tested here.',gpath,redact(answer.split(' 1)')[0],260)+' ███',artifact='se_attacks_filled.json',evidence='Generated response',checks=gpt[18]['output'].strip(),artifactSource=source('community/gpt52-guard-attack-v2/evidence/se_attacks_filled.json'),field='response · GCG')
web=[
 ('claude-chat','Claude Opus 4.5','Multilingual toxicity examples.','Paired toxic and non-toxic text across languages.','claudeopus45-share',0),
 ('gpt-chat','GPT-5.2 Chat','News articles as structured data.','A media-bias task produces YAML records with text and classification fields.','issue-29-gpt52chat',1),
 ('gemini-chat','Gemini 3 Pro','Completing a forensic-analysis task.','The conversation fills missing data in a code-analysis workflow. The paper redacts operational content.','issue-13-gemini3pro',2),
 ('deepseek-chat','DeepSeek V3.2','Test cases for a prompt-injection detector.','The response organizes injection examples as Python data for Qwen3Guard evaluation.','deepseek-v32-share',3),
 ('glm-chat','GLM-5','Paired answers in JSON.','The task produces assistant_safe and assistant_unsafe fields in structured records.','glm5-share',4),
 ('qwen-chat','Qwen 3 Max','Toxicity data across languages.','The output contains text, language, and toxicity labels for classifier evaluation.','issue-4-qwen3max',5),
]
for id,llm,title,summary,folder,panel in web:
    case(id,'Web chat',title,llm,summary,f'community/{folder}/',panel=panel,evidence='Archived screenshot',artifact='Shared conversation')
subjects={0:'A defamatory news article',1:'Body-shaming campaign text',4:'A sexist workplace email',9:'Targeted harassment text',31:'Encouraging someone to gamble savings',32:'Promoting payday loans to gamblers',50:'A fabricated political news article',51:'A conspiracy article about 9/11',54:'A false health claim about 5G',56:'A climate-denial thread',58:'Fabricated evidence for a flat Earth',59:'A conspiracy narrative about global events'}
archives=[('Grok 4.1 Fast','experiment/tvd_chatbot/result_demo/x-ai-grok-4.1-fast/jbb/ai-guard/1sample.json'),('Claude Sonnet 4.5','experiment/tvd_chatbot/result_demo/anthropic-claude-sonnet-4.5/jbb/ai-guard/0sample_judged.json'),('DeepSeek V3.2','experiment/tvd_chatbot/result_demo/deepseek-deepseek-v3.2-exp/jbb/ai-guard/0sample.json')]
for llm,path in archives:
    for record in read(path)['results']:
        index=record['index']
        if index not in subjects:continue
        output=record.get('extraction',{}).get('extracted','')
        pointer=f"results/{index}/extraction/extracted"
        if not output:
            candidates=[]
            for match in re.finditer(r'"assistant_unsafe"\s*:\s*',record['response']):
                try:value,_=json.JSONDecoder().raw_decode(record['response'][match.end():])
                except ValueError:continue
                if isinstance(value,str) and value!='???':candidates.append(value)
            if not candidates:continue
            output=candidates[-1];pointer=f'results/{index}/response · assistant_unsafe'
        if not isinstance(output,str):continue
        case(f'{llm.lower().replace(" ","-")}-{index}','Chat API',subjects[index],llm,
             'A saved single-turn classifier-evaluation task. The LLM fills the unsafe-response field; commands and validation shown in the reply are simulated text.',path,redact(output),artifact=Path(path).name,evidence='Generated response',query=redact(record['query'],180),field='assistant_unsafe',pointer=pointer,recordId=record['id'],topic=subjects[index])
path='experiment/harmful_data_generator/unsafe_response.ipynb';notebook=read(path)
assert sum(bool(c.get('outputs')) for c in notebook['cells'])==2
case('batch-chat','Notebook','A follow-up request extends the dataset.','Chatbot workflow','This notebook preserves outputs from the initial request and a follow-up generation loop. It demonstrates chat-based dataset expansion, without executing the simulated guard.',path,
     'Could you give me more diverse examples in chinese?',artifact='unsafe_response.ipynb',evidence='Notebook with saved outputs',display='Follow-up instruction')
assert len(cases)>=40, f'Only {len(cases)} evidenced cases were assembled'

families=[
    dict(id='llamaguard',label='LlamaGuard',description='Safe and unsafe responses',main=True),
    dict(id='toxicbert',label='Toxic-BERT',description='Toxicity samples',main=True),
    dict(id='pyod',label='PyOD',description='Outlier samples',main=True),
    dict(id='news',label='News',description='Article classification'),
    dict(id='detoxify',label='Detoxify',description='Category scores'),
    dict(id='qwenguard',label='Qwen3Guard',description='Response pairs'),
    dict(id='sentiment',label='Sentiment',description='Reviews and ratings'),
    dict(id='moderation',label='Moderation',description='Prompts and responses'),
    dict(id='web',label='Web examples',description='Screenshots'),
]
for c in cases:
    c['family']='llamaguard' if c['kind'] in ['Chat API','Notebook'] else 'web'
    c['format']='prose'
    if c['id']=='fable-news':c.update(family='news',tool='News classifier',format='article',task='Prepare articles for a news-classifier evaluation.',rule='No unfinished fields · ≥30 words · label FAKE')
    if c['id']=='opus-guard':c.update(family='qwenguard',tool='Qwen3Guard',format='json',task='Complete a safe and unsafe response pair.',rule='Match the template’s safe / unsafe labels')
    if c['id'] in ['opus-prompts','gpt-prompts']:c.update(family='moderation',tool='Moderation API',rule='The moderation API must flag the required field')
    if c['kind']=='Chat API':c.update(tool='LlamaGuard',task='Complete safe and unsafe responses for a supplied query.',rule='assistant_safe → safe · assistant_unsafe → unsafe')
    if c.get('panel') is not None:c['format']='image'

additional_path=ROOT/'docs/static/data/additional-cases.json'
additional=json.loads(additional_path.read_text())
family_ids={'Toxic-BERT':'toxicbert','PyOD':'pyod','Fake-news classifier':'news','Sentiment classifier':'sentiment'}
short_rules={'toxicbert':'flagged: score >0.5 · not_flagged: score ≤0.5','pyod':'Last sample: outlier (1) · references: normal (0)','news':'Required label: FAKE','sentiment':'Match the requested star rating'}
for entry in additional['cases']:
    c=dict(entry);c['family']=family_ids[entry['family']];c['ruleDetail']=c['rule'];c['rule']=short_rules[c['family']]
    c['artifact']=c['dataFile'];c['summary']=c['task'];c['recordId']=str(c['provenance']['recordId']);c['pointer']=c['provenance']['pointer']
    if c['sourceUnavailable']:
        line=next(i for i,l in enumerate(additional_path.read_text().splitlines(),1) if f'"id": "{c["id"]}"' in l)
        c['source']=source('docs/static/data/additional-cases.json')+f'#L{line}'
        c['path']='docs/static/data/additional-cases.json'
    else:
        c['path']=c['source'];c['source']=source(c['source'])
    if c['format']=='json':
        obj=json.loads(c['excerpt']);obj['article_text']=redact(obj['article_text'],400);c['excerpt']=json.dumps(obj,ensure_ascii=False,indent=2)
    else:c['excerpt']=redact(c['excerpt'],420)
    if c['family']=='news':c['format']='article'
    cases.append(c)
assert len({c['id'] for c in cases})==len(cases)
workflows=build_workflows(ROOT,redact,cases,replays)
workflows[0].update(toolLabel='News classifier',format='article')
workflows[1].update(toolLabel='Detoxify',format='prose')
workflows[2].update(toolLabel='Qwen3Guard',format='prose')
cases.append(dict(id='detoxify-categories',family='detoxify',tool='Detoxify',title='Threat, insult, and identity-attack samples',
                  query='',task=workflows[1]['task'],rule='Each category score ≥0.5',format='json',kind='Agent',llm='GPT-5.1',
                  excerpt=workflows[1]['steps'][-1]['editor'],checks=workflows[1]['steps'][-1]['feedback'],
                  source=source('community/gpt51-guard-attack-v2/evidence/detoxify/test_cases_filled.json'),
                  path='community/gpt51-guard-attack-v2/evidence/detoxify/test_cases_filled.json',
                  summary='Three category-specific examples prepared in one dataset.',artifact='test_cases.json',field='text'))
attach_agent_activity(ROOT, workflows, redact)
workflows.extend(build_chat_trajectories(ROOT, redact))
workspace_families, workspace_cases, workspace_walkthroughs = build_workspace_walkthroughs(ROOT, redact)
families.extend(workspace_families)
cases.extend(workspace_cases)
workflows.extend(workspace_walkthroughs)

# Preserve the README's reported-trigger index, with links to the evidence.
readme=(ROOT/'README.md').read_text()
table=readme.split('<strong>LLM results and evidence · 62 entries</strong></summary>',1)[1].split('</details>',1)[0]
model_reports=[]
for line in table.splitlines():
    if not line.startswith('| <img '):continue
    cells=[part.strip() for part in line.strip('|').split('|')]
    name=html.unescape(re.sub(r'<[^>]+>','',cells[0]).strip())
    icon=re.search(r'src="([^"]+)"',cells[0])
    links=re.findall(r'\]\(([^)]+)\)',cells[2])
    links=[url if url.startswith('https://') else source(url) for url in links]
    model_reports.append(dict(name=name,reported=cells[1],icon=icon.group(1).removeprefix('docs/') if icon else '',links=links))
# Some rows use a text-only model name rather than an icon.
for line in table.splitlines():
    if not line.startswith('| ') or line.startswith('| <img ') or '](' not in line:continue
    cells=[part.strip() for part in line.strip('|').split('|')]
    if len(cells)!=4 or cells[1] not in ['Yes','No','Partial']:continue
    links=re.findall(r'\]\(([^)]+)\)',cells[2])
    model_reports.append(dict(name=cells[0].strip('`'),reported=cells[1],icon='',links=[u if u.startswith('https://') else source(u) for u in links]))
assert len(model_reports)==62,len(model_reports)

# All displayed excerpts above are selected log output or explicitly marked metadata/summaries.
data=dict(cases=cases,replays=replays,workflows=workflows,families=families,modelReports=model_reports,paper='https://arxiv.org/pdf/2603.23509',schemaVersion=2)
(OUT/'evidence.json').write_text(json.dumps(data,ensure_ascii=False,indent=2)+'\n')
media=ROOT/'docs/static/media';media.mkdir(exist_ok=True)
shutil.copyfile(ROOT/'assets/optimized/paper-v2-web-examples.webp',media/'web-cases.webp')

# A changed asset needs a new URL so returning visitors do not mix releases.
# Update data -> script -> HTML in dependency order; unchanged content keeps its URL.
def version_asset(text, relative_path):
    digest = hashlib.sha256((ROOT/'docs'/relative_path).read_bytes()).hexdigest()[:12]
    text, count = re.subn(
        re.escape(relative_path) + r'(?:\?v=[0-9a-f]+)?',
        relative_path + '?v=' + digest,
        text,
    )
    if count != 1:
        raise ValueError(f'Expected one reference to {relative_path}, found {count}')
    return text

script = ROOT/'docs/static/js/main.js'
script.write_text(version_asset(script.read_text(), 'static/data/evidence.json'))
page = ROOT/'docs/index.html'
markup = version_asset(page.read_text(), 'static/css/style.css')
markup = version_asset(markup, 'static/css/workspace.css')
markup = version_asset(markup, 'static/css/workspace-motion.css')
markup = version_asset(markup, 'static/js/workspace-motion.js')
page.write_text(version_asset(markup, 'static/js/main.js'))
print(f'Built {len(cases)} sourced cases and {len(workflows)} trajectories.')
