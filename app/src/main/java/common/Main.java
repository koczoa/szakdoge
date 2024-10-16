package common;

import model.MainModel;
import communicator.MainCommunicator;
import view.MainView;

import javax.swing.*;
import java.io.IOException;

public class Main {
	public static void main(String[] args) throws IOException {
		MainModel mm = new MainModel(60);
		mm.placeDefaultUnits();
		mm.placeDefaultControlPoints();
		MainCommunicator mc = new MainCommunicator(mm);
		if (args.length >= 1 && args[0].equals("graf")) {
			SwingUtilities.invokeLater(() -> {
                MainView mv = new MainView(1600, 1000, 1.1f, mm.width(), 60);
                mm.addListener(mv);
            });

		}
		System.out.println("awaiting for connections");
		while (true) {
			var go = mc.tick(10);
			if(!go) {
				System.exit(0);
			}
		}
	}
}
