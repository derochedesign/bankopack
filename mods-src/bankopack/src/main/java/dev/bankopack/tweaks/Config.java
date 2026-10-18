package dev.bankopack.tweaks;

import java.util.ArrayList;
import java.util.List;
import java.util.Map;
import net.minecraft.resources.ResourceLocation;
import net.neoforged.neoforge.common.ModConfigSpec;

public final class Config {
    private static final ModConfigSpec.Builder BUILDER = new ModConfigSpec.Builder();

    private static final ModConfigSpec.ConfigValue<List<? extends String>> SHADER_OFF_DIMENSIONS;
    private static final ModConfigSpec.ConfigValue<List<? extends String>> JEI_MOD_ALIASES;
    public static final ModConfigSpec.DoubleValue GUI_SCALE;

    static {
        BUILDER.push("shaders");
        SHADER_OFF_DIMENSIONS = BUILDER
            .comment("Dimensions where Iris shaders are turned off automatically.",
                     "Use full IDs like \"ad_astra:moon\", or \"namespace:*\" for every dimension from a mod.")
            .defineListAllowEmpty("dimensions", List.of("ad_astra:*", "the_bumblezone:the_bumblezone", "eternal_starlight:starlight"), () -> "", Config::isValidDimensionEntry);
        BUILDER.pop();

        BUILDER.push("jei");
        JEI_MOD_ALIASES = BUILDER
            .comment("Extra names JEI's @ mod search will match, as \"alias=modid1,modid2,...\".",
                     "Example: \"rpg=wizards,rogues\" makes @rpg list items from both mods. Restart the game after editing.")
            .defineListAllowEmpty("mod_aliases", List.of(
                "rpg=wizards,paladins,rogues,archers,jewelry,spell_engine,runes,skill_tree_rpgs,more_rpg_classes,"
                    + "berserker_rpg,forcemaster_rpg,witcher_rpg,elemental_wizards_rpg,bards_rpg"),
                () -> "", Config::isValidAliasEntry);
        BUILDER.pop();

        BUILDER.push("gui");
        GUI_SCALE = BUILDER
            .comment("GUI scale to use instead of the whole-number Video Settings slider, e.g. 2.5.",
                     "Capped to the largest scale your window fits (the same limit as vanilla's Auto).",
                     "Set to 0 to use the vanilla slider again.")
            .defineInRange("gui_scale", 2.5, 0.0, 8.0);
        BUILDER.pop();
    }

    public static final ModConfigSpec SPEC = BUILDER.build();

    private Config() {}

    private static boolean isValidDimensionEntry(Object o) {
        if (!(o instanceof String s)) return false;
        return s.endsWith(":*") ? ResourceLocation.isValidNamespace(s.substring(0, s.length() - 2))
                                : ResourceLocation.tryParse(s) != null;
    }

    private static boolean isValidAliasEntry(Object o) {
        return o instanceof String s && s.indexOf('=') > 0 && s.indexOf('=') < s.length() - 1;
    }

    public static boolean isShaderOffDimension(ResourceLocation dim) {
        String id = dim.toString();
        for (String entry : SHADER_OFF_DIMENSIONS.get()) {
            if (entry.endsWith(":*") ? dim.getNamespace().equals(entry.substring(0, entry.length() - 2))
                                     : entry.equals(id)) {
                return true;
            }
        }
        return false;
    }

    /** Parsed JEI aliases as (alias, modIds) pairs. */
    public static List<Map.Entry<String, List<String>>> jeiModAliases() {
        List<Map.Entry<String, List<String>>> result = new ArrayList<>();
        for (String entry : JEI_MOD_ALIASES.get()) {
            int eq = entry.indexOf('=');
            String alias = entry.substring(0, eq).trim();
            List<String> modIds = new ArrayList<>();
            for (String id : entry.substring(eq + 1).split(",")) {
                if (!id.isBlank()) modIds.add(id.trim());
            }
            result.add(Map.entry(alias, modIds));
        }
        return result;
    }
}
