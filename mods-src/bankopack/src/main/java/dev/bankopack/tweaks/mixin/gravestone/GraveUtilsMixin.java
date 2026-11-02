package dev.bankopack.tweaks.mixin.gravestone;

import net.minecraft.core.BlockPos;
import net.minecraft.world.level.Level;
import net.minecraft.world.level.levelgen.Heightmap;
import org.spongepowered.asm.mixin.Mixin;
import org.spongepowered.asm.mixin.injection.At;
import org.spongepowered.asm.mixin.injection.Inject;
import org.spongepowered.asm.mixin.injection.callback.CallbackInfoReturnable;

/**
 * Gravestone searches upward from the death position for a free block, so a player who dies above the build limit
 * (e.g. fighting a wither at y 350) gets no grave and their items drop in midair. For those deaths, put the grave on
 * the highest free block of that column instead. Its own {@code strict_placement} option doesn't help: it targets
 * y = max build height, which is itself outside the world, so the grave block never places.
 */
@Mixin(targets = "de.maxhenkel.gravestone.GraveUtils", remap = false)
public abstract class GraveUtilsMixin {
    @Inject(method = "getGraveStoneLocation", at = @At("HEAD"), cancellable = true, require = 0)
    private static void bankopack$graveBelowBuildLimit(Level level, BlockPos pos, CallbackInfoReturnable<BlockPos> cir) {
        if (pos.getY() < level.getMaxBuildHeight()) return;
        BlockPos column = level.getWorldBorder().clampToBounds(pos);
        int top = level.getHeight(Heightmap.Types.MOTION_BLOCKING, column.getX(), column.getZ());
        if (top < level.getMaxBuildHeight()) cir.setReturnValue(new BlockPos(column.getX(), top, column.getZ()));
    }
}
