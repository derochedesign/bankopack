package dev.bankopack.tweaks.shaders;

import dev.bankopack.tweaks.BankopackTweaks;
import dev.bankopack.tweaks.Config;
import java.util.Objects;
import net.irisshaders.iris.api.v0.IrisApi;
import net.irisshaders.iris.api.v0.IrisApiConfig;
import net.minecraft.client.Minecraft;
import net.minecraft.resources.ResourceKey;
import net.minecraft.world.level.Level;
import net.neoforged.neoforge.client.event.ClientTickEvent;

/** Turns shaders off on entering a listed dimension, and back on when leaving, if we were the ones who turned them off. */
public final class ShaderSwitcher {
    private static ResourceKey<Level> lastDimension;
    private static boolean disabledByUs;

    private ShaderSwitcher() {}

    public static void onClientTick(ClientTickEvent.Post event) {
        Minecraft mc = Minecraft.getInstance();
        ResourceKey<Level> dimension = mc.level == null ? null : mc.level.dimension();
        if (Objects.equals(dimension, lastDimension)) return;
        lastDimension = dimension;

        try {
            IrisApiConfig iris = IrisApi.getInstance().getConfig();
            // Leaving the world counts as "not listed", so shaders are restored before Iris saves its config.
            boolean listed = dimension != null && Config.isShaderOffDimension(dimension.location());
            if (listed && iris.areShadersEnabled()) {
                disabledByUs = true;
                iris.setShadersEnabledAndApply(false);
                BankopackTweaks.LOGGER.info("Shaders off in {}", dimension.location());
            } else if (!listed && disabledByUs) {
                disabledByUs = false;
                iris.setShadersEnabledAndApply(true);
                BankopackTweaks.LOGGER.info("Shaders back on ({})", dimension == null ? "left world" : dimension.location());
            }
        } catch (Throwable t) {
            BankopackTweaks.LOGGER.error("Failed to toggle shaders", t);
        }
    }
}
