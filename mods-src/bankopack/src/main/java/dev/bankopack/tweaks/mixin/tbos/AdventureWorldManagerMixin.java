package dev.bankopack.tweaks.mixin.tbos;

import net.minecraft.server.level.ServerLevel;
import net.minecraft.world.level.levelgen.Heightmap;
import org.spongepowered.asm.mixin.Mixin;
import org.spongepowered.asm.mixin.injection.At;
import org.spongepowered.asm.mixin.injection.Redirect;

/**
 * The Birth of Steve places the Meridian Archive (when the Archive Survey Map is first used) by asking
 * {@code level.getHeight(...)} for a spot ~384 blocks away. For an unloaded chunk, vanilla's
 * {@code Level.getHeight} returns the world's minimum height instead of generating the chunk, so the
 * archive ends up buried at the bottom of the world. Loading the chunk first makes the heightmap real.
 */
@Mixin(targets = "com.nightbeam.tbos.world.AdventureWorldManager", remap = false)
public abstract class AdventureWorldManagerMixin {
    @Redirect(
        method = "findDrySurface",
        at = @At(value = "INVOKE",
                 target = "Lnet/minecraft/server/level/ServerLevel;getHeight(Lnet/minecraft/world/level/levelgen/Heightmap$Types;II)I"),
        require = 0)
    private static int bankopack$heightWithLoadedChunk(ServerLevel level, Heightmap.Types type, int x, int z) {
        level.getChunk(x >> 4, z >> 4); // generates/loads the chunk to FULL so its heightmap exists
        return level.getHeight(type, x, z);
    }
}
