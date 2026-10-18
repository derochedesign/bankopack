package dev.bankopack.tweaks.shaders;

import dev.bankopack.tweaks.BankopackTweaks;
import net.irisshaders.iris.Iris;

/** Separate class so Iris is only touched when it is installed. */
public final class IrisReload {
    private IrisReload() {}

    public static void reload() {
        try {
            Iris.reload();
        } catch (Exception e) {
            BankopackTweaks.LOGGER.warn("Iris shader reload after GUI scale change failed", e);
        }
    }
}
