package view;

import model.Team;

import java.awt.*;
import java.awt.geom.Rectangle2D;
import java.util.ArrayList;

public class TeamView {
    private final Team team;

    public TeamView(Team t) {
        this.team = t;
    }

    public void render(Graphics2D g2d, int x, int inity) {
        g2d.setColor(Color.BLACK);
        Font oldFont = g2d.getFont();
        Font newFont = oldFont.deriveFont(oldFont.getSize() * 1.4F);
        g2d.setFont(newFont);
        int y = inity;
        ArrayList<String> teamInfo = team.teamMembersToString();
        for(var s : teamInfo) {
            for (String line : s.split("\n")) {
                g2d.drawString(line, x, y);
                y += 20;
            }
            y += 50;
        }
        g2d.setFont(oldFont);
    }
}
