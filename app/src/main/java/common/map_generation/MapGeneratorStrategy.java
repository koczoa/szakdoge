package common.map_generation;

import model.Field;
import model.Position;

import java.util.Map;

public interface MapGeneratorStrategy {
	Map<Position, Field> generateMap(int mapSize);
}
