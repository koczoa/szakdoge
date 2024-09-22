package view;

import common.ControlPointListener;
import model.ControlPoint;
import util.Tuplet;

import java.awt.*;
import java.awt.geom.Ellipse2D;

public class ControlPointView implements ControlPointListener {
    private util.Color color;
    private final Tuplet<Float, Float> center;
    private final float r;

    public ControlPointView(ControlPoint cp, float squareSize, float udc) {
        this.center = cp.pos().screenCoords(squareSize, udc);
        cp.registerListener(this);
        this.r = ((cp.size() + 1.5f) * squareSize * udc);
        this.color = util.Color.DEFAULT;
    }

    public void render(Graphics2D g2d) {
        switch (this.color) {
            case RED -> g2d.setColor(new Color(1f, 0, 0, 0.5f));
            case WHITE -> g2d.setColor(new Color(1f, 1f, 1f, 0.5f));
            case DEFAULT -> g2d.setColor(new Color(0, 1f, 1f, 0.5f));
        }
        g2d.fill(new Ellipse2D.Float(center.a - r, center.b - r, 2*r, 2*r));
    }

    @Override
    public void onTeamChange(util.Color c) {
        this.color = c;
    }
}