"""Attach source-log commands and file inspections to the site's agent trajectories."""
import ast
import io
import json
import re
import tokenize


def attach_agent_activity(root, workflows, redact):
    def clean(text, limit=1800):
        text = re.sub(r'\x1b\[[0-9;]*m', '', text)
        text = '\n'.join(line for line in text.splitlines() if not re.search(r'Loading weights:|it/s|BertForSequenceClassification LOAD REPORT|^Downloading:', line))
        return redact(text, limit)

    def shorten_literals(code, paired=False):
        """Keep the source program's structure while redacting long data literals."""
        lines = code.splitlines(keepends=True)
        offsets = [0]
        for line in lines: offsets.append(offsets[-1] + len(line))
        edits = []
        long_count = 0
        try:
            for token in tokenize.generate_tokens(io.StringIO(code).readline):
                if token.type != tokenize.STRING: continue
                try: value = ast.literal_eval(token.string)
                except (ValueError, SyntaxError): continue
                if not isinstance(value, str) or len(value) < 100: continue
                long_count += 1
                value = '███' if paired and long_count > 2 else redact(value, 150)
                value = re.sub(r'Black people|immigrants|break every bone in your body|kill you', '███', value, flags=re.I)
                start = offsets[token.start[0]-1] + token.start[1]
                end = offsets[token.end[0]-1] + token.end[1]
                edits.append((start, end, json.dumps(value, ensure_ascii=False)))
        except (tokenize.TokenError, IndentationError): pass
        for start, end, value in reversed(edits): code = code[:start] + value + code[end:]
        return code

    def command(entry):
        args = entry['arguments']
        if isinstance(args, str): args = json.loads(args)
        return args['command']

    def display_command(entry):
        value = command(entry)
        match = re.search(r"<<\s*['\"]?(\w+)['\"]?[^\n]*\n", value)
        if match:
            end = re.search(r'^' + re.escape(match[1]) + r'\s*$', value[match.end():], re.M)
            if end:
                start, stop = match.end(), match.end() + end.start()
                value = value[:start] + shorten_literals(value[start:stop], 'responses = [' in value) + value[stop:]
        return redact(re.sub(r'\x1b\[[0-9;]*m', '', value), 2800)

    def events(log, indices):
        result = []
        for i in indices:
            entry = log[i]
            if entry.get('type') == 'function_call':
                result.append(dict(kind='command', text=display_command(entry), language='shell', pointer=f'/{i}/arguments', tool=entry.get('name','shell')))
            elif entry.get('type') == 'function_call_output':
                result.append(dict(kind='output', text=clean(entry['output']), language='text', pointer=f'/{i}/output'))
            elif entry.get('role') == 'assistant':
                content = entry.get('content', [])
                text = content if isinstance(content,str) else '\n'.join(c.get('text','') for c in content)
                result.append(dict(kind='assistant', text=clean(text,550), language='text', pointer=f'/{i}/content'))
        return result

    def extra(log, indices, label, file, editor, language='text', phase='inspect', data='pending', tool='pending', tests='pending'):
        return dict(label=label, phase=phase, editor=editor, file=file, language=language,
                    feedback='', feedbackKind='Recorded output', pointer='; '.join(f'/{i}' for i in indices),
                    activity=events(log, indices), checks=dict(data=data,tool=tool,tests=tests))

    def equip(w, log, mapping, unsafe):
        w.update(mode='agent', unsafeFields=unsafe, files=[w['file'],'validator.py','test_validator.py'])
        for s, indices in zip(w['steps'], mapping):
            s.update(activity=events(log, indices), language='json', unsafeFields=unsafe)
        return w['steps']

    news, tox, pairs = workflows
    f = json.loads((root/'community/claude-fable-5-fake-news/evidence/agent_log.json').read_text())
    old = equip(news,f,[[5,6],[7],[8],[9,10],[11,12],[13,14],[15]],['article_text'])
    news['steps'] = [
        extra(f,[1,2],'Explore the workspace','workspace',f[2]['output'].strip()),
        extra(f,[3,4],'Inspect the validation code','validator.py',clean(f[4]['output'].split('\n---\n')[0],2600),'python'),
        *old,
    ]

    t = json.loads((root/'community/gpt51-guard-attack-v2/evidence/detoxify/agent_log.json').read_text())
    old = equip(tox,t,[[3,4],[9,10],[13,14],[15,16],[17,18],[19,20]],['text','text_threat','text_insult','text_id'])
    tox['steps'] = [
        extra(t,[1,2],'Explore the workspace','workspace',t[2]['output'].strip()),
        old[0],
        extra(t,[5,6],'Inspect the score checks','validator.py',clean(t[6]['output'],2600),'python'),
        extra(t,[7,8],'Read the tests','test_validator.py',clean(t[8]['output'],2600),'python'),
        old[1],
        extra(t,[11,12],'Try category-specific wording','classifier input',display_command(t[11]),'shell',phase='probe'),
        *old[2:],
    ]

    p = json.loads((root/'community/claudeopus48-agent-qwenguard/evidence/agent_log.json').read_text())
    old = equip(pairs,p,[[4,5,6,7],[11,12,13],[22,23],[35,36]],['assistant_unsafe'])
    old[2].update(label='Run the validator', phase='probe')
    pairdata = old[2]['editor']
    pairs['files'] += ['probe.py','responses.py','test_resp.py','pytest.log']
    pairs['steps'] = [
        extra(p,[1,2,3],'Explore the workspace','workspace',clean(p[3]['output'])),
        old[0],
        extra(p,[8,9,10],'Check the runtime','workspace',clean(p[10]['output'])),
        old[1],
        extra(p,[14,15],'Write the response pairs','responses.py',display_command(p[14]),'shell',phase='write'),
        extra(p,[16,17,18],'Test the pairs with the guard','test_resp.py',display_command(p[17]),'shell',phase='probe',tool='pass'),
        extra(p,[19,20,21],'Save the response pairs','test_cases.json',pairdata,'json',phase='write',data='written',tool='pass'),
        old[2],
        extra(p,[24,25,26],'Run the test suite','test_cases.json',pairdata,'json',phase='timeout',data='written',tool='pass'),
        extra(p,[27,28,29],'Retry with a longer timeout','test_cases.json',pairdata,'json',phase='timeout',data='written',tool='pass'),
        extra(p,[30,31,32],'Run pytest in the background','test_cases.json',pairdata,'json',phase='probe',data='written',tool='pass'),
        extra(p,[33,34],'Read the test progress','pytest.log',clean(p[34]['output']),'text',phase='probe',data='written',tool='pass'),
        old[3],
    ]
    for w in workflows:
        for s in w['steps']: s.setdefault('unsafeFields',w['unsafeFields'])
