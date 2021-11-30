# 4. Write an RYU controller that uses the first path (h1-s1-s3-s2-h2) for routing packets from h1 to h2 and uses the second path for backup. Specifically, when the first path experiences a link failure, the network should automatically switch to the second path without causing packet drop. (hint: consider using \verb"OFPGT_FF" (FF is short for ``fast failover'') to construct a group table)

from ryu.base import app_manager
from ryu.controller import ofp_event
from ryu.controller.handler import CONFIG_DISPATCHER, MAIN_DISPATCHER, set_ev_cls
from ryu.lib import packet
from ryu.lib.packet import ether_types, ethernet
from ryu.lib.packet import in_proto as inet
from ryu.ofproto import ofproto_v1_3

from ryu.topology.api import get_switch, get_link
from ryu.topology import event, switches
from time import time

LEFT = 0
RIGHT = 1
UPPER = 2
BOTTOM = 3

class FFSwtich(app_manager.RyuApp):
    OFP_VERSIONS = [ofproto_v1_3.OFP_VERSION]

    def __init__(self, *_args, **_kwargs):
        super(FFSwtich, self).__init__(*_args, **_kwargs)
        self.lr = -1
        self.ub = -1
        self.prev_time = -1
        self.change_state = 0
    
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

            match_src = '10.0.0.1' if datapath.id == 1 else '10.0.0.2'
            match_dst = '10.0.0.2' if datapath.id == 1 else '10.0.0.1'
            match = parser.OFPMatch(in_port=1,eth_type=ether_types.ETH_TYPE_IP,ipv4_src=match_src,ipv4_dst=match_dst)
            self.add_flow(datapath,15,match,actions2)
            match = parser.OFPMatch(in_port=2, eth_type=ether_types.ETH_TYPE_IP,ipv4_src=match_src,ipv4_dst=match_dst)
            self.add_flow(datapath,15,match,actions1)

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
            actions3 = [parser.OFPActionOutput(3)]

            # fail over for port 1
            buckets1 = [
                parser.OFPBucket(watch_port=2, actions=actions2),
                parser.OFPBucket(watch_port=3, actions=actions3)]
            group_id = 3
            self.req_group(datapath, group_id, buckets1)
            match = parser.OFPMatch(in_port=1)
            self.add_flow_group(datapath, 10, match, group_id)

            # fail over for port 2
            buckets2 = [
                parser.OFPBucket(watch_port=1, actions=actions1),
                parser.OFPBucket(watch_port=3, actions=actions3)]
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
        datapath = msg.datapath
        ofproto = datapath.ofproto    
        if msg.reason == ofproto.OFPPR_MODIFY:
            if self.prev_time < 0 or time()-self.prev_time <= 1:
                # not recorded: at the build stage.
                # it is too close as the same op: don't make duplicated work.
                self.prev_time = time() # refresh time and move on.
                return
            # regard it as different op.
            # will not refresh the previous time 
            # as we need to locate the location of the broken link.
            if datapath.id == 1:
                # left
                self.lr = LEFT
            elif datapath.id == 2:
                # right
                self.lr = RIGHT
            elif datapath.id == 3:
                # upper link
                self.ub = UPPER
            elif datapath.id == 4:
                # bottom link
                self.ub = BOTTOM
            self.change_state = self.change_state + 1 if self.change_state < 3 else 0
            print(str(self.lr) + "," + str(self.ub) + "," + str(self.change_state))
            if self.change_state == 0:
                # make the change.
                # the information is efficient enough to make adjustment.
                switch_list = get_switch(self)
                if self.lr == LEFT:
                    # notify s2
                    target_switch = switch_list[1]
                else:
                    # notify s1
                    target_switch = switch_list[0]
                dp = target_switch.dp
                ofp = datapath.ofproto
                parser = dp.ofproto_parser
                if self.ub == UPPER:
                    # port3 -> port2
                    match = parser.OFPMatch(in_port=3)
                    actions = [parser.OFPActionOutput(2)]
                    self.add_flow(dp, 20, match, actions)
                else:
                    # port3 -> port1
                    match = parser.OFPMatch(in_port=3)
                    actions = [parser.OFPActionOutput(1)]
                    self.add_flow(dp, 20, match, actions)