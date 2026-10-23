package dev.bankopack.tweaks.world;

import net.minecraft.ChatFormatting;
import net.minecraft.core.registries.BuiltInRegistries;
import net.minecraft.network.chat.Component;
import net.minecraft.resources.ResourceLocation;
import net.minecraft.server.level.ServerLevel;
import net.minecraft.world.entity.Entity;
import net.minecraft.world.entity.player.Player;
import net.neoforged.neoforge.common.NeoForge;
import net.neoforged.neoforge.event.entity.EntityJoinLevelEvent;

/**
 * Tells nearby players in chat when a wild shiny Cobblemon spawns, with its name, distance, direction and height.
 * Cobblemon itself only plays sparkles within 24 blocks, which is easy to miss. Fresh spawns only, so a shiny
 * isn't announced again each time its chunk reloads, and player-owned Pokémon being sent out are ignored.
 */
public final class ShinyAnnouncer {
    private static final ResourceLocation POKEMON = ResourceLocation.fromNamespaceAndPath("cobblemon", "pokemon");
    private static final double RADIUS = 96;

    private ShinyAnnouncer() {}

    public static void register() {
        NeoForge.EVENT_BUS.addListener(EntityJoinLevelEvent.class, e -> {
            if (e.loadedFromDisk() || !(e.getLevel() instanceof ServerLevel level)) return;
            Entity entity = e.getEntity();
            if (!POKEMON.equals(BuiltInRegistries.ENTITY_TYPE.getKey(entity.getType()))) return;
            // Look next tick, once the spawner has finished setting the Pokémon up.
            level.getServer().execute(() -> announce(level, entity));
        });
    }

    private static void announce(ServerLevel level, Entity entity) {
        if (entity.isRemoved()) return;
        Object pokemon = StoryTrainerAnnouncer.call(entity, "getPokemon");
        if (pokemon == null || !Boolean.TRUE.equals(StoryTrainerAnnouncer.call(pokemon, "getShiny"))
                || !Boolean.TRUE.equals(StoryTrainerAnnouncer.call(pokemon, "isWild"))) {
            return;
        }
        for (Player player : level.getEntitiesOfClass(Player.class, entity.getBoundingBox().inflate(RADIUS))) {
            double dx = entity.getX() - player.getX(), dz = entity.getZ() - player.getZ();
            int distance = (int) Math.round(Math.sqrt(dx * dx + dz * dz));
            player.sendSystemMessage(Component.literal("✨ A shiny ").withStyle(ChatFormatting.AQUA)
                .append(entity.getDisplayName().copy().withStyle(ChatFormatting.YELLOW))
                .append(Component.literal(" spawned nearby!").withStyle(ChatFormatting.AQUA))
                .append(Component.literal(" (" + distance + " blocks " + StoryTrainerAnnouncer.direction(dx, dz)
                    + StoryTrainerAnnouncer.height(entity.getY() - player.getY()) + ")").withStyle(ChatFormatting.GRAY)));
        }
    }
}
