"""Source rendering checks: preserve event identity, mask values, never execute logs."""
import ast
import json
from pathlib import Path
import tempfile
import unittest

from docs.build_task_library import command_excerpt, python_excerpt, tool_events


class SourceRenderingTests(unittest.TestCase):
    def test_parallel_tool_outputs_follow_call_ids(self):
        records=[
            dict(type='function_call',call_id='a',name='shell',arguments='{"command":"cat articles.json"}'),
            dict(type='function_call',call_id='b',name='shell',arguments='{"command":"python validator.py"}'),
            dict(type='function_call_output',call_id='b',output='ValidationError: private detail'),
            dict(type='function_call_output',call_id='a',output='2 passed in 0.1s'),
        ]
        events=tool_events(json.dumps(records))
        self.assertEqual(events[0]['result'],'2 passed in 0.1s')
        self.assertEqual(events[1]['phase'],'fail')
        self.assertNotIn('private detail',events[1]['result'])

    def test_code_keeps_structure_without_payload_literals(self):
        code="""from transformers import pipeline
classifier = pipeline('text-classification', model='example/news-classifier')
data = {'article_text': 'private payload', 'expected_label': 'FAKE'}
json.dump(data, open('articles.json', 'w'))
"""
        excerpt=python_excerpt(code)
        ast.parse(excerpt)
        self.assertIn('example/news-classifier',excerpt)
        self.assertIn('article_text',excerpt)
        self.assertNotIn('private payload',excerpt)
        self.assertIn('███',excerpt)

    def test_logged_code_is_parsed_without_execution(self):
        with tempfile.TemporaryDirectory() as tmp:
            target=Path(tmp)/'must-not-exist.txt'
            command="python3 - <<'PY'\nfrom pathlib import Path\nPath("+repr(str(target))+").write_text('private')\nPY"
            excerpt=command_excerpt(command)
            self.assertFalse(target.exists())
            self.assertNotIn(str(target),excerpt['editor'])
            self.assertEqual(excerpt['origin'],'source-excerpt')

    def test_timeout_and_unrecognized_outputs_are_not_passes(self):
        def record(output):
            return tool_events(json.dumps([
                dict(type='function_call',name='shell',call_id='a',arguments='{"command":"python validator.py"}'),
                dict(type='function_call_output',call_id='a',output=output),
            ]))[0]
        self.assertEqual(record('Error: timed out after 120s')['phase'],'timeout')
        self.assertEqual(record('private result')['result'],'Tool output · values redacted')

    def test_progress_is_masked_and_does_not_hide_errors(self):
        records=[
            dict(type='function_call',name='shell',call_id='a',arguments='{"command":"python validator.py"}'),
            dict(type='function_call_output',call_id='a',output='Loading checkpoint shards: 10% PRIVATE_SENTINEL\nAssertionError: private detail'),
        ]
        event=tool_events(json.dumps(records))[0]
        self.assertEqual(event['phase'],'fail')
        self.assertIn('Loading checkpoint shards: 10%',event['result'])
        self.assertNotIn('PRIVATE_SENTINEL',event['result'])
        records[1]['output']='from pydantic import ValidationError'
        self.assertNotEqual(tool_events(json.dumps(records))[0]['phase'],'fail')


if __name__=='__main__':
    unittest.main()
