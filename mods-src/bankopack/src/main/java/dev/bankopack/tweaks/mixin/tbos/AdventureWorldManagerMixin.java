package dev.bankopack.tweaks.mixin.tbos;

import net.minecraft.core.BlockPos;
import net.minecraft.server.level.ServerLevel;
import net.minecraft.world.level.chunk.ChunkGenerator;
import net.minecraft.world.level.levelgen.Heightmap;
import net.minecraft.world.level.levelgen.RandomState;
import org.spongepowered.asm.mixin.Mixin;
import org.spongepowered.asm.mixin.injection.At;
import org.spongepowered.asm.mixin.injection.Inject;
import org.spongepowered.asm.mixin.injection.Redirect;
import org.spongepowered.asm.mixin.injection.callback.CallbackInfoReturnable;

/**
 * Fixes how The Birth of Steve picks ground for its Fracture Shrines and Meridian Archive
 * ({@code AdventureWorldManager.findDrySurface}).
 * <ul>
 *   <li>The original only tries 12 spots within 24 blocks of the target and falls back to the target even
 *       if it is water, so in ocean-heavy terrain sites land on the sea. We search outward in rings up to
 *       {@link #SEARCH_RADIUS} blocks, using the chunk generator's noise height (cheap, no chunk loading)
 *       to find land above sea level, then load only the chosen chunk.</li>
 *   <li>It reads {@code level.getHeight}, which returns the world's minimum height for unloaded chunks,
 *       burying the archive at the bottom of the world. The redirect loads the chunk first (also covers the
 *       original code path when our search finds no land).</li>
 * </ul>
 */
@Mixin(targets = "com.nightbeam.tbos.world.AdventureWorldManager", remap = false)
public abstract class AdventureWorldManagerMixin {
    private static final int SEARCH_RADIUS = 256;
    private static final int RING_STEP = 16;

    @Inject(method = "findDrySurface", at = @At("HEAD"), cancellable = true, require = 0)
    private static void bankopack$findDryLand(ServerLevel level, int targetX, int targetZ, int salt,
                                             CallbackInfoReturnable<BlockPos> cir) {
        ChunkGenerator generator = level.getChunkSource().getGenerator();
        RandomState randomState = level.getChunkSource().randomState();
        int seaLevel = generator.getSeaLevel();
        double angleOffset = Math.floorMod(salt, 360) * Math.PI / 180.0;

        for (int radius = 0; radius <= SEARCH_RADIUS; radius += RING_STEP) {
            int samples = radius == 0 ? 1 : Math.max(8, radius / 8);
            for (int i = 0; i < samples; i++) {
                double angle = angleOffset + i * 2.0 * Math.PI / samples;
                int x = targetX + (int) Math.round(Math.cos(angle) * radius);
                int z = targetZ + (int) Math.round(Math.sin(angle) * radius);
                // Terrain top ignoring water, straight from the noise: no chunk generation needed.
                int ground = generator.getBaseHeight(x, z, Heightmap.Types.OCEAN_FLOOR_WG, level, randomState);
                if (ground <= seaLevel + 1) continue;

                level.getChunk(x >> 4, z >> 4); // generate just this chunk so the real heightmap exists
                int y = level.getHeight(Heightmap.Types.MOTION_BLOCKING_NO_LEAVES, x, z);
                if (!level.getFluidState(new BlockPos(x, y - 1, z)).isEmpty()) continue; // river/lake on top
                cir.setReturnValue(new BlockPos(x, Math.max(level.getMinBuildHeight() + 1, y), z));
                return;
            }
        }
        // No land found nearby: fall through to the original logic (still patched by the redirect below).
    }

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
