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
import java.awt.geom.Rectangle2D;
import java.util.HashMap;
import java.util.Map;


public class MainView extends JPanel implements MainModelListener {
    private final JFrame frame;
    private final int width;
    private final int height;
    private final int size;
    private final float squareSize;
    private final float udc;

    private final Map<Unit, UnitView> unitViews;
    private final Map<Field, FieldView> fieldViews;
    private final Map<ControlPoint, ControlPointView> controlPointViews;
    private final Map<Team, TeamView> teamViews;

    public MainView(int width, int height, float udc, int NoF, int fps) {
        frame = new JFrame("float");
        frame.setDefaultCloseOperation(JFrame.EXIT_ON_CLOSE);
        this.width = width;
        this.height = height;
        this.size = Math.min(width, height);
        this.udc = udc;
        this.squareSize =  (size / udc) / NoF;
        frame.setSize(width, height);
        frame.getContentPane().add(this);
        frame.setVisible(true);

        this.unitViews = new HashMap<>();
        this.fieldViews = new HashMap<>();
        this.controlPointViews = new HashMap<>();
        this.teamViews = new HashMap<>();

        Timer looper = new Timer(1000 / fps, e -> repaint());
        looper.start();

    }

    @Override
    public void paintComponent(Graphics g) {
        super.paintComponent(g);
        Graphics2D g2d = (Graphics2D) g;
        g2d.setRenderingHint(RenderingHints.KEY_ANTIALIASING, RenderingHints.VALUE_ANTIALIAS_ON);
        var bg = new Rectangle2D.Float(0, 0, size, size);
        g2d.fill(bg);
        g2d.setClip(bg);
        fieldViews.forEach((_, fv) -> fv.render(g2d));
        unitViews.forEach((_, uv) -> uv.render(g2d));
        controlPointViews.forEach((_, cpv) -> cpv.render(g2d));
        g2d.setClip(new Rectangle2D.Float(size, 0, width, height));
        int i = 1;
        for (var tv: teamViews.values()) {
            int x = (width - height) * i / (teamViews.size() + 1);
            tv.render(g2d, size + x, 20);
            i++;
        }
    }

    @Override
    public void unitCreated(Unit u) {
        unitViews.put(u, new UnitView(u, this.squareSize, this.udc));
    }

    @Override
    public void unitDestoryed(Unit u) {
        var uv = unitViews.get(u);
        uv.unitDied();

    }

    @Override
    public void controlPointCreated(ControlPoint cp) {
        controlPointViews.put(cp, new ControlPointView(cp, this.squareSize, this.udc));
    }

    @Override
    public void fieldCreated(Field f) {
        fieldViews.put(f, new FieldView(f, this.squareSize, this.udc));
    }

    @Override
    public void teamCreated(Team t) {
        teamViews.put(t, new TeamView(t));
    }

    @Override
    public void teamDestroyed(Team t) {
        teamViews.remove(t);
    }
}