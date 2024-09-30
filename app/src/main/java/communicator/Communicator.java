package communicator;

import logger.Label;
import logger.Log;
import model.Position;
import model.Team;
import org.json.JSONObject;

import java.io.*;
import java.nio.ByteBuffer;
import java.nio.ByteOrder;
import java.nio.channels.SocketChannel;
import java.nio.charset.StandardCharsets;
import java.nio.file.Files;
import java.nio.file.Paths;


public class Communicator {
	private final SocketChannel socketChannel;
	private final Team team;

    private final Label javaLogLabel;
	private int runCounter = 0;
	private boolean simuEnded = false;
	private boolean weWon = false;

	public Communicator(Team team, SocketChannel sc,  String strategy) throws IOException {
		this.socketChannel = sc;
		this.team = team;
		javaLogLabel = new Label(team.getName() + " java", Label.Color.BLACK,
				team.getName().equals("red") ? Label.Color.RED : Label.Color.WHITE);
		var setupMessagePayLoad = new JSONObject();

		setupMessagePayLoad.put("teamName", team.getName());
		setupMessagePayLoad.put("strategy", strategy);
		setupMessagePayLoad.put("mapSize", team.getMainModel().width());

		var setupMessage = new JSONObject();
		setupMessage.put("type", "setupMessage");
		setupMessage.put("payload", setupMessagePayLoad);

		ByteBuffer sizeBuffer = ByteBuffer.allocate(4);
		ByteBuffer buffer = StandardCharsets.UTF_8.encode(setupMessage.toString());
		sizeBuffer.putInt(buffer.limit());
		sizeBuffer.position(0);
//		ByteBuffer buffer = ByteBuffer.allocate(sizeBuffer.limit());
//		buffer.put
		socketChannel.write(sizeBuffer);
		socketChannel.write(buffer);
		buffer.position(0);
		sizeBuffer.position(0);
		Log.d(javaLogLabel, "buffcap: " + buffer.capacity() + " bufflim: " + buffer.limit());
	}

	public void communicate() throws IOException {
		team.refillActionPoints();
		team.updateUnits();
		runCounter++;
		Log.d(javaLogLabel, "RUN:" + runCounter);
		Log.d(javaLogLabel, "communicating");
		var message = new JSONObject();
		var payload = new JSONObject();
		var mapDescriptors = team.toMerge();
		var unitsPayload = team.teamMembersToJson();
		payload.put("units", unitsPayload);
		payload.put("map", mapDescriptors);

		if (!simuEnded) {
			message.put("type", "commMessage");
			message.put("payload", payload);
		} else {
			message.put("type", "endMessage");
			message.put("payload", weWon);
			simuEnded = false;
		}

		ByteBuffer sizeBuffer = ByteBuffer.allocate(4);
		ByteBuffer buffer = StandardCharsets.UTF_8.encode(String.valueOf(message));
//		Log.d(javaLogLabel, "output: " + message);
		sizeBuffer.putInt(buffer.limit());
		sizeBuffer.position(0);

		socketChannel.write(sizeBuffer);
		socketChannel.write(buffer);
		buffer.position(0);
		sizeBuffer.position(0);

		//TODO: here comes the read-in part
		Log.d(javaLogLabel, "END communicating");
	}

	public void close() {
        try {
            socketChannel.close();
        } catch (IOException e) {}
    }

	public Team getTeam() {
		return team;
	}
}
