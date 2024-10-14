package model;

import common.*;
import common.map_generation.MapGeneratorStrategy;
import common.map_generation.SimplexMapGeneratorStrategy;
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
		teams.put(WHITE, new Team(WHITE, "dummy", 5000, this));
		teams.put(RED, new Team(RED, "heuristic", 5000, this));
		listeners = new ArrayList<>();
		fields = mapGeneratorStrategy.generateMap(size);
	}

	public MainModel(int size) {
		this(size, new SimplexMapGeneratorStrategy());
	}

	public void placeDefaultUnits() {
		//TODO: rework this
		new Unit(fields.get(new Position(0, 0)), teams.get(WHITE), Unit.Type.TANK);
		new Unit(fields.get(new Position(3, 2)), teams.get(WHITE), Unit.Type.TANK);
		new Unit(fields.get(new Position(5, 5)), teams.get(WHITE), Unit.Type.TANK);
		new Unit(fields.get(new Position(3, 4)), teams.get(WHITE), Unit.Type.INFANTRY);
		new Unit(fields.get(new Position(4, 5)), teams.get(WHITE), Unit.Type.SCOUT);

		new Unit(fields.get(new Position(mapSize - 1, mapSize - 1)), teams.get(RED), Unit.Type.TANK);
		new Unit(fields.get(new Position(mapSize - 4, mapSize - 2)), teams.get(RED), Unit.Type.TANK);
		new Unit(fields.get(new Position(mapSize - 6, mapSize - 1)), teams.get(RED), Unit.Type.TANK);
		new Unit(fields.get(new Position(mapSize - 3 , mapSize - 2)), teams.get(RED), Unit.Type.INFANTRY);
		new Unit(fields.get(new Position(mapSize - 1, mapSize - 4)), teams.get(RED), Unit.Type.SCOUT);
	}

	public void placeDefaultControlPoints() {
		//TODO: rework this
		controlPoints.add(new ControlPoint(new Position(30, 30), 10, 4, this));
		controlPoints.add(new ControlPoint(new Position(40, 20), 20, 2, this));
		controlPoints.add(new ControlPoint(new Position(20, 40), 20, 2, this));

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
			if (pos.inDistance(p, size)) {
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
