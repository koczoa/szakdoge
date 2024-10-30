package model;

import org.json.JSONObject;

public final class PerceivedUnit {
	private final Position pos;
	private final String team;
	private final String type;
	private final int id;
	private final int health;

	public PerceivedUnit(Position p, String t, String type, int id, int hp) {
		pos = p;
		team = t;
		this.type = type;
		this.id = id;
		this.health = hp;
	}

	@Override
	public String toString() {
		return pos + " " + team + " " + type + " " + id + " " + health;
	}

	public JSONObject toJSON() {
		return new JSONObject().put("pos", this.pos.toJSON()).put("team", team).put("type", type).put("id", id).put("health", health);
	}

	@Override
	public int hashCode() {
		return this.id;
	}

	@Override
	public boolean equals(Object o) {
		if (this == o) return true;
		if (o == null || getClass() != o.getClass()) return false;
		PerceivedUnit that = (PerceivedUnit) o;
		return id == that.id;
	}
}
