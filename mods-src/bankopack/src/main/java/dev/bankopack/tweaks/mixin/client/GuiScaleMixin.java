package dev.bankopack.tweaks.mixin.client;

import com.mojang.blaze3d.platform.Window;
import dev.bankopack.tweaks.GuiScaleConfig;
import net.minecraft.client.Minecraft;
import org.spongepowered.asm.mixin.Final;
import org.spongepowered.asm.mixin.Mixin;
import org.spongepowered.asm.mixin.Shadow;
import org.spongepowered.asm.mixin.injection.At;
import org.spongepowered.asm.mixin.injection.ModifyArg;

/**
 * Vanilla only allows whole-number GUI scales. {@code resizeDisplay} is the one place the scale is applied
 * (window resize, option change, startup), so swapping the value there changes every screen and the HUD alike.
 */
@Mixin(Minecraft.class)
public abstract class GuiScaleMixin {
    @Shadow @Final private Window window;

    @Shadow public abstract boolean isEnforceUnicode();

    @ModifyArg(method = "resizeDisplay", at = @At(value = "INVOKE",
            target = "Lcom/mojang/blaze3d/platform/Window;setGuiScale(D)V"))
    private double bankopack$fractionalGuiScale(double vanillaScale) {
        double wanted;
        try {
            wanted = GuiScaleConfig.SCALE.get();
        } catch (IllegalStateException notLoadedYet) {
            return vanillaScale;
        }
        if (wanted <= 0) return vanillaScale;
        int largestThatFits = window.calculateScale(0, isEnforceUnicode());
        return Math.max(1.0, Math.min(wanted, largestThatFits));
    }
}
