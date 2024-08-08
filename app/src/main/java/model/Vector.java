package model;

/**
 * Class to represent the in-simulation coordinates of Units, Fields, ControlPoints
 */
public final class Vector {
	private final int x;
	private final int y;

	public Vector(int x, int y) {
		this.x = x;
		this.y = y;
	}

	public Vector(Vector v) {
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

	@Override
	public int hashCode() {
		return Integer.hashCode(Integer.hashCode(x*100) + y);
	}

	@Override
	public boolean equals(Object obj) {
		if(obj instanceof Vector v) {
			return this.x == v.x && this.y == v.y;
		}
		return false;
	}

	//TODO: function to return the coords to coords that are representable on the screen
	//TODO: https://github.com/koczoa/szakdoge/issues/1
}