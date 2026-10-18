package dev.bankopack.tweaks;

import net.minecraft.client.Minecraft;
import net.neoforged.bus.api.IEventBus;
import net.neoforged.fml.ModContainer;
import net.neoforged.fml.config.ModConfig;
import net.neoforged.fml.event.config.ModConfigEvent;
import net.neoforged.neoforge.client.gui.ConfigurationScreen;
import net.neoforged.neoforge.client.gui.IConfigScreenFactory;

/** Client-only setup, kept out of {@link BankopackTweaks} so a dedicated server never loads client classes. */
final class BankopackClient {
    private BankopackClient() {}

    static void init(IEventBus modBus, ModContainer container) {
        // Own file so pack updates (which ship bankopack-client.toml) never reset a player's GUI scale.
        container.registerConfig(ModConfig.Type.CLIENT, GuiScaleConfig.SPEC, "bankopack-gui.toml");
        container.registerExtensionPoint(IConfigScreenFactory.class, ConfigurationScreen::new);
        modBus.addListener(ModConfigEvent.Reloading.class, e -> {
            if (e.getConfig().getSpec() == GuiScaleConfig.SPEC) {
                Minecraft mc = Minecraft.getInstance();
                mc.execute(mc::resizeDisplay);
            }
        });
    }
}
