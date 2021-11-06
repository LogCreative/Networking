# 3. Write an RYU controller that uses both paths to forward packets from h1 to h2.

from ryu.base import app_manager
from ryu.controller import ofp_event
from ryu.controller.handler import CONFIG_DISPATCHER, MAIN_DISPATCHER, set_ev_cls
from ryu.lib import packet
from ryu.lib.packet import ether_types, ethernet
from ryu.lib.packet import in_proto as inet
from ryu.ofproto import ofproto_v1_3

class PeriodicSwtich(app_manager.RyuApp):
    OFP_VERSIONS = [ofproto_v1_3.OFP_VERSION]

    def __init__(self, *_args, **_kwargs):
        super(PeriodicSwtich, self).__init__(*_args, **_kwargs)
    
    @set_ev_cls(ofp_event.EventOFPSwitchFeatures, CONFIG_DISPATCHER)
    def switch_features_handler(self, ev):
        datapath = ev.msg.datapath
        ofproto = datapath.ofproto
        parser = datapath.ofproto_parser

        if datapath.id == 1 or datapath.id == 2:
            # s1 / s2
            # bucket group
            actions1 = [parser.OFPActionOutput(1)]
            actions2 = [parser.OFPActionOutput(2)]
            buckets = [
            parser.OFPBucket(watch_port=1, actions=actions1),
            parser.OFPBucket(watch_port=2, actions=actions2)]
            
            group_id = 2
            self.req_group(datapath, group_id, buckets)

            match = parser.OFPMatch(in_port=3)
            self.add_flow_group(datapath, 10, match, group_id)

            # return flow s1(s2) -> h1
            # 2 possible flows: from port 1, from port 2.
            match = parser.OFPMatch(in_port=1)
            actions = [parser.OFPActionOutput(3)]
            self.add_flow(datapath, 10, match, actions)
            match = parser.OFPMatch(in_port=2)
            actions = [parser.OFPActionOutput(3)]
            self.add_flow(datapath, 10, match, actions)
        elif datapath.id == 3 or datapath.id == 4:
            # s3 / s4

            actions1 = [parser.OFPActionOutput(1)]
            actions2 = [parser.OFPActionOutput(2)]

            # fail over for port 1
            buckets1 = [
                parser.OFPBucket(watch_port=2, actions=actions2),
                parser.OFPBucket(watch_port=1, actions=actions1)]
            group_id = 3
            self.req_group(datapath, group_id, buckets1)
            match = parser.OFPMatch(in_port=1)
            self.add_flow_group(datapath, 10, match, group_id)

            # fail over for port 2
            buckets2 = [
                parser.OFPBucket(watch_port=1, actions=actions1),
                parser.OFPBucket(watch_port=2, actions=actions2)]
            group_id = 4
            self.req_group(datapath, group_id, buckets2)
            match = parser.OFPMatch(in_port=2)
            self.add_flow_group(datapath, 10, match, group_id)

    def add_flow(self, datapath, priority, match, actions, buffer_id=None):
        ofproto = datapath.ofproto
        parser = datapath.ofproto_parser

        inst = [parser.OFPInstructionActions(ofproto.OFPIT_APPLY_ACTIONS,
                                             actions)]
        if buffer_id:
            mod = parser.OFPFlowMod(datapath=datapath, buffer_id=buffer_id,
                                    priority=priority, match=match,
                                    instructions=inst)
        else:
            mod = parser.OFPFlowMod(datapath=datapath, priority=priority,
                                    match=match, instructions=inst)
        datapath.send_msg(mod)
    
    def req_group(self, datapath, group_id, buckets):
        ofproto = datapath.ofproto
        parser = datapath.ofproto_parser

        req = parser.OFPGroupMod(datapath, ofproto.OFPGC_ADD, ofproto.OFPGT_FF, group_id, buckets)
        datapath.send_msg(req)

    def add_flow_group(self, datapath, priority, match, group_id):
        ofproto = datapath.ofproto
        parser = datapath.ofproto_parser
        
        actions = [parser.OFPActionGroup(group_id=group_id)]
        inst = [parser.OFPInstructionActions(ofproto.OFPIT_APPLY_ACTIONS, actions)]
        mod = parser.OFPFlowMod(datapath=datapath, priority=priority, match=match, instructions=inst)
        datapath.send_msg(mod)

    @set_ev_cls(ofp_event.EventOFPPortStatus, MAIN_DISPATCHER)
    def port_status_handler(self, ev):
        msg = ev.msg
        dp = msg.datapath
        ofp = dp.ofproto

        if msg.reason == ofp.OFPPR_ADD:
            reason = 'ADD'
        elif msg.reason == ofp.OFPPR_DELETE:
            reason = 'DELETE'
        elif msg.reason == ofp.OFPPR_MODIFY:
            reason = 'MODIFY'
        else:
            reason = 'unknown'

        self.logger.debug('OFPPortStatus received: reason=%s desc=%s',
                            reason, msg.desc)