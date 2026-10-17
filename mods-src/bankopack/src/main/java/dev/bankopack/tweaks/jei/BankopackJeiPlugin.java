package dev.bankopack.tweaks.jei;

import dev.bankopack.tweaks.BankopackTweaks;
import dev.bankopack.tweaks.Config;
import java.util.List;
import java.util.Map;
import mezz.jei.api.IModPlugin;
import mezz.jei.api.JeiPlugin;
import mezz.jei.api.registration.IModInfoRegistration;
import mezz.jei.api.runtime.IJeiRuntime;
import net.minecraft.resources.ResourceLocation;
import net.neoforged.fml.ModList;

/**
 * Registers extra mod-name aliases so JEI's @ search can group several mods under one name, and hands the JEI
 * runtime to {@link FtbRecipeKeys}.
 */
@JeiPlugin
public class BankopackJeiPlugin implements IModPlugin {
    private static final ResourceLocation UID = ResourceLocation.fromNamespaceAndPath(BankopackTweaks.MODID, "mod_aliases");

    @Override
    public ResourceLocation getPluginUid() {
        return UID;
    }

    @Override
    public void registerModInfo(IModInfoRegistration registration) {
        for (Map.Entry<String, List<String>> entry : Config.jeiModAliases()) {
            for (String modId : entry.getValue()) {
                if (ModList.get().isLoaded(modId)) {
                    registration.addModAliases(modId, entry.getKey());
                }
            }
        }
    }

    @Override
    public void onRuntimeAvailable(IJeiRuntime jeiRuntime) {
        FtbRecipeKeys.setRuntime(jeiRuntime);
    }

    @Override
    public void onRuntimeUnavailable() {
        FtbRecipeKeys.setRuntime(null);
    }
}
