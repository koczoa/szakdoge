package view;

import model.Field;
import util.Tuplet;

import java.awt.*;
import java.awt.geom.Rectangle2D;

public class FieldView {
    private Color color;
    private final float squareSize;
    private final Tuplet<Float, Float> center;

    public FieldView(Field f, float squareSize, float udc) {
        this.squareSize = squareSize;
        this.center = f.pos().screenCoords(squareSize, udc);
        switch (f.type()) {
            case BUILDING -> this.color = new Color(0.5f, 0.5f, 0.5f, 1);
            case GRASS -> this.color = Color.GREEN;
            case WATER -> this.color = Color.BLUE;
            case FOREST -> this.color = new Color(0.11f, 0.5f, 0.11f, 1);
            case MARSH -> this.color = new Color(0.47f, 0.35f, 0.23f, 1);
        }
    }

    public void render(Graphics2D g2d) {
        g2d.setColor(this.color);
        g2d.fill(new Rectangle2D.Double(this.center.a - squareSize/2, this.center.b - squareSize/2, squareSize, squareSize));
    }
}
