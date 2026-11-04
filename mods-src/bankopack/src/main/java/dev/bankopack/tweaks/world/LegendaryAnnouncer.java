package dev.bankopack.tweaks.world;

import java.util.Collection;
import java.util.Comparator;
import dev.bankopack.tweaks.BankopackTweaks;
import net.minecraft.ChatFormatting;
import net.minecraft.core.registries.BuiltInRegistries;
import net.minecraft.network.chat.Component;
import net.minecraft.resources.ResourceLocation;
import net.minecraft.server.level.ServerLevel;
import net.minecraft.server.level.ServerPlayer;
import net.minecraft.world.entity.Entity;
import net.neoforged.neoforge.common.NeoForge;
import net.neoforged.neoforge.event.entity.EntityJoinLevelEvent;

/**
 * Announces wild legendary, mythical, Ultra Beast and Paradox Pokémon to the whole server when they spawn, naming the
 * nearest player and the dimension, and gives players in that dimension the distance and direction. Fresh spawns
 * only, like {@link ShinyAnnouncer}, so a legendary isn't re-announced each time its chunk reloads.
 */
public final class LegendaryAnnouncer {
    private static final ResourceLocation POKEMON = ResourceLocation.fromNamespaceAndPath("cobblemon", "pokemon");
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

        ServerPlayer nearest = level.players().stream()
            .min(Comparator.comparingDouble(p -> p.distanceToSqr(entity))).orElse(null);
        Component headline = Component.literal("🌟 A wild " + kind + " ").withStyle(ChatFormatting.LIGHT_PURPLE)
            .append(entity.getDisplayName().copy().withStyle(ChatFormatting.GOLD, ChatFormatting.BOLD))
            .append(Component.literal(" appeared" + (nearest != null ? " near " + nearest.getGameProfile().getName() : "")
                + " in " + dimensionName(level) + "!").withStyle(ChatFormatting.LIGHT_PURPLE));
        BankopackTweaks.LOGGER.info("{} at {}", headline.getString(), entity.blockPosition());
        for (ServerPlayer player : level.getServer().getPlayerList().getPlayers()) {
            Component message = headline;
            if (player.level() == level) {
                double dx = entity.getX() - player.getX(), dz = entity.getZ() - player.getZ();
                int distance = (int) Math.round(Math.sqrt(dx * dx + dz * dz));
                message = headline.copy().append(Component.literal(" (" + distance + " blocks "
                    + StoryTrainerAnnouncer.direction(dx, dz)
                    + StoryTrainerAnnouncer.height(entity.getY() - player.getY()) + ")").withStyle(ChatFormatting.GRAY));
            }
            player.sendSystemMessage(message);
        }
    }

    private static String kind(Object labels) {
        if (!(labels instanceof Collection<?> set)) return null;
        for (String[] kind : KINDS) {
            if (set.contains(kind[0])) return kind[1];
        }
        return null;
    }

    private static String dimensionName(ServerLevel level) {
        ResourceLocation id = level.dimension().location();
        return switch (id.toString()) {
            case "minecraft:overworld" -> "the Overworld";
            case "minecraft:the_nether" -> "the Nether";
            case "minecraft:the_end" -> "the End";
            case "aether:the_aether" -> "the Aether";
            case "eternal_starlight:starlight" -> "Eternal Starlight";
            case "twilightforest:twilight_forest" -> "the Twilight Forest";
            case "deeperdarker:otherside" -> "the Otherside";
            default -> id.getPath().replace('_', ' ');
        };
    }
}
