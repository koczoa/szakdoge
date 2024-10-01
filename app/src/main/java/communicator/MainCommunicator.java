package communicator;

import model.MainModel;
import common.MainModelCommunicatorListener;
import logger.Label;

import java.io.IOException;
import java.net.InetSocketAddress;
import java.nio.channels.ServerSocketChannel;
import java.nio.channels.SocketChannel;
import java.util.ArrayList;
import java.util.List;

public class MainCommunicator implements MainModelCommunicatorListener {
	ServerSocketChannel server;
	InetSocketAddress address;
	private final List<Communicator> communictors;
	private final Label communicationLogLabel;
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
		communictors = new ArrayList<>();
		communicationLogLabel = new Label("Communication", Label.Color.NONE, Label.Color.NONE);
		this.activeIdx = 0;
	}

	public boolean tick() throws IOException {
		var client = server.accept();
		if (client != null) {
			client.configureBlocking(false);
			switch (communictors.size()) {
				case 0 -> communictors.add(new Communicator(mm.team(WHITE), client,  "dummy"));
				case 1 -> {
					communictors.add(new Communicator(mm.team(RED), client, "dummy"));
					communictors.get(activeIdx).yourTurn();
				}
                default -> client.close();
			}
		}
		if (communictors.size() == 2) {
			try {
				if(communictors.get(activeIdx).tick()) {
					activeIdx = 1 - activeIdx;
					communictors.get(activeIdx).yourTurn();
				}
			} catch (IOException e) {
				communictors.get(activeIdx).close();
				return false;
			}
        }
		try {
			Thread.sleep(500);
		} catch (InterruptedException e) {
			throw new RuntimeException(e);
		}
		return true;
	}

	@Override
	public void teamLost(String name) {

	}
}