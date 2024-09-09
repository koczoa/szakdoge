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

    public MainCommunicator(MainModel mm) throws IOException {
		this.mm = mm;
		server = ServerSocketChannel.open();
		address = new InetSocketAddress("localhost", 6969);
		server.bind(address);
		server.configureBlocking(false);
		communictors = new ArrayList<>();
		communicationLogLabel = new Label("Communication", Label.Color.NONE, Label.Color.NONE);

	}


	public void tick() throws IOException {
		var client = server.accept();
		if (client != null) {
			client.configureBlocking(false);
			switch (communictors.size()) {
				case 0:
					communictors.add(new Communicator(mm.team(WHITE), client,  "dummy"));
					break;
				case 1:
					communictors.add(new Communicator(mm.team(RED), client,  "dummy"));
					break;
				default:
					client.close();
			}
		}
		for (var comm : communictors) {
			comm.communicate();
		}
	}

	@Override
	public void teamLost(String name) {

	}
}