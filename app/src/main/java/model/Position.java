package model;

import org.json.JSONArray;
import org.json.JSONObject;
import util.Tuplet;

/**
 * Class to represent the in-simulation coordinates of Units, Fields, ControlPoints
 */
public final class Position {
	private final int x;
	private final int y;

	public Position(int x, int y) {
		this.x = x;
		this.y = y;
	}

	public Position(Position v) {
		this.x = v.x;
		this.y = v.y;
	}

	public int x() {
		return this.x;
	}

	public int y() {
		return this.y;
	}

	@Override
	public String toString() {
		return "x: " + x + " y: " + y;
	}

	public JSONObject toJSON() {
		JSONObject response = new JSONObject();
		response.put("x", x);
		response.put("y", y);
		return response;
	}

	@Override
	public int hashCode() {
		return Integer.hashCode(Integer.hashCode(x*100) + y);
	}

	@Override
	public boolean equals(Object obj) {
		if(obj instanceof Position v) {
			return this.x == v.x && this.y == v.y;
		}
		return false;
	}

	public Tuplet<Float, Float> screenCoords(float size, float udc) {
		return new Tuplet<>((udc * size + udc * x * size)-size*udc/2, (udc * size + udc * y * size)-size*udc/2);
	}

	public boolean inDistance(Position p, float rov) {
		return Math.pow(this.x - p.x(), 2) + Math.pow(this.y - p.y(), 2) <= Math.pow((rov + 0.5f), 2);
	}

	public boolean isNeighbouring(Position p) {
		return (Math.abs(this.x - p.x) <= 1 && Math.abs(this.y - p.y) <= 1);
	}
}