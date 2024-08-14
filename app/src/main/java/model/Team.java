package model;

import util.Color;

import java.util.ArrayList;
import java.util.HashMap;
import java.util.List;
import java.util.Map;
import java.util.Random;

public final class Team {
	private final Color color;
	private final String name;
	private final String strategy;
	private final HashMap<Integer, Unit> units;
	private final HashMap<Integer, Unit> deadUnits;
	private final int budget;
	private final MainModel mm;
	Random rand = new Random();

	public Team(String name, String strategy, int budget, MainModel mm) {
		units = new HashMap<>();
		deadUnits = new HashMap<>();
		if (name.equals("white")) {
			this.color = Color.WHITE;
		} else if (name.equals("red")) {
			this.color = Color.RED;
		} else {
			this.color = Color.DEFAULT;
		}
		this.name = name;
		this.budget = budget;
		this.mm = mm;
		this.strategy = strategy;
	}

	public Color getColor() {
		return color;
	}

	public String getName() {
		return name;
	}

	public String getStrategy() {
		return strategy;
	}

	public void addUnit(Unit u) {
		int currentBalance = 0;
		for (java.util.Map.Entry<Integer, Unit> entry : units.entrySet()) {
			currentBalance += entry.getValue().price();
		}
		if (currentBalance + u.price() <= budget) {
			this.units.put(u.getUUID(), u);
		}
	}

	public Map<Integer, Unit> units() {
		return this.units;
	}

	public List<Unit> requestUnits(Position pos, float size) {
		var view = new ArrayList<Unit>();
		units.forEach((id, u) -> {
			if (pos.inDistance(u.pos(), size) && u.pos() != pos) {
				view.add(u);
			}
		});
		return view;
	}

	public List<PerceivedUnit> requestPerceivedUnits(Position pos, float size) {
		var view = new ArrayList<PerceivedUnit>();
		units.forEach((id, u) -> {
			if (pos.inDistance(u.pos(), size) && u.pos() != pos) {
				view.add(u.getPerception());
			}
		});
		return view;
	}

	public void moveUnit(int id, Position newPos) {
		var newField = mm.getField(newPos);
		var u = units.get(id);
		if (newField == null || u == null) {
			return;
		}
		u.move(newField);
	}

	public void fireUnit(int id, Position newPos) {
		double spreadChance = rand.nextDouble();
		if (spreadChance > 0.75) {
			newPos = new Position(newPos.x() + 2 * rand.nextInt(2) - 1, newPos.y() + 2 * rand.nextInt(2) - 1);
		}
		var newField = mm.getField(newPos);
		var u = units.get(id);
		if (newField == null || u == null) {
			return;
		}
		u.shoot(newField);
	}

	public void updateUnits() {
		units.forEach((id, u) -> u.updateWorld(mm));
	}

	public void refillActionPoints() {
		units.forEach((id, u) -> u.refillActionPoints());
	}


	public void unitDied(int id) {
		var deadUnit = units.remove(id);
		deadUnits.put(id, deadUnit);
		if (units.isEmpty()) {
			mm.teamLost(name);
		}
	}

	public List<String> teamMembersToString(boolean toMonitor) {
		var res = new ArrayList<String>();
		units.forEach((id, u) -> res.add(u.toString(toMonitor)));
		return res;
	}

	public void reset() {
		units.putAll(deadUnits);
		deadUnits.clear();
		units.forEach((id, u) -> u.reset(mm.getField(u.getStartingPos())));
	}

	public MainModel getMainModel() {
		return mm;
	}
}
