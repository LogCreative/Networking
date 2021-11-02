# 2. Write an RYU controller that switches paths (h1-s1-s3-s2-h2 or h1-s1-s4-s2-h2) between h1 and h2 every 5 seconds. 

from ryu.base import app_manager
from ryu.controller import ofp_event
from ryu.controller.handler import CONFIG_DISPATCHER, MAIN_DISPATCHER, set_ev_cls
from ryu.lib import packet
from ryu.lib.packet import ether_types, ethernet
from ryu.lib.packet import in_proto as inet
from ryu.ofproto import ofproto_v1_3

pathport = 1
pathstate = 1
# 0 -> 1 -> 0 (change)

class PeriodicSwtich(app_manager.RyuApp):
    OFP_VERSIONS = [ofproto_v1_3.OFP_VERSION]

    def __init__(self, *_args, **_kwargs):
        super(PeriodicSwtich, self).__init__(*_args, **_kwargs)
    
    @set_ev_cls(ofp_event.EventOFPSwitchFeatures, CONFIG_DISPATCHER)
    def switch_features_handler(self, ev):
        datapath = ev.msg.datapath
        ofproto = datapath.ofproto
        parser = datapath.ofproto_parser
        out_port = 1
        
        match = parser.OFPMatch(in_port=1, eth_type=ether_types.ETH_TYPE_IP,ipv4_src='10.0.0.1', ipv4_dst='10.0.0.2',ip_proto=inet.IPPROTO_UDP, udp_dst=5555)
        actions = [parser.OFPActionOutput(out_port)]
        self.add_flow(datapath, 0, match, actions)

    def add_flow(self, datapath, priority, match, actions, buffer_id=None):
        """
        Default adding flow.
        """
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

    def add_flow_timeout(self, datapath, priority, match, actions, buffer_id=None):
        """
        Add a flow that timeout in 5 sec.
        """
        ofproto = datapath.ofproto
        parser = datapath.ofproto_parser

        inst = [parser.OFPInstructionActions(ofproto.OFPIT_APPLY_ACTIONS,
                                             actions)]
        if buffer_id:
            mod = parser.OFPFlowMod(datapath=datapath, buffer_id=buffer_id,
                                    priority=priority, match=match,
                                    instructions=inst, hard_timeout=5, flags=ofproto.OFPFF_SEND_FLOW_REM)
        else:
            mod = parser.OFPFlowMod(datapath=datapath, priority=priority,
                                    match=match, instructions=inst, hard_timeout=5, flags=ofproto.OFPFF_SEND_FLOW_REM)
        datapath.send_msg(mod)

    @set_ev_cls(ofp_event.EventOFPSwitchFeatures, CONFIG_DISPATCHER)
    def switch_features_handler(self, ev):
        global pathport

        datapath = ev.msg.datapath
        ofproto = datapath.ofproto
        parser = datapath.ofproto_parser
        
        # Since the switches are added in order,
        # The id is appended in order as well.
        print('CONFIG switch id: '+ str(datapath.id))

        if datapath.id == 1 or datapath.id == 2:
            # forward flow h1 -> s1(s2)
            # input from port 3, output to the selected port.
            match = parser.OFPMatch(in_port=3)
            actions = [parser.OFPActionOutput(pathport)] #
            self.add_flow_timeout(datapath, 2, match, actions)

            # return flow s1(s2) -> h1
            # 2 possible flows: from port 1, from port 2.
            match = parser.OFPMatch(in_port=1)
            actions = [parser.OFPActionOutput(3)]
            self.add_flow(datapath, 2, match, actions)
            match = parser.OFPMatch(in_port=2)
            actions = [parser.OFPActionOutput(3)]
            self.add_flow(datapath, 2, match, actions)
        elif datapath.id == 3 or datapath.id == 4:
            # s3 / s4
            match = parser.OFPMatch(in_port=1)
            actions = [parser.OFPActionOutput(2)]
            self.add_flow(datapath, 2, match, actions)
            match = parser.OFPMatch(in_port=2)
            actions = [parser.OFPActionOutput(1)]
            self.add_flow(datapath, 2, match, actions)

    @set_ev_cls(ofp_event.EventOFPFlowRemoved, MAIN_DISPATCHER)
    def flow_removed_handler(self, ev):
        global pathport, pathstate
        
        msg = ev.msg
        datapath = msg.datapath
        ofproto = datapath.ofproto
        parser = datapath.ofproto_parser

        if msg.reason == ofproto.OFPRR_HARD_TIMEOUT:
            pathstate += 1
            if pathstate == 2: 
                pathstate = 0
                pathport = 2 if pathport==1 else 1
                # change on pathport could only be invoked once in one round.
                print('Swtich to port: ' + str(pathport))
            print('OFPFlowRemoved received: ' + str(datapath.id))
            match = parser.OFPMatch(in_port=3)
            actions = [parser.OFPActionOutput(pathport)]
            self.add_flow_timeout(datapath, 2, match, actions)
