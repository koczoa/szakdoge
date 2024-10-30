package communicator;

import model.MainModel;

import java.io.IOException;
import java.net.InetSocketAddress;
import java.nio.channels.ServerSocketChannel;
import java.util.ArrayList;
import java.util.List;

public class MainCommunicator {
	ServerSocketChannel server;
	InetSocketAddress address;
	private final List<Communicator> communicators;
	private static final String WHITE = "white";
	private static final String RED = "red";
	private final MainModel mm;
	private int activeIdx;

    public MainCommunicator(MainModel mm) throws IOException {
		this.mm = mm;
		server = ServerSocketChannel.open();
		address = new InetSocketAddress("localhost", 6969);
		server.bind(address);
		server.configureBlocking(false);
		communicators = new ArrayList<>();
		this.activeIdx = 0;
	}

	public boolean tick(int pollTimeOut) throws IOException {
		var client = server.accept();
		if (client != null) {
			client.configureBlocking(false);
			switch (communicators.size()) {
				case 0 -> communicators.add(new Communicator(mm.team(WHITE), client,  mm.team(WHITE).getStrategy()));
				case 1 -> {
					communicators.add(new Communicator(mm.team(RED), client, mm.team(RED).getStrategy()));
					communicators.get(activeIdx).yourTurn();
				}
                default -> client.close();
			}
		}
		mm.controlPointsUpdate();
		if (communicators.size() == 2) {
			try {
				if(communicators.get(activeIdx).tick()) {
					activeIdx = 1 - activeIdx;
					if (mm.getWinnerTeam() != null) {
						for (var comm : communicators) {
							comm.end(mm.getWinnerTeam().getName());
							comm.close();
						}
						communicators.clear();
						return false;
					} else {
						communicators.get(activeIdx).yourTurn();
					}
				}
			} catch (IOException e) {
				communicators.get(activeIdx).close();
				return false;
			}
        }
		try {
			Thread.sleep(pollTimeOut);
		} catch (InterruptedException e) {
			throw new RuntimeException(e);
		}
		return true;
	}
}