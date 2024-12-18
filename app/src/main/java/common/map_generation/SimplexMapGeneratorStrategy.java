package common.map_generation;

import model.Field;
import model.Position;
import util.SimplexNoise;

import java.util.HashMap;
import java.util.Map;

public class SimplexMapGeneratorStrategy implements MapGeneratorStrategy {
	private final int starterCornerSize = 5;
	@Override
	public Map<Position, Field> generateMap(int mapSize) {
		Map<Position, Field> fields = new HashMap<>();
		for (int i = 0; i < mapSize; i++) {
			for (int j = 0; j < mapSize; j++) {
				var temPos = new Position(i, j);
				var noiseProb = SimplexNoise.noise(i / 20.0, j / 10.0, 25);
				if (-1 < noiseProb && noiseProb <= 0.2) {
					fields.put(temPos, new Field(temPos, Field.Type.GRASS));
				} else if (0.2 < noiseProb && noiseProb <= 0.4) {
					fields.put(temPos, new Field(temPos, Field.Type.WATER));
				} else if (0.4 < noiseProb && noiseProb <= 0.6) {
					fields.put(temPos, new Field(temPos, Field.Type.FOREST));
				} else if (0.6 < noiseProb && noiseProb <= 0.8) {
					fields.put(temPos, new Field(temPos, Field.Type.BUILDING));
				} else if (0.8 < noiseProb && noiseProb <= 1) {
					fields.put(temPos, new Field(temPos, Field.Type.MARSH));
				}
			}
		}
		replaceCorners(fields, mapSize);
		return fields;
	}

	private void replaceCorners(Map<Position, Field> fields, int mapSize) {
		for (int i = 0; i < starterCornerSize; i++) {
			for (int j = 0; j < starterCornerSize; j++) {
				fields.replace(new Position(i, j), new Field(new Position(i, j), Field.Type.GRASS));
			}
		}
		for (int i = mapSize - 1; i > mapSize - starterCornerSize; i--) {
			for (int j = mapSize - 1; j > mapSize - starterCornerSize; j--) {
				fields.replace(new Position(i, j), new Field(new Position(i, j), Field.Type.GRASS));
			}
		}
	}
}
