package communicator;

import logger.Label;
import logger.Log;
import model.Position;
import model.Team;
import org.json.JSONObject;

import java.io.*;
import java.nio.ByteBuffer;
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
		Log.d(javaLogLabel, "buffcap: " + buffer.capacity() + "buff: " + buffer);
		sizeBuffer.putInt(buffer.limit());
		sizeBuffer.position(0);

		socketChannel.write(sizeBuffer);
		socketChannel.write(buffer);
		buffer.position(0);
		sizeBuffer.position(0);

	}

	public void communicate() throws IOException {
		team.refillActionPoints();
		team.updateUnits();
		runCounter++;
		Log.d(javaLogLabel, "RUN:" + runCounter);
		Log.d(javaLogLabel, "communicating");
		var message = new JSONObject();
		var messagePayload = team.teamMembersToJson();

		if (!simuEnded) {
			message.put("phase", "commPhase");
			message.put("teamSize", team.units().size());
			message.put("payload", messagePayload);
		} else {
			message.put("phase", "endPhase");
			message.put("result", weWon);
			simuEnded = false;
		}

		ByteBuffer sizeBuffer = ByteBuffer.allocate(4);
		ByteBuffer buffer = StandardCharsets.UTF_8.encode(String.valueOf(message));
		System.out.println("buffcap: " + buffer.capacity() + "buff: " + buffer);
		sizeBuffer.putInt(buffer.limit());
		sizeBuffer.position(0);

		socketChannel.write(sizeBuffer);
		socketChannel.write(buffer);
		buffer.position(0);
		sizeBuffer.position(0);
		Log.d(javaLogLabel, "END communicating");
	}

	private void unitMove(String[] split) {
		if (split.length == 4) {
			team.moveUnit(Integer.parseInt(split[1]),
					new Position(Integer.parseInt(split[2]), Integer.parseInt(split[3])));
		}
	}

	private void unitShoot(String[] split) {
		if (split.length == 4) {
			team.fireUnit(Integer.parseInt(split[1]),
					new Position(Integer.parseInt(split[2]), Integer.parseInt(split[3])));
		}
	}

	public void endSimu(boolean win) {
		simuEnded = true;
		weWon = win;
	}

	public Team getTeam() {
		return team;
	}
}
