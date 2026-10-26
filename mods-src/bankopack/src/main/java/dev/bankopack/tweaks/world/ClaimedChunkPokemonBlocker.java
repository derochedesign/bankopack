package dev.bankopack.tweaks.world;

import dev.bankopack.tweaks.BankopackTweaks;
import dev.ftb.mods.ftbchunks.api.FTBChunksAPI;
import dev.ftb.mods.ftblibrary.math.ChunkDimPos;
import net.minecraft.core.registries.BuiltInRegistries;
import net.minecraft.resources.ResourceLocation;
import net.minecraft.server.level.ServerLevel;
import net.minecraft.world.entity.Entity;
import net.neoforged.bus.api.EventPriority;
import net.neoforged.neoforge.common.NeoForge;
import net.neoforged.neoforge.event.entity.EntityJoinLevelEvent;

/**
 * Stops Cobblemon's ambient spawner (the one that spawns around players) from putting wild Pokémon in FTB claimed
 * chunks. Fishing and Poké Snack spawns use other spawners and still work in claims; sent-out, trainer and saved
 * Pokémon have no player-spawner cause and are untouched. Runs at HIGH priority so ShinyAnnouncer, which ignores
 * cancelled events, never announces a blocked spawn.
 */
public final class ClaimedChunkPokemonBlocker {
    private static final ResourceLocation POKEMON = ResourceLocation.fromNamespaceAndPath("cobblemon", "pokemon");

    private static Class<?> playerSpawner;

    private ClaimedChunkPokemonBlocker() {}

    public static void register() {
        try {
            playerSpawner = Class.forName("com.cobblemon.mod.common.api.spawning.spawner.PlayerSpawner");
        } catch (ClassNotFoundException ex) {
            BankopackTweaks.LOGGER.warn("Cobblemon PlayerSpawner not found; Pokémon will still spawn in claimed chunks");
            return;
        }
        NeoForge.EVENT_BUS.addListener(EventPriority.HIGH, EntityJoinLevelEvent.class, e -> {
            if (e.loadedFromDisk() || !(e.getLevel() instanceof ServerLevel level)) return;
            Entity entity = e.getEntity();
            if (!POKEMON.equals(BuiltInRegistries.ENTITY_TYPE.getKey(entity.getType()))) return;
            Object cause = StoryTrainerAnnouncer.call(entity, "getSpawnCause");
            if (cause == null || !playerSpawner.isInstance(StoryTrainerAnnouncer.call(cause, "getSpawner"))) return;
            if (!FTBChunksAPI.api().isManagerLoaded()) return;
            if (FTBChunksAPI.api().getManager().getChunk(new ChunkDimPos(level, entity.blockPosition())) != null) {
                e.setCanceled(true);
            }
        });
    }
}
