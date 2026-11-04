package dev.bankopack.tweaks.world;

import java.util.Collection;
import dev.bankopack.tweaks.BankopackTweaks;
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
 * Tells nearby players in chat when a wild legendary, mythical, Ultra Beast or Paradox Pokémon spawns, with its
 * distance, direction and height, like {@link ShinyAnnouncer}. Fresh spawns only, so a legendary isn't re-announced
 * each time its chunk reloads.
 */
public final class LegendaryAnnouncer {
    private static final ResourceLocation POKEMON = ResourceLocation.fromNamespaceAndPath("cobblemon", "pokemon");
    private static final double RADIUS = 96;
    private static final String[][] KINDS = {
        {"legendary", "legendary"}, {"mythical", "mythical"}, {"ultra_beast", "Ultra Beast"}, {"paradox", "Paradox"}};

    private LegendaryAnnouncer() {}

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
        if (pokemon == null || !Boolean.TRUE.equals(StoryTrainerAnnouncer.call(pokemon, "isWild"))) return;
        String kind = kind(StoryTrainerAnnouncer.call(StoryTrainerAnnouncer.call(pokemon, "getSpecies"), "getLabels"));
        if (kind == null) return;

        Component headline = Component.literal("🌟 A wild " + kind + " ").withStyle(ChatFormatting.LIGHT_PURPLE)
            .append(entity.getDisplayName().copy().withStyle(ChatFormatting.GOLD, ChatFormatting.BOLD))
            .append(Component.literal(" spawned nearby!").withStyle(ChatFormatting.LIGHT_PURPLE));
        // Logged so the spawn rate can be tuned from the server log.
        BankopackTweaks.LOGGER.info("Wild {} {} spawned in {} at {}", kind, entity.getDisplayName().getString(),
            level.dimension().location(), entity.blockPosition());
        for (Player player : level.getEntitiesOfClass(Player.class, entity.getBoundingBox().inflate(RADIUS))) {
            double dx = entity.getX() - player.getX(), dz = entity.getZ() - player.getZ();
            int distance = (int) Math.round(Math.sqrt(dx * dx + dz * dz));
            player.sendSystemMessage(headline.copy().append(Component.literal(" (" + distance + " blocks "
                + StoryTrainerAnnouncer.direction(dx, dz)
                + StoryTrainerAnnouncer.height(entity.getY() - player.getY()) + ")").withStyle(ChatFormatting.GRAY)));
        }
    }

    private static String kind(Object labels) {
        if (!(labels instanceof Collection<?> set)) return null;
        for (String[] kind : KINDS) {
            if (set.contains(kind[0])) return kind[1];
        }
        return null;
    }
}
