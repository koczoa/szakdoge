package communicator;

import logger.Label;
import logger.Log;
import model.Position;
import model.Team;
import org.json.JSONObject;
import util.Wrapper;

import java.io.*;
import java.nio.channels.SocketChannel;


public class Communicator {
	private final Team team;
	private final Wrapper w;

    private final Label javaLogLabel;
	private int runCounter = 0;
	private State state;

	public enum State {
		WAIT,
		READ
	}

	public Communicator(Team team, SocketChannel sc,  String strategy) throws IOException {
		this.w = new Wrapper(sc);
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
		w.write(setupMessage, javaLogLabel);
		this.state = State.WAIT;
//		Log.d(javaLogLabel, "output: " + setupMessage);
	}

	public boolean doStuff() throws IOException {
		var readMessage = w.read();
		if(readMessage == null) {
			return false;
		}
		for (var command : readMessage) {
			var obj = (JSONObject) command;
			switch (obj.getString("action")) {
				case "shoot": {
					var target = obj.getJSONObject("target");
					team.fireUnit(
						obj.getInt("id"),
						new Position(target.getInt("x"), target.getInt("y"))
					);
				} break;
				case "move": {
					var target = obj.getJSONObject("target");
					team.moveUnit(
						obj.getInt("id"),
						new Position(target.getInt("x"), target.getInt("y"))
					);
				} break;
			}
		}
		Log.d(javaLogLabel, "END communicating");
		this.state = State.WAIT;
		return true;
	}

	public void yourTurn() throws IOException {
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
		message.put("type", "commMessage");
		message.put("payload", payload);
		w.write(message, javaLogLabel);
		this.state = State.READ;
	}

	public void end(String winnerName) throws IOException {
		var message = new JSONObject();
		message.put("type", "endMessage");
		message.put("payload", winnerName.equals(this.team.getName()));
		w.write(message, javaLogLabel);
	}

	public boolean tick() throws IOException {
        return this.state == State.READ && doStuff();
    }

	public void close() {
        w.close();
    }

	public Team getTeam() {
		return team;
	}
}
