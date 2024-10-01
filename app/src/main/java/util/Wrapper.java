package util;

import logger.Label;
import org.json.JSONArray;
import org.json.JSONObject;

import java.io.IOException;
import java.nio.ByteBuffer;
import java.nio.channels.SocketChannel;
import java.nio.charset.StandardCharsets;

public class Wrapper {
    private final SocketChannel sc;
    private ByteBuffer buffer;
    private State state;

    public enum State {
        SIZE,
        DATA
    }

    public Wrapper(SocketChannel sc) {
        this.sc = sc;
        this.state = State.SIZE;
        this.buffer = ByteBuffer.allocate(4);
    }

    public void write(JSONObject message, Label javaLogLabel) throws IOException {
        ByteBuffer sizeBuffer = ByteBuffer.allocate(4);
        ByteBuffer buffer = StandardCharsets.UTF_8.encode(message.toString());
        sizeBuffer.putInt(buffer.limit());
        sizeBuffer.position(0);
        sc.write(sizeBuffer);
        sc.write(buffer);
        buffer.position(0);
        sizeBuffer.position(0);
//      Log.d(javaLogLabel, "buffcap: " + buffer.capacity() + " bufflim: " + buffer.limit());
    }


    public JSONArray read() throws IOException {
        var asdf = sc.read(buffer);
        System.out.println(asdf + " " + buffer);
        if(buffer.hasRemaining()) {
            return null;
        }
        if(state == State.SIZE) {
            buffer.position(0);
            var size = buffer.getInt();
            buffer = ByteBuffer.allocate(size);
            this.state = State.DATA;
            return read();
        } else {
            buffer.position(0);
            var message = StandardCharsets.UTF_8.decode(buffer);
            this.state = State.SIZE;
            buffer = ByteBuffer.allocate(4);
            return new JSONArray(message.toString());
        }
    }

    public void close() {
        try {
            sc.close();
        } catch (IOException e) {}
    }
}
