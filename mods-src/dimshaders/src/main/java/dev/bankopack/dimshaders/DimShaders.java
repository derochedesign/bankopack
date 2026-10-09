package dev.bankopack.dimshaders;

import com.mojang.logging.LogUtils;
import net.neoforged.api.distmarker.Dist;
import net.neoforged.bus.api.IEventBus;
import net.neoforged.fml.ModContainer;
import net.neoforged.fml.ModList;
import net.neoforged.fml.common.Mod;
import net.neoforged.fml.config.ModConfig;
import net.neoforged.neoforge.common.NeoForge;
import org.slf4j.Logger;

@Mod(value = DimShaders.MODID, dist = Dist.CLIENT)
public class DimShaders {
    public static final String MODID = "dimshaders";
    static final Logger LOGGER = LogUtils.getLogger();

    public DimShaders(IEventBus modBus, ModContainer container) {
        container.registerConfig(ModConfig.Type.CLIENT, Config.SPEC);
        // ShaderSwitcher references Iris classes, so only touch it when Iris is present.
        if (ModList.get().isLoaded("iris")) {
            NeoForge.EVENT_BUS.addListener(ShaderSwitcher::onClientTick);
        } else {
            LOGGER.info("Iris not installed; dimension-based shader switching is inactive");
        }
    }
}
