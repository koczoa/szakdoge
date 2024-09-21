package model;

import common.*;
import common.map_generation.MapGeneratorStrategy;
import common.map_generation.SimplexMapGeneratorStrategy;
import communicator.Communicator;
import logger.Log;

import java.io.IOException;
import java.util.ArrayList;
import java.util.HashMap;
import java.util.List;
import java.util.Map;

public class MainModel {
	//measured in fields
	private final int mapSize;
	private final Map<String, Team> teams;
	private final Map<Position, Field> fields;
	private final ArrayList<ControlPoint> controlPoints;
	private final List<MainModelListener> listeners;
	private static final String WHITE = "white";
	private static final String RED = "red";
	private MainModelCommunicatorListener mmcl;

	private MainModel(int size, MapGeneratorStrategy mapGeneratorStrategy) {
		mapSize = size;
		controlPoints = new ArrayList<>();
		teams = new HashMap<>();
		//TODO: refactor!!!
		Team whiteTeam = new Team(WHITE, "sarlMove", 5000, this);
		Team redTeam = new Team(RED, "dummy", 5000, this);
		teams.put(WHITE, whiteTeam);
		teams.put(RED, redTeam);
		listeners = new ArrayList<>();
		fields = mapGeneratorStrategy.generateMap(size);
	}

	public MainModel(int size) {
		this(size, new SimplexMapGeneratorStrategy());
	}

	public void placeDefaultUnits() {
		//TODO: rework this
//		new Unit(fields.get(new Position(38, 20)), teams.get(WHITE), Unit.Type.SCOUT);
		new Unit(fields.get(new Position(0, 0)), teams.get(RED), Unit.Type.SCOUT);
//		new Unit(fields.get(new Position(40, 40)), teams.get(RED), Unit.Type.SCOUT);
		new Unit(fields.get(new Position(5, 5)), teams.get(RED), Unit.Type.TANK);
		new Unit(fields.get(new Position(7, 3)), teams.get(WHITE), Unit.Type.TANK);
//		new Unit(fields.get(new Position(38, 25)), teams.get(RED), Unit.Type.TANK);
//		new Unit(fields.get(new Position(37, 20)), teams.get(WHITE), Unit.Type.TANK);
//		new Unit(fields.get(new Position(38, 21)), teams.get(WHITE), Unit.Type.TANK);
//		new Unit(fields.get(new Position(38, 22)), teams.get(WHITE), Unit.Type.INFANTRY);
	}

	public void placeDefaultControlPoints() {
		//TODO: rework this
		controlPoints.add(new ControlPoint(new Position(40, 50), 10, 3, this));
//		controlPoints.add(new ControlPoint(new Position(1, 5), 10, 2, this));
	}

	public void addListener(MainModelListener mml) {
		this.listeners.add(mml);

		for (var t : teams.values()) {
			for (var u : t.units().values()) {
				mml.unitCreated(u);
			}
		}
		for (var cp : controlPoints) {
			mml.controlPointCreated(cp);
		}
		for (var f : fields.values()) {
			mml.fieldCreated(f);
		}
		for (var t : teams.values()) {
			mml.teamCreated(t);
		}
	}

	public void addListener(MainModelCommunicatorListener mmcl) {
		this.mmcl = mmcl;
	}

	public void removeListener(MainModelListener mml) {
		this.listeners.remove(mml);

	}

	public Team team(String name) {
		return teams.get(name);
	}


	public List<Unit> requestUnits(Position pos, float size) {
		var view = new ArrayList<Unit>();
		for (var t : teams.values()) {
			view.addAll(t.requestUnits(pos, size));
		}
		return view;
	}

	public List<PerceivedUnit> requestPerceivedUnits(Position pos, float size) {
		var view = new ArrayList<PerceivedUnit>();
		for (var t : teams.values()) {
			view.addAll(t.requestPerceivedUnits(pos, size));
		}
		return view;
	}

	public List<ControlPoint> requestControlPoints(Position pos, float size) {
		var view = new ArrayList<ControlPoint>();
		for (var cp : controlPoints) {
			if (pos.inDistance(cp.pos(), size)) {
				view.add(cp);
			}
		}
		return view;
	}

	public List<Field> requestFileds(Position pos, float size) {
		var view = new ArrayList<Field>();
		fields.forEach((p, f) -> {
			if (pos.inDistance(p, size) && pos.hashCode() != p.hashCode()) {
				view.add(f);
			}
		});
		return view;
	}

	public void controlPointsUpdate() {
		for (var cp : controlPoints) {
			cp.updateNearbyUnits();
		}
	}

	public void teamLost(String name) {

	}

	public Field getField(Position pos) {
		return fields.get(pos);
	}

	public int width() {
		return mapSize;
	}

	public List<Team> getTeams() {
		return new ArrayList<>(teams.values());
	}
}
