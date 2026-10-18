package dev.bankopack.tweaks;

import net.minecraft.client.Minecraft;
import net.neoforged.bus.api.IEventBus;
import net.neoforged.fml.ModContainer;
import net.neoforged.fml.ModList;
import net.neoforged.fml.event.config.ModConfigEvent;
import net.neoforged.neoforge.client.gui.ConfigurationScreen;
import net.neoforged.neoforge.client.gui.IConfigScreenFactory;

/** Client-only setup, kept out of {@link BankopackTweaks} so a dedicated server never loads client classes. */
final class BankopackClient {
    private static double appliedGuiScale = Double.NaN;

    private BankopackClient() {}

    static void init(IEventBus modBus, ModContainer container) {
        container.registerExtensionPoint(IConfigScreenFactory.class, ConfigurationScreen::new);
        modBus.addListener(ModConfigEvent.Loading.class, e -> {
            if (e.getConfig().getSpec() == Config.SPEC) appliedGuiScale = Config.GUI_SCALE.get();
        });
        modBus.addListener(ModConfigEvent.Reloading.class, e -> {
            if (e.getConfig().getSpec() != Config.SPEC) return;
            double scale = Config.GUI_SCALE.get();
            if (scale == appliedGuiScale) return;
            appliedGuiScale = scale;
            Minecraft mc = Minecraft.getInstance();
            mc.execute(() -> {
                mc.resizeDisplay();
                // Shader framebuffers keep the old layout after a GUI scale change until Iris reloads.
                if (ModList.get().isLoaded("iris")) dev.bankopack.tweaks.shaders.IrisReload.reload();
            });
        });
    }
}
