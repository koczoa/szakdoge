package model;


import common.UnitListener;
import logger.Label;
import logger.Log;
import util.Color;

import org.json.*;
import util.Triplet;

import java.nio.file.Path;
import java.util.ArrayList;
import java.util.List;
import java.util.Scanner;

public class Unit {
	private static final Path descriptorDir = Path.of("src", "/main/resources/descriptors");

	private final int id;
	private Field field;
	private List<Field> seenFields;
	private List<PerceivedUnit> seenUnits;
	private List<ControlPoint> seenControlPoints;
	private final List<Field.Type> steppableTypes;
	private final Team team;
	private final Type type;
	private UnitListener listener;

	private int health;
	private int maxHealth;
	private int viewRange;
	private int shootRange;
	private int damage;
	private int ammo;
	private int maxAmmo;
	private int fuel;
	private int maxFuel;
	private int consumption;
	private int price;
	private int maxActionPoints;
	private int actionPoints;
	private final Position startingPos;
	private final Label javaLogLabel;

	private static int idCounter = 0;

	public enum Type {
		SCOUT("SCOUT"),
		TANK("TANK"),
		INFANTRY("INFANTRY");

		public final Path path;

		Type(String sourceFileName) {
			path = Path.of(sourceFileName);
		}
	}

	public Unit(Field f, Team team, Type type) {
		seenFields = new ArrayList<>();
		seenUnits = new ArrayList<>();
		steppableTypes = new ArrayList<>();
		id = idCounter++;
		setField(f);
		this.team = team;
		team.addUnit(this);
		this.type = type;
		this.startingPos = f.pos();
		try (Scanner sc = new Scanner(descriptorDir.resolve(type.path))) {
			maxHealth = Integer.parseInt(sc.nextLine());
			viewRange = Integer.parseInt(sc.nextLine());
			shootRange = Integer.parseInt(sc.nextLine());
			damage = Integer.parseInt(sc.nextLine());
			maxAmmo = Integer.parseInt(sc.nextLine());
			maxFuel = Integer.parseInt(sc.nextLine());
			consumption = Integer.parseInt(sc.nextLine());
			maxActionPoints = Integer.parseInt(sc.nextLine());
			price = Integer.parseInt(sc.nextLine());
			steppableTypes.add(Field.Type.valueOf(sc.nextLine()));
		} catch (Exception e) {
			e.printStackTrace();
		}
		health = maxHealth;
		ammo = maxAmmo;
		fuel = maxFuel;
		actionPoints = maxActionPoints;
		javaLogLabel = new Label(
				team.getName() + " javaUnit",
				Label.Color.BLACK,
				team.getName().equals("red") ? Label.Color.RED : Label.Color.WHITE
		);
	}

	public void move(Field dest) {
		if (actionPoints <= 0) {
			Log.e(javaLogLabel,this.id + "id: out of actionPoints");
		}
		if (fuel < consumption) {
			Log.e(javaLogLabel,this.id + "id: out of fuel");
		}
		if (!field.isNeighbouring(dest)) {
			Log.e(javaLogLabel,this.id + "id: move not neighbouring: curr: " + this.field.pos().toString() + ", dest: " + dest);
		}
		if (!steppableTypes.contains(dest.type())) {
			Log.e(javaLogLabel,this.id + "id: dest not steppable");
		}
		if (!dest.arrive(this)) {
			Log.e(javaLogLabel,this.id + "id: dest occupied");
		}
		if (dest == field) {
			return;
		}
		field.leave();
		field = dest;
		fuel -= consumption;
		actionPoints--;
	}

	public void shoot(Field target) {
		if (actionPoints <= 0) {
			Log.e(javaLogLabel,this.id + "id: out of actionPoints");
		}
		if (ammo <= 0) {
			Log.e(javaLogLabel,this.id + "id: out of ammo");
		}
		if (!field.inDistance(target, shootRange + 0.5f)) {
			Log.e(javaLogLabel,this.id + "id: out of range");
		}

		target.takeShot(damage);
		if (listener != null) {
			listener.onShoot(target.pos());
		}
		ammo--;
		actionPoints--;
	}

	public void takeShot(int damage) {
		health -= damage;
		if (health <= 0) {
			field.leave();
			team.unitDied(id);
			if (listener != null) {
				listener.unitDied();
			}
		}
	}

	public void updateWorld(MainModel mm) {
		seenFields = mm.requestFileds(field.pos(), viewRange + 0.5f);
		seenUnits = mm.requestPerceivedUnits(field.pos(), viewRange + 0.5f);
		seenControlPoints = mm.requestControlPoints(field.pos(), viewRange + 0.5f);
	}

	public void refillActionPoints() {
		actionPoints = maxActionPoints;
	}

	public void updateSelf(int percentage) {
		int updateAmount;
		if (health <= maxHealth) {
			updateAmount = (int) Math.ceil(maxHealth * (percentage / 100f));
			health = Math.min(maxHealth, health + updateAmount);
		}
		if (ammo <= maxAmmo) {
			updateAmount = (int) Math.ceil(maxAmmo * (percentage / 100f));
			ammo = Math.min(maxAmmo, ammo + updateAmount);
		}
		if (fuel <= maxFuel) {
			updateAmount = (int) Math.ceil(maxHealth * (percentage / 100f));
			fuel = Math.min(maxFuel, fuel + updateAmount);
		}
	}

	public int getUUID() {
		return this.id;
	}

	public Position pos() {
		return field.pos();
	}

	public Team team() {
		return team;
	}

	public int shootRange() {
		return shootRange;
	}

	public Color color() {
		return team.getColor();
	}

	public int viewRange() {
		return viewRange;
	}

	public void registerListener(UnitListener ul) {
		listener = ul;
	}

	public Type type() {
		return type;
	}

	public int price() {
		return price;
	}

	public List<Field.Type> steppables() {
		return steppableTypes;
	}

	public PerceivedUnit getPerception() {
		return new PerceivedUnit(field.pos(), team.getName(), type.toString(), id, health);
	}

	public int actionPoints() {
		return actionPoints;
	}

	public Position getStartingPos() {
		return startingPos;
	}

	public String toString() {
		return "ID: " + id + "\n"
				+ "Type: " + type.toString() + "\n"
				+ "Pos: " + field.pos().toString() + "\n"
				+ "Health: " + health + "/" + maxHealth + "\n"
				+ "Ammo: " + ammo + "/" + maxAmmo + "\n"
				+ "Fuel: " + fuel + "/" + maxFuel + "\n";
	}
	public JSONObject toJSON() {
		JSONObject response = new JSONObject();
		response.put("id", id);
		response.put("type", type);
		response.put("currentField", field.toJSON());
		response.put("health", health);
		response.put("ammo", ammo);
		response.put("fuel", fuel);
		response.put("actionPoints", actionPoints);
		response.put("teamName", team.getName());
		return response;
	}

	public Triplet<List<Field>, List<PerceivedUnit>, List<ControlPoint>> toMerge() {
		return new Triplet<>(this.seenFields, this.seenUnits, this.seenControlPoints);
	}

	public void reset(Field f) {
		health = maxHealth;
		ammo = maxAmmo;
		fuel = maxFuel;
		actionPoints = maxActionPoints;
		setField(f);
		if (listener != null) {
			listener.unitReseted();
		}
	}

	public void setField(Field f) {
		if(this.field != null) {
			this.field.leave();
		}
		f.arrive(this);
		this.field = f;
	}
}