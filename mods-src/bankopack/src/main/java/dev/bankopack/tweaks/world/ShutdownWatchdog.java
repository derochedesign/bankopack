package dev.bankopack.tweaks.world;

import dev.bankopack.tweaks.BankopackTweaks;
import net.neoforged.neoforge.common.NeoForge;
import net.neoforged.neoforge.event.server.ServerStoppedEvent;

/**
 * Distant Horizons leaves non-daemon threads running, so after a crash the dedicated server saves the world and
 * then never exits: the container sits "unhealthy" and Docker's restart policy never kicks in (2026-10-24, ~9 hours
 * down). Once the server has fully stopped, give the JVM 30 seconds to exit on its own, then halt it.
 * Only registered on the dedicated server; on a client, ServerStoppedEvent fires when leaving a singleplayer world.
 */
public final class ShutdownWatchdog {
    private static final long GRACE_MILLIS = 30_000;

    private ShutdownWatchdog() {}

    public static void register() {
        NeoForge.EVENT_BUS.addListener(ServerStoppedEvent.class, e -> {
            Thread watchdog = new Thread(() -> {
                try {
                    Thread.sleep(GRACE_MILLIS);
                } catch (InterruptedException ex) {
                    return;
                }
                BankopackTweaks.LOGGER.warn("Server stopped {}s ago but the JVM is still running; halting", GRACE_MILLIS / 1000);
                Runtime.getRuntime().halt(1);
            }, "Bankopack shutdown watchdog");
            watchdog.setDaemon(true);
            watchdog.start();
        });
    }
}
