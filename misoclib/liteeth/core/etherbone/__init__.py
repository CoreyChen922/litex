from misoclib.liteeth.common import *
from misoclib.liteeth.generic import *
from misoclib.liteeth.generic.arbiter import Arbiter
from misoclib.liteeth.generic.dispatcher import Dispatcher
from misoclib.liteeth.core.etherbone.packet import *
from misoclib.liteeth.core.etherbone.probe import *
from misoclib.liteeth.core.etherbone.record import *
from misoclib.liteeth.core.etherbone.wishbone import *

class LiteEthEtherbone(Module):
	def __init__(self, udp, udp_port):
		# decode/encode etherbone packets
		self.submodules.packet = packet = LiteEthEtherbonePacket(udp, udp_port)

		# packets can be probe (etherbone discovering) or records with
		# writes and reads
		self.submodules.probe = probe = LiteEthEtherboneProbe()
		self.submodules.record = record = LiteEthEtherboneRecord()

		# arbitrate/dispatch probe/records packets
		dispatcher = Dispatcher(packet.source, [probe.sink, record.sink])
		self.comb += dispatcher.sel.eq(~packet.source.pf)
		arbiter = Arbiter([probe.source, record.source], packet.sink)
		self.submodules += dispatcher, arbiter

		# create mmap ŵishbone master
		self.submodules.master = master = LiteEthEtherboneWishboneMaster()
		self.comb += [
			Record.connect(record.receiver.source, master.sink),
			Record.connect(master.source, record.sender.sink)
		]
