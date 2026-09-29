"""Application-level event prefixes, administrative censoring and audit."""
from pathlib import Path
from datetime import datetime,timezone
from collections import Counter
import gzip,json,xml.etree.ElementTree as ET
import numpy as np
import pandas as pd
from research_program.io import download,data_dir,write_json
HERE=Path(__file__).resolve().parent
CONFIG=json.loads((HERE/'config.json').read_text())
DAY=86400


def stamp(value):
    return datetime.fromisoformat(value.replace('Z','+00:00')).timestamp()


def discretize(remaining,event,exposure,horizon=30):
    if event and remaining<=exposure and remaining<=horizon:
        return max(1,int(np.ceil(remaining))),1
    return max(0,min(horizon,int(np.floor(exposure)))),0


def prefix_features(events,k,start):
    prefix=events[:k];now=prefix[-1]['timestamp'];latest=next((e['activity'] for e in reversed(prefix) if e['activity'].startswith('A_')),'unknown')
    gaps=np.diff([e['timestamp'] for e in prefix])/DAY
    row={'prefix':k,'age_days':(now-start)/DAY,'last_gap_days':float(gaps[-1]) if len(gaps) else 0,'max_gap_days':float(gaps.max()) if len(gaps) else 0,'mean_gap_days':float(gaps.mean()) if len(gaps) else 0,'stage':latest,'last_activity':prefix[-1]['activity'],'last_lifecycle':prefix[-1]['lifecycle'],'offers_created':sum(e['activity']=='O_Create Offer' for e in prefix)}
    for activity,n in Counter(e['activity'] for e in prefix).items():row['activity:'+activity]=n
    for lifecycle,n in Counter(e['lifecycle'] for e in prefix).items():row['lifecycle:'+lifecycle]=n
    stages=[e for e in prefix if e['activity'].startswith('A_')]
    row['transitions']=[{'from':a['activity'],'to':b['activity'],'elapsed_days':(b['timestamp']-a['timestamp'])/DAY} for a,b in zip(stages,stages[1:])]
    row['age_band']=0 if row['age_days']<1 else (1 if row['age_days']<=7 else 2)
    return row


def ingest():
    folder=data_dir('S58');source=download(CONFIG['source_url'],folder/'BPIChallenge2017.xes.gz',CONFIG['sha256'],max_bytes=35_000_000)
    if source.stat().st_size!=CONFIG['bytes']:raise ValueError('Source size changed')
    records=[];activity=Counter();lifecycle=Counter();trace_count=event_count=unordered=duplicate_ids=0;offers={};offer_cross_trace=0;events_with_offer=0;missing_terminal=0;last_timestamp=0
    for _,trace in ET.iterparse(gzip.open(source,'rb'),events=('end',)):
        if trace.tag.rsplit('}',1)[-1]!='trace':continue
        events=[];ids=set()
        for node in trace:
            if node.tag.rsplit('}',1)[-1]!='event':continue
            fields={x.attrib['key']:x.attrib.get('value') for x in node if 'key' in x.attrib};eid=fields.get('EventID')
            if eid in ids:duplicate_ids+=1
            ids.add(eid);name=fields['concept:name'];life=fields['lifecycle:transition'];time=stamp(fields['time:timestamp'])
            events.append({'activity':name,'lifecycle':life,'timestamp':time,'offer':fields.get('OfferID'),'event_id':eid});activity[name]+=1;lifecycle[life]+=1;event_count+=1;last_timestamp=max(last_timestamp,time)
            if fields.get('OfferID'):
                events_with_offer+=1;offer=fields['OfferID']
                if offer in offers and offers[offer]!=trace_count:offer_cross_trace+=1
                offers[offer]=trace_count
        if not events:raise ValueError('Empty application trace')
        if any(a['timestamp']>b['timestamp'] for a,b in zip(events,events[1:])):unordered+=1;events.sort(key=lambda e:e['timestamp'])
        start=events[0]['timestamp'];terminal=next((i for i,e in enumerate(events) if e['activity'] in CONFIG['terminal_statuses']),None)
        target_time=events[terminal]['timestamp'] if terminal is not None else None
        if target_time is None:missing_terminal+=1
        for k in CONFIG['prefix_lengths']:
            base={'application':trace_count,'start':start,'prefix':k,'source_events':len(events),'has_prefix':len(events)>=k}
            if len(events)<k:base['reason']='too_short';records.append(base);continue
            if terminal is not None and terminal<k:base['reason']='already_dispositioned';records.append(base);continue
            now=events[k-1]['timestamp'];features=prefix_features(events,k,start)
            records.append({**base,**features,'reason':'eligible','prefix_time':now,'target_time':target_time,'remaining_days':(target_time-now)/DAY if target_time is not None else np.nan})
        trace_count+=1;trace.clear()
    if trace_count!=CONFIG['applications'] or event_count!=CONFIG['events'] or last_timestamp!=stamp(CONFIG['file_cutoff']):raise ValueError('Source coverage changed')
    if offer_cross_trace:raise ValueError('Offer identifiers cross application boundaries')
    frame=pd.DataFrame(records)
    cohorts={};cohort_audit={}
    dates={
        'development':('2016-01-01','2016-09-01','2016-09-01','2016-10-01'),
        'validation':('2016-09-01','2016-10-01','2016-10-01','2016-11-01'),
        'final_training':('2016-01-01','2016-10-01','2016-11-01','2016-12-01'),
        'test':('2016-12-01','2017-01-01','2017-01-01',CONFIG['file_cutoff'])}
    for name,(start_min,start_max,entry_max,end) in dates.items():
        times=[stamp(x+'T00:00:00Z' if len(x)==10 else x) for x in [start_min,start_max,entry_max,end]]
        potential=frame[(frame.start>=times[0])&(frame.start<times[1])].copy();eligible=potential[(potential.reason=='eligible')&(potential.prefix_time<times[2])].copy()
        eligible['exposure_days']=(times[3]-eligible.prefix_time)/DAY
        eligible['event_observed']=eligible.target_time.notna()&(eligible.target_time<times[3])
        survival=[discretize(r.remaining_days,bool(r.event_observed),r.exposure_days) for r in eligible.itertuples()]
        eligible['risk_days']=[x[0] for x in survival];eligible['event_day']=[x[0] if x[1] else 0 for x in survival]
        eligible['complete_horizon']=(eligible.exposure_days>=CONFIG['horizon'])|eligible.event_observed
        eligible['restricted_days']=np.where(eligible.event_observed,np.minimum(np.maximum(np.ceil(eligible.remaining_days),1),30),30)
        eligible['weight']=1/eligible.groupby('application').application.transform('size')
        count_columns=[x for x in eligible if x.startswith(('activity:','lifecycle:'))];eligible[count_columns]=eligible[count_columns].fillna(0)
        cohorts[name]=eligible.reset_index(drop=True)
        cohort_audit[name]={'applications_considered':int(potential.application.nunique()),'prefix_slots':len(potential),'prefixes':len(eligible),'applications':int(eligible.application.nunique()),'already_dispositioned':int((potential.reason=='already_dispositioned').sum()),'too_short':int((potential.reason=='too_short').sum()),'entry_after_cutoff':int(((potential.reason=='eligible')&(potential.prefix_time>=times[2])).sum()),'administratively_censored':int((~eligible.event_observed).sum()),'restricted_horizon_incomplete':int((~eligible.complete_horizon).sum()),'prefix_counts':eligible.prefix.value_counts().sort_index().to_dict()}
    if not cohorts['validation'].complete_horizon.all() or not cohorts['test'].complete_horizon.all():raise ValueError('Incomplete evaluation horizon')
    if set(cohorts['test'].application)&set(cohorts['final_training'].application):raise ValueError('Application leakage')
    audit={'applications':trace_count,'events':event_count,'activity_counts':dict(activity),'lifecycle_counts':dict(lifecycle),'unordered_traces_sorted':unordered,'repeated_event_ids_within_application':duplicate_ids,'events_with_offer_id':events_with_offer,'distinct_offer_references':len(offers),'offer_cross_application_conflicts':offer_cross_trace,'applications_without_target_status':missing_terminal,'file_cutoff_utc':CONFIG['file_cutoff'],'cohorts':cohort_audit}
    write_json(folder/'ingestion-audit.json',audit)
    return cohorts,audit
