"""Restricted Bitcoin Core RPC to MQTT telemetry. No wallet or lifecycle calls."""
import base64
import json
import re
import signal
import threading
import time
import urllib.request
from pathlib import Path
from urllib.parse import urlsplit

METHODS = frozenset(('getblockchaininfo', 'getnetworkinfo', 'getnettotals', 'uptime'))
STOP = threading.Event()

class NoRedirect(urllib.request.HTTPRedirectHandler):
    def redirect_request(self, req, fp, code, msg, headers, newurl):
        return None

class RPC:
    def __init__(self, options):
        self.url = options['rpc_url']
        u = urlsplit(self.url)
        if u.scheme not in ('http', 'https') or not u.hostname or u.username or u.password or u.query or u.fragment or u.path not in ('', '/'):
            raise ValueError('RPC URL must be a node root HTTP(S) URL without credentials')
        if u.scheme == 'http' and not options['allow_insecure_rpc']:
            raise ValueError('Plain HTTP RPC requires explicit opt-in')
        if not options['rpc_username'] or not options['rpc_password']:
            raise ValueError('Dedicated RPC credentials required')
        self.auth = 'Basic ' + base64.b64encode((options['rpc_username'] + ':' + options['rpc_password']).encode()).decode()
        self.opener = urllib.request.build_opener(urllib.request.ProxyHandler({}), NoRedirect())

    def call(self, method):
        if method not in METHODS:
            raise ValueError('RPC method not allowed')
        request = urllib.request.Request(self.url, json.dumps({'jsonrpc':'1.0','id':'monitor','method':method,'params':[]}).encode(), {'Authorization':self.auth,'Content-Type':'application/json'})
        with self.opener.open(request, timeout=10) as response:
            data = json.loads(response.read(2_000_001))
        if data.get('error') is not None or data.get('id') != 'monitor':
            raise ValueError('RPC response error')
        return data['result']

SENSORS = {
    'blocks': ('Block Height', None), 'headers': ('Header Height', None),
    'verification_progress': ('Verification Progress', '%'), 'peers': ('Connected Peers', None),
    'inbound': ('Inbound Peers', None), 'outbound': ('Outbound Peers', None),
    'disk_gib': ('Blockchain Data Size', 'GiB'), 'prune_height': ('Prune Height', None),
    'chain': ('Chain', None), 'version': ('Bitcoin Core Version', None),
    'uptime_seconds': ('Node Uptime', 's'), 'bytes_received_gib': ('Network Received', 'GiB'),
    'bytes_sent_gib': ('Network Sent', 'GiB'), 'sync_stalled_minutes': ('Observed Sync Stall Duration', 'min'),
}
BINARY = {'initial_download':'Initial Block Download','pruned':'Pruning Enabled','synchronized':'Synchronized','no_peers':'No Peers','sync_stalled':'Observed Sync Stall'}

def snapshot(rpc, previous, now, stall_minutes):
    c, n, t, uptime = (rpc.call(m) for m in ('getblockchaininfo','getnetworkinfo','getnettotals','uptime'))
    blocks, headers = int(c['blocks']), int(c['headers'])
    ibd = bool(c['initialblockdownload'])
    last = previous.get('last', now)
    if previous.get('blocks') != blocks or previous.get('chain') != c['chain'] or not ibd or now < last:
        last = now
    duration = (now-last)/60 if ibd else 0
    peers = int(n['connections'])
    state = dict(blocks=blocks, headers=headers, verification_progress=round(float(c['verificationprogress'])*100,4), peers=peers, inbound=int(n['connections_in']), outbound=int(n['connections_out']), disk_gib=round(int(c['size_on_disk'])/2**30,3), prune_height=c.get('pruneheight'), chain=c['chain'], version=n['subversion'], uptime_seconds=int(uptime), bytes_received_gib=round(int(t['totalbytesrecv'])/2**30,4), bytes_sent_gib=round(int(t['totalbytessent'])/2**30,4), initial_download=ibd, pruned=bool(c['pruned']), synchronized=not ibd and blocks>0 and 0<=headers-blocks<=1, no_peers=peers==0, sync_stalled_minutes=round(duration,1), sync_stalled=ibd and duration>=stall_minutes)
    return state, dict(blocks=blocks, chain=c['chain'], last=last)

def configs(node, prefix, expiry):
    base = 'bitcoin_node_monitor/'+node
    device = {'identifiers':['bitcoin_node_monitor_'+node], 'name':'Bitcoin Node Monitor '+node, 'manufacturer':'Community','model':'Bitcoin Core'}
    for kind, fields in [('sensor',SENSORS),('binary_sensor',BINARY)]:
        for key, spec in fields.items():
            name, unit = spec if kind=='sensor' else (spec,None)
            cfg = dict(name=name, unique_id='bitcoin_node_monitor_'+node+'_'+key, state_topic=base+'/state', availability_topic=base+'/availability', expire_after=expiry, device=device)
            cfg['value_template'] = '{{ value_json.'+key+' }}' if kind=='sensor' else "{{ 'ON' if value_json."+key+" else 'OFF' }}"
            if unit: cfg['unit_of_measurement']=unit
            if key=='uptime_seconds': cfg['device_class']='duration'
            if key in ('no_peers','sync_stalled'): cfg['device_class']='problem'
            yield f'{prefix}/{kind}/bitcoin_node_monitor_{node}/{key}/config', cfg

def send(client, topic, payload):
    info=client.publish(topic,payload,qos=1,retain=True)
    info.wait_for_publish(timeout=10)
    if not info.is_published(): raise RuntimeError('MQTT publication failed')

def main():
    import paho.mqtt.client as mqtt
    o=json.loads(Path('/data/options.json').read_text())
    node=o['node_id']; prefix=o['discovery_prefix'].strip('/'); interval=int(o['poll_interval'])
    if not re.fullmatch(r'[A-Za-z0-9_-]{1,48}',node) or not prefix or any(x in prefix for x in '+#\x00') or not 15<=interval<=3600: raise ValueError('Invalid node ID, prefix or interval')
    if not o['mqtt_tls'] and not o['allow_insecure_mqtt']: raise ValueError('Plain MQTT requires explicit opt-in')
    rpc=RPC(o); base='bitcoin_node_monitor/'+node; previous={}
    signal.signal(signal.SIGTERM,lambda *_:STOP.set()); signal.signal(signal.SIGINT,lambda *_:STOP.set())
    while not STOP.is_set():
        client=mqtt.Client(mqtt.CallbackAPIVersion.VERSION2,client_id='bnm_'+node)
        ready=threading.Event(); refresh=threading.Event(); refresh.set()
        def connected(c,u,f,rc,p):
            if rc==0:
                c.subscribe(prefix+'/status'); refresh.set(); ready.set()
            else: ready.clear()
        def disconnected(*args): ready.clear()
        def message(c,u,msg):
            if msg.payload==b'online': refresh.set()
        client.on_connect=connected; client.on_disconnect=disconnected; client.on_message=message
        client.will_set(base+'/availability','offline',qos=1,retain=True)
        if o['mqtt_username']: client.username_pw_set(o['mqtt_username'],o['mqtt_password'])
        if o['mqtt_tls']: client.tls_set()
        started=False
        try:
            client.connect(o['mqtt_host'],int(o['mqtt_port']),keepalive=30); client.loop_start(); started=True
            if not ready.wait(15): raise RuntimeError('MQTT connection unavailable')
            send(client,base+'/availability','offline')
            while not STOP.is_set() and ready.is_set():
                if refresh.is_set():
                    refresh.clear()
                    for topic,cfg in configs(node,prefix,max(180,interval*3+60)): send(client,topic,json.dumps(cfg))
                try:
                    state, previous=snapshot(rpc,previous,time.monotonic(),int(o['stall_minutes']))
                    payload=json.dumps(state,allow_nan=False)
                except Exception as exc:
                    previous={}; send(client,base+'/availability','offline'); print('RPC unavailable: '+type(exc).__name__,flush=True)
                else:
                    send(client,base+'/state',payload); send(client,base+'/availability','online')
                STOP.wait(interval)
        except Exception as exc:
            print('Monitoring transport unavailable: '+type(exc).__name__,flush=True)
        finally:
            if started:
                if ready.is_set():
                    try: send(client,base+'/availability','offline')
                    except Exception: pass
                client.disconnect(); client.loop_stop()
        STOP.wait(5)

if __name__=='__main__':
    try: main()
    except Exception as exc:
        print('Configuration/startup failed: '+type(exc).__name__,flush=True)
        raise SystemExit(1)
