package model;

import common.ControlPointListener;
import org.json.JSONObject;
import util.Color;

import java.util.*;

public class ControlPoint {
	private final Position pos;
	private final int size;
	private final int percentage;
	private ControlPointListener listener;
	private Team controlTeam;
	private Team prevControlTeam;
	private int controlLength;
	private final MainModel mm;
	private final int id;
	private static int idCounter = 0;

	public ControlPoint(Position p, int percentage, int size, MainModel mm) {
		pos = p;
		this.size = size;
		this.percentage = percentage;
		this.mm = mm;
		this.id = idCounter++;
	}

	private Map<Team, Integer> countUnits(List<Unit> seenUnits) {
		var unitCount = new HashMap<Team, Integer>();
		for (var u : seenUnits) {
			if (unitCount.containsKey(u.team())) {
				var val = unitCount.get(u.team());
				unitCount.put(u.team(), val++);
			} else {
				unitCount.put(u.team(), 1);
			}
		}
		return unitCount;
	}

	private boolean defineControlTeam(Map<Team, Integer> unitCount) {
		boolean twoTeams = false;
		int max = Integer.MIN_VALUE;
		Set<Map.Entry<Team, Integer>> entries = unitCount.entrySet();
		for (Map.Entry<Team, Integer> entry : entries) {
			if (entry.getValue() > max) {
				max = entry.getValue();
				controlTeam = entry.getKey();
				if (prevControlTeam == controlTeam) {
					controlLength++;
				} else {
					prevControlTeam = controlTeam;
					controlLength = 1;
				}
			}
			if (entry.getValue() == max && entry.getKey() != controlTeam) {
				twoTeams = true;
				prevControlTeam = null;
				controlLength = 0;

			}
		}
		return twoTeams;
	}

	private void healUnits(boolean twoTeams, List<Unit> seenUnits) {
		if (!twoTeams && controlTeam != null) {
			if (listener != null) {
				listener.onTeamChange(controlTeam.getColor());
			} //színállítás
			for (var u : seenUnits) {
				if (u.team() == controlTeam) {
					u.updateSelf(percentage);
				}
			}
		}
	}

	public void updateNearbyUnits() {
		boolean twoContolrTeams;
		//this could be reworked to work with percievedUnits as well, but then the PercievedUnits should store the unit
		//the perviecedUnit literally should be an another view, or even better, an interface, and i could

		var seenUnits = mm.requestUnits(pos, size + 0.5f);
		if (!seenUnits.isEmpty()) {
			var unitCount = countUnits(seenUnits);
			//eddig csak megszámoltuk, hogy melyik csapathoz hány egység tartozik

			twoContolrTeams = defineControlTeam(unitCount);
			// megnézzük, hogy melyik csapathoz tartozik a ControlPoint

			healUnits(twoContolrTeams, seenUnits);
			//controlTeam healelése
		} else {
			if (listener != null) {
				listener.onTeamChange(Color.DEFAULT);
				controlTeam = null;
			}
		}
	}

	public int getControlLength() {
		return controlLength;
	}

	public Position pos() {
		return pos;
	}

	public int size() {
		return size;
	}

	public int getId() {
		return id;
	}

	public void registerListener(ControlPointListener cpl) {
		listener = cpl;
	}

	public String toString() {
		return this.pos.toString() + " " + this.percentage + " " + this.size + " " + this.id;
	}

	public JSONObject toJSON() {
		return new JSONObject().put("id", this.id).put("pos", this.pos.toJSON()).put("size", this.size).put("percentage", this.percentage);
	}

	@Override
	public boolean equals(Object o) {
		if (this == o) return true;
		if (o == null || getClass() != o.getClass()) return false;
		ControlPoint that = (ControlPoint) o;
		return id == that.id;
	}

	@Override
	public int hashCode() {
		return Objects.hashCode(id);
	}
}
