package common;

import model.MainModel;
import communicator.MainCommunicator;

import java.io.IOException;

public class Main {
	public static void main(String[] args) throws IOException {
		System.out.println("Hello");
		MainModel mm = new MainModel(60);
		mm.placeDefaultUnits();
		mm.placeDefaultControlPoints();
		MainCommunicator mc = new MainCommunicator(mm);
		mm.addListener(mc);
		while (true) {
			mc.tick();
		}
	}
}
