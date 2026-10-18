package dev.bankopack.tweaks;

import net.neoforged.neoforge.common.ModConfigSpec;

/**
 * Fractional GUI scale, kept in its own file (config/bankopack-gui.toml) so pack updates never overwrite a
 * player's choice. Applied by {@code mixin.client.GuiScaleMixin}.
 */
public final class GuiScaleConfig {
    private static final ModConfigSpec.Builder BUILDER = new ModConfigSpec.Builder();

    public static final ModConfigSpec.DoubleValue SCALE = BUILDER
        .comment("GUI scale to use instead of the whole-number Video Settings slider, e.g. 2.3.",
                 "Capped to the largest scale your window fits (the same limit as vanilla's Auto).",
                 "Set to 0 to use the vanilla slider again.")
        .defineInRange("gui_scale", 2.3, 0.0, 8.0);

    public static final ModConfigSpec SPEC = BUILDER.build();

    private GuiScaleConfig() {}
}
