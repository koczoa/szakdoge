package common;

import model.MainModel;
import communicator.MainCommunicator;

import java.io.IOException;

public class Main {
	public static void main(String[] args) throws IOException {
		MainModel mm = new MainModel(10);
		mm.placeDefaultUnits();
		mm.placeDefaultControlPoints();
		MainCommunicator mc = new MainCommunicator(mm);
		mm.addListener(mc);
		while (true) {
			var go = mc.tick();
			if(!go) {
				System.exit(0);
			}
		}
	}
}
