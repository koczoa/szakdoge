package common;

import model.MainModel;
import communicator.MainCommunicator;
import view.MainView;

import java.io.IOException;

public class Main {
	public static void main(String[] args) throws IOException {
		MainModel mm = new MainModel(10);
		mm.placeDefaultUnits();
		mm.placeDefaultControlPoints();
		MainCommunicator mc = new MainCommunicator(mm);
		mm.addListener(mc);

		if (args.length >= 1 && args[0].equals("graf")) {
			MainView mv = new MainView(1600, 1000, 1.1f, mm.width());
			mm.addListener(mv);
		}
		while (true) {
			var go = mc.tick();
			if(!go) {
				System.exit(0);
			}
		}
	}
}
