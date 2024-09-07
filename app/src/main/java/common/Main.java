package common;

import model.MainModel;
import communicator.MainCommunicator;

public class Main {
	public static void main(String[] args) {
		System.out.println("Hello");
		MainModel mm = new MainModel(60);
		mm.placeDefaultUnits();
		mm.placeDefaultControlPoints();
		MainCommunicator mc = new MainCommunicator(mm);
		mm.addListener(mc);
	}
}
