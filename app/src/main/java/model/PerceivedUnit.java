package model;

public final class PerceivedUnit {
	private final String pos;
	private final String team;
	private final String type;
	private final int id;
	private final int health;

	public PerceivedUnit(String p, String t, String type, int id, int hp) {
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
}
