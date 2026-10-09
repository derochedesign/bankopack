package dev.bankopack.dimshaders;

import java.util.List;
import net.minecraft.resources.ResourceLocation;
import net.neoforged.neoforge.common.ModConfigSpec;

public final class Config {
    private static final ModConfigSpec.Builder BUILDER = new ModConfigSpec.Builder();

    static final ModConfigSpec.ConfigValue<List<? extends String>> DIMENSIONS = BUILDER
        .comment("Dimensions where shaders are turned off automatically.",
                 "Use full IDs like \"ad_astra:moon\", or \"namespace:*\" for every dimension from a mod.")
        .defineListAllowEmpty("dimensions", List.of("ad_astra:*"), () -> "", Config::isValidEntry);

    static final ModConfigSpec SPEC = BUILDER.build();

    private Config() {}

    private static boolean isValidEntry(Object o) {
        if (!(o instanceof String s)) return false;
        return s.endsWith(":*") ? ResourceLocation.isValidNamespace(s.substring(0, s.length() - 2))
                                : ResourceLocation.tryParse(s) != null;
    }

    static boolean isListed(ResourceLocation dim) {
        String id = dim.toString();
        for (String entry : DIMENSIONS.get()) {
            if (entry.endsWith(":*") ? dim.getNamespace().equals(entry.substring(0, entry.length() - 2))
                                     : entry.equals(id)) {
                return true;
            }
        }
        return false;
    }
}
