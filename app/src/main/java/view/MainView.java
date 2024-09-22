package view;

import common.MainModelListener;
import model.ControlPoint;
import model.Field;
import model.Team;
import model.Unit;

import javax.swing.*;
import java.awt.*;
import java.awt.event.ActionEvent;
import java.awt.event.ActionListener;
import java.util.HashMap;
import java.util.Map;


public class MainView extends JPanel implements MainModelListener {
    private final JFrame frame;
    private final int width;
    private final int height;
    private final int size;
    private final float squareSize;
    private final float udc;

    private Map<Unit, UnitView> unitViews;
    private Map<Field, FieldView> fieldViews;
    private Map<ControlPoint, ControlPointView> controlPointViews;

    public MainView(int width, int height, float udc, int NoF) {
        frame = new JFrame("float");
        frame.setDefaultCloseOperation(JFrame.EXIT_ON_CLOSE);
        this.width = width;
        this.height = height;
        size = Math.min(width, height);
        this.udc = udc;
        this.squareSize =  (size / udc) / NoF;
        System.out.println("s: " + size + " udc: " + udc + " sq: " + squareSize);
        frame.setSize(width, height);
        frame.getContentPane().add(this);
        frame.setVisible(true);

        unitViews = new HashMap<>();
        fieldViews = new HashMap<>();
        controlPointViews = new HashMap<>();

//        looper.start();

    }

    private Timer looper = new Timer(1000/100, new ActionListener() {
        @Override
        public void actionPerformed(ActionEvent e) {
            repaint();
        }
    });

    @Override
    public void paintComponent(Graphics g) {
        super.paintComponent(g);
        Graphics2D g2d = (Graphics2D) g;
        g.fillRect(0, 0, size, size);
        System.out.println("render starting");
        fieldViews.forEach((_, fv) -> fv.render(g2d));
        System.out.println("render ending");
        g.setColor(Color.BLUE);
        g2d.fillRect(405, 405, 91, 91);
        g.fillRect(205, 205, 91, 91);
    }

    @Override
    public void unitCreated(Unit u) {

    }

    @Override
    public void unitDestoryed(Unit u) {

    }

    @Override
    public void controlPointCreated(ControlPoint cp) {

    }

    @Override
    public void fieldCreated(Field f) {
        fieldViews.put(f, new FieldView(f, this.squareSize, this.udc));
    }
}