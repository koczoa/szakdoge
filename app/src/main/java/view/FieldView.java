package view;

import model.Field;
import util.Tuplet;

import java.awt.*;
import java.awt.geom.Rectangle2D;

public class FieldView {
    private Color color;
    private float squareSize;
    private Tuplet<Float, Float> center;

    public FieldView(Field f, float squareSize, float udc) {
        this.squareSize = squareSize;
        this.center = f.pos().screenCoords(squareSize, udc);
        switch (f.type()) {
            case BUILDING:
                this.color = new Color(0.5f, 0.5f, 0.5f, 1);
                break;
            case GRASS:
                this.color = new Color(0, 1, 0, 1);
                break;
            case WATER:
                this.color = new Color(0, 0, 1, 1);
                break;
            case FOREST:
                this.color = new Color(0.11f, 0.5f, 0.11f, 1);
                break;
            case MARSH:
                this.color = new Color(0.47f, 0.35f, 0.23f, 1);
                break;
        }
    }

    public void render(Graphics2D g2d) {
        g2d.setColor(this.color);
        g2d.fill(new Rectangle2D.Double(5, 5, 91, 91));
        System.out.println(squareSize);
    }
}
