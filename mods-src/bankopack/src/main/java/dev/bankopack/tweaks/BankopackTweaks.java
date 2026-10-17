package dev.bankopack.tweaks;

import com.mojang.logging.LogUtils;
import dev.bankopack.tweaks.debug.TerrainStatsCommand;
import dev.bankopack.tweaks.shaders.ShaderSwitcher;
import net.neoforged.api.distmarker.Dist;
import net.neoforged.bus.api.IEventBus;
import net.neoforged.fml.ModContainer;
import net.neoforged.fml.ModList;
import net.neoforged.fml.common.Mod;
import net.neoforged.fml.config.ModConfig;
import net.neoforged.fml.loading.FMLEnvironment;
import net.neoforged.neoforge.common.NeoForge;
import org.slf4j.Logger;

@Mod(BankopackTweaks.MODID)
public class BankopackTweaks {
    public static final String MODID = "bankopack";
    public static final Logger LOGGER = LogUtils.getLogger();

    public BankopackTweaks(IEventBus modBus, ModContainer container) {
        container.registerConfig(ModConfig.Type.CLIENT, Config.SPEC);
        NeoForge.EVENT_BUS.addListener(TerrainStatsCommand::register);

        if (FMLEnvironment.dist == Dist.CLIENT) {
            // ShaderSwitcher references Iris classes, so only touch it when Iris is present.
            // The JEI plugin is discovered by JEI itself via @JeiPlugin, so it needs no wiring here.
            if (ModList.get().isLoaded("iris")) {
                NeoForge.EVENT_BUS.addListener(ShaderSwitcher::onClientTick);
            } else {
                LOGGER.info("Iris not installed; dimension-based shader switching is inactive");
            }
            if (ModList.get().isLoaded("jei")) {
                NeoForge.EVENT_BUS.addListener(dev.bankopack.tweaks.jei.FtbRecipeKeys::onKeyPressed);
            }
        }
    }
}
