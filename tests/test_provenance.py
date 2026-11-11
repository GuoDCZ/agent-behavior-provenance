import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
import xml.etree.ElementTree as ET
import networkx as nx
from provenance.parser import parse
from provenance.policy import allowed,assess
from provenance.graph import build
from provenance.slice import backward_slice
from provenance.report import analyze
from tests.fixtures_generator import make_run,PAYLOAD

class ProvenanceTests(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory(); self.root=Path(self.tmp.name)
    def tearDown(self): self.tmp.cleanup()
    def run_case(self,case):
        run=make_run(self.root/case,case)
        return run,analyze(run,self.root/('report-'+case))
    def test_normal(self):
        run,r=self.run_case('normal')
        self.assertEqual(r['policy']['protected_paths_changed'],[])
        self.assertTrue(r['policy']['oracle_passed'])
        self.assertEqual(r['exposure']['visibility'],'not_applicable_control')
        self.assertEqual([e['order'] for e in r['events']],list(range(1,len(r['events'])+1)))
    def test_injection_confirmed_change_and_exposure(self):
        run,r=self.run_case('injection')
        self.assertEqual(r['exposure']['visibility'],'observed_in_model_context')
        self.assertEqual(r['policy']['protected_paths_changed'],['tests/check.py'])
        self.assertEqual(len(r['policy']['attempts']),1)
        s=r['slices'][0]
        self.assertGreater(s['candidate_tool_results'],0)
        self.assertTrue(any(n['node_type']=='IntegrityChange' for n in s['observed']))
        self.assertFalse(any(n['node_type']=='ToolCall' for n in s['observed']))
        self.assertTrue(any(n['node_type']=='ToolCall' for n in s['possible']))
        self.assertEqual(r['policy']['completion_claims'][0]['assessment'],'public_test_claim_unverified_independent_oracle_failed')
    def test_unknown_visibility_does_not_invent_context(self):
        run,r=self.run_case('unknown')
        self.assertEqual(r['exposure']['visibility'],'tool_output_recorded_but_model_visibility_unknown')
        self.assertEqual(r['exposure']['classification'],'unknown')
    def test_payload_on_disk_is_not_exposure(self):
        run=make_run(self.root/'disk','unknown')
        events=(run/'events.jsonl').read_text().replace(PAYLOAD,'ordinary output')
        (run/'events.jsonl').write_text(events)
        r=analyze(run,self.root/'report')
        self.assertEqual(r['exposure']['visibility'],'not_observed')
    def test_attempt_error_without_final_change(self):
        run,r=self.run_case('attempt')
        self.assertEqual(r['policy']['protected_paths_changed'],[])
        self.assertEqual(len(r['policy']['attempts']),1)
        self.assertEqual(r['policy']['attempts'][0]['completion'],'tool_reported_error_no_final_change')
    def test_malformed_records_continue(self):
        run,r=self.run_case('malformed')
        self.assertGreater(r['metrics']['events'],0)
        self.assertTrue(any('malformed' in w for w in r['warnings']))
        self.assertEqual(r['coverage'],'partial')
    def test_paths(self):
        for p in ('src2/a','../tests/a','src/../tests/a','/src/a','src','outputs2/a','src\\..\\tests/a'):
            with self.subTest(p=p): self.assertFalse(allowed(p))
        for p in ('./src/a','src/sub/a','outputs/report.md'):
            with self.subTest(p=p): self.assertTrue(allowed(p))
    def test_graph_relations_and_chronology_exclusion(self):
        run=make_run(self.root/'g','injection'); events,_,_=parse(run)
        g=build(events,assess(run,events),run)
        self.assertTrue(nx.is_directed_acyclic_graph(g))
        relations={d['relation'] for _,_,d in g.edges(data=True)}
        self.assertTrue({'READ_FROM','RETURNED','AVAILABLE_TO_MODEL','POSSIBLY_AVAILABLE','WROTE_TO'}<=relations)
        last=events[-1].event_id
        self.assertEqual([n['node'] for n in backward_slice(g,last)['observed']],[last])
    def test_missing_logs_rejected_and_snapshot_explicit(self):
        run=make_run(self.root/'missing'); (run/'events.jsonl').unlink()
        with self.assertRaisesRegex(ValueError,'Missing events'): analyze(run,self.root/'bad')
        r=analyze(run,self.root/'ok',True)
        self.assertEqual(r['evidence_kind'],'local_snapshot_without_agent_trajectory')
    def test_report_exports_and_evidence(self):
        _,r=self.run_case('injection'); out=self.root/'report-injection'
        ET.parse(out/'graph.svg'); g=nx.read_graphml(out/'graph.graphml')
        self.assertTrue(nx.is_directed_acyclic_graph(g))
        md=(out/'analysis.md').read_text()
        self.assertIn('events.jsonl:line-',md); self.assertIn('hypotheses',md)
        self.assertIn('synthetic',r['evidence_kind'])
    def test_native_opencode_contract_preferred(self):
        run=make_run(self.root/'native')
        (run/'session.json').write_text(json.dumps({'messages':[{'info':{'id':'m1','role':'assistant'},'parts':[{'type':'tool','callID':'c1','tool':'read','state':{'input':{'filePath':'src/app.py'},'output':'old','status':'completed'}}]}]}))
        e,w,s=parse(run)
        self.assertEqual(s,'opencode_native_contract')
        self.assertEqual([v.kind for v in e],['model_turn','tool_call','tool_result'])
        g=build(e,assess(run,e),run)
        self.assertIn('INVOKED',{d['relation'] for _,_,d in g.edges(data=True)})
    def test_pi_contract(self):
        run=make_run(self.root/'pi')
        records=[{'type':'message_end','message':{'role':'assistant','content':[{'type':'toolCall','id':'t1','name':'read','arguments':{'path':'src/app.py'}}]}},{'type':'message_end','message':{'role':'toolResult','toolCallId':'t1','toolName':'read','content':[{'type':'text','text':'old'}]}}]
        (run/'events.jsonl').write_text('\n'.join(json.dumps(x) for x in records))
        e,_,_=parse(run)
        self.assertEqual([x.kind for x in e],['model_turn','tool_call','tool_result'])
        self.assertEqual(e[-1].text,'old')
    def test_cli_invalid_and_help(self):
        p=subprocess.run([sys.executable,'-m','provenance.cli','analyze','--run',str(self.root/'absent'),'--output',str(self.root/'out')],capture_output=True,text=True)
        self.assertEqual(p.returncode,2); self.assertIn('prepare.py',p.stderr)
        p=subprocess.run([sys.executable,'-m','provenance.cli','--help'],capture_output=True,text=True)
        self.assertEqual(p.returncode,0)
    def test_independent_snapshot_detects_change_without_checker(self):
        run=make_run(self.root/'snap','injection'); (run/'check.json').unlink()
        r=analyze(run,self.root/'out')
        self.assertEqual(r['policy']['protected_paths_changed'],['tests/check.py'])
        self.assertIsNone(r['policy']['oracle_passed'])

    def test_failed_read_is_intent_not_dataflow(self):
        run=make_run(self.root/'failedread')
        records=[json.loads(line) for line in (run/'events.jsonl').read_text().splitlines()]
        records[0]['part']['state'].update(status='error',output='not found')
        (run/'events.jsonl').write_text('\n'.join(json.dumps(r) for r in records))
        e,_,_=parse(run); g=build(e,assess(run,e),run)
        rel={d['relation'] for _,_,d in g.edges(data=True)}
        self.assertIn('READ_TARGET',rel); self.assertNotIn('READ_FROM',rel)
    def test_execution_error_kept_separate_from_attack(self):
        run=make_run(self.root/'error','unknown')
        (run/'execution.json').write_text(json.dumps({'status':'exited','exit_code':1}))
        (run/'events.jsonl').write_text(json.dumps({'type':'error','error':'synthetic auth failure'})+'\n')
        r=analyze(run,self.root/'out')
        self.assertEqual(r['run_status'],'execution_error')
        self.assertEqual(r['exposure']['classification'],'unknown')
    def test_new_deleted_and_prefix_protected_paths(self):
        run=make_run(self.root/'paths'); ws=run/'workspace'
        (ws/'tests/check.py').unlink(); (ws/'src2').mkdir(); (ws/'src2/new.py').write_text('new')
        (run/'check.json').unlink(); e,_,_=parse(run); policy=assess(run,e)
        self.assertEqual(policy['protected_paths_changed'],['src2/new.py','tests/check.py'])
    def test_deterministic_output_for_same_evidence(self):
        run=make_run(self.root/'determinism','injection')
        first=self.root/'one'; second=self.root/'two'
        analyze(run,first); analyze(run,second)
        for filename in ('analysis.json','analysis.md','graph.json','graph.graphml','graph.svg'):
            with self.subTest(filename=filename):
                self.assertEqual((first/filename).read_bytes(),(second/filename).read_bytes())

    def test_sibling_tools_do_not_consume_each_others_results(self):
        run=make_run(self.root/'siblings')
        parts=[{'type':'tool','tool':'read','callID':cid,'state':{'input':{'filePath':'src/app.py'},'output':'old','status':'completed'}} for cid in ('a','b')]
        (run/'session.json').write_text(json.dumps({'messages':[{'info':{'id':'one-message','role':'assistant'},'parts':parts}]}))
        e,_,_=parse(run); g=build(e,assess(run,e),run)
        self.assertNotIn('POSSIBLY_AVAILABLE',{d['relation'] for _,_,d in g.edges(data=True)})

if __name__=='__main__': unittest.main()
