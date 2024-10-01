package view;

import common.UnitListener;
import model.Position;
import model.Unit;
import util.Tuplet;

import javax.imageio.ImageIO;
import java.awt.*;
import java.awt.geom.Ellipse2D;
import java.awt.geom.Line2D;
import java.awt.image.BufferedImage;
import java.io.File;

public class UnitView implements UnitListener {
    private static final String IMAGES_PATH = System.getProperty("user.dir") + "/src/main/resources/images/";
    private Unit u;
    private Tuplet<Float, Float> center;
    private boolean currentlyShooting;
    private Position shootingPos;
    private int shootRange;
    private int viewRange;
    private util.Color c;
    private Image icon;
    private boolean visible = true;
    private final float squareSize;
    private final float udc;

    public UnitView(Unit u, float squareSize, float udc) {
        this.u = u;
        u.registerListener(this);
        this.currentlyShooting = false;
        this.squareSize = squareSize;
        this.udc = udc;
        this.shootRange = u.shootRange();
        this.viewRange = u.viewRange();
        this.c = u.color();
        try {
            if (u.type() == Unit.Type.TANK && icon == null) {
                icon = ImageIO.read(new File( IMAGES_PATH + "tank.png")).getScaledInstance(Math.round(squareSize), Math.round(squareSize), Image.SCALE_DEFAULT);;
            } else if (u.type() == Unit.Type.SCOUT && icon == null) {
                icon = ImageIO.read(new File(IMAGES_PATH + "scout.png")).getScaledInstance(Math.round(squareSize), Math.round(squareSize), Image.SCALE_DEFAULT);;
            } else if (u.type() == Unit.Type.INFANTRY && icon == null) {
                icon = ImageIO.read(new File(IMAGES_PATH + "infantry.png")).getScaledInstance(Math.round(squareSize), Math.round(squareSize), Image.SCALE_DEFAULT);;
            }
        } catch (Exception _) {}
    }


    public void render(Graphics2D g2d) {
        if (visible) {
            switch (c) {
                case RED -> g2d.setColor(Color.RED);
                case WHITE -> g2d.setColor(Color.WHITE);
                case DEFAULT -> g2d.setColor(Color.BLACK);
            }
            this.center = u.pos().screenCoords(squareSize, udc);
            g2d.fill(new Ellipse2D.Float(this.center.a - squareSize/2, this.center.b - squareSize/2, squareSize, squareSize));
            g2d.drawImage(this.icon, (int)(this.center.a - squareSize/2), (int)(this.center.b - squareSize/2), null);
            g2d.setStroke(new BasicStroke(2f));
            var r = ((shootRange + 0.5f) * squareSize * udc);
            g2d.draw(new Ellipse2D.Float(this.center.a - r, this.center.b - r, 2*r, 2*r));
            r = ((viewRange + 0.5f) * squareSize * udc);
            g2d.draw(new Ellipse2D.Float(this.center.a - r, this.center.b - r, 2*r, 2*r));
            g2d.setStroke(new BasicStroke(1f));
            if(currentlyShooting) {
                var shootingPosScreen = shootingPos.screenCoords(squareSize, udc);
                g2d.draw(new Line2D.Float(this.center.a, this.center.b, shootingPosScreen.a, shootingPosScreen.b));
            }
        }
    }

    @Override
    public void onShoot(Position p) {
        currentlyShooting = true;
        shootingPos = p;
    }

    @Override
    public void unitDied() {
        visible = false;
    }

    @Override
    public void unitReseted() {
        visible = true;
    }
}
