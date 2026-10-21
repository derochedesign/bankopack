package dev.bankopack.tweaks.world;

import com.google.gson.JsonElement;
import com.google.gson.JsonParser;
import dev.bankopack.tweaks.BankopackTweaks;
import java.io.Reader;
import java.util.HashMap;
import java.util.List;
import java.util.Map;
import java.util.UUID;
import net.minecraft.ChatFormatting;
import net.minecraft.core.registries.BuiltInRegistries;
import net.minecraft.network.chat.Component;
import net.minecraft.resources.ResourceLocation;
import net.minecraft.server.MinecraftServer;
import net.minecraft.server.level.ServerLevel;
import net.minecraft.server.level.ServerPlayer;
import net.minecraft.world.entity.Entity;
import net.minecraft.world.entity.player.Player;
import net.neoforged.neoforge.common.NeoForge;
import net.neoforged.neoforge.event.OnDatapackSyncEvent;
import net.neoforged.neoforge.event.entity.EntityJoinLevelEvent;
import net.neoforged.neoforge.event.server.ServerStartedEvent;

/**
 * Tells a player in chat when a Radical Cobblemon Trainers story trainer (one tied to a series) spawns for them,
 * with its name, distance and direction. Series membership comes from RCT's own spawn data
 * (data/rctmod/mobs/trainers/single/&lt;trainer id&gt;.json, or groups/&lt;prefix&gt;.json for trainer ids that start with it),
 * read straight from the loaded datapacks so it follows our overrides and any RCT update.
 */
public final class StoryTrainerAnnouncer {
    private static final ResourceLocation TRAINER = ResourceLocation.fromNamespaceAndPath("rctmod", "trainer");
    private static final double FALLBACK_RADIUS = 96;

    private static Map<String, String> singleSeries = Map.of();
    private static Map<String, String> groupSeries = Map.of();

    private StoryTrainerAnnouncer() {}

    public static void register() {
        NeoForge.EVENT_BUS.addListener(ServerStartedEvent.class, e -> load(e.getServer()));
        NeoForge.EVENT_BUS.addListener(OnDatapackSyncEvent.class, e -> {
            if (e.getPlayer() == null) load(e.getPlayerList().getServer());
        });
        NeoForge.EVENT_BUS.addListener(EntityJoinLevelEvent.class, e -> {
            if (e.loadedFromDisk() || !(e.getLevel() instanceof ServerLevel level)) return;
            Entity entity = e.getEntity();
            if (!TRAINER.equals(BuiltInRegistries.ENTITY_TYPE.getKey(entity.getType()))) return;
            // RCT may set the trainer id and origin player right after adding the entity, so look next tick.
            level.getServer().execute(() -> announce(level, entity));
        });
    }

    private static void load(MinecraftServer server) {
        Map<String, String> singles = new HashMap<>();
        Map<String, String> groups = new HashMap<>();
        server.getResourceManager().listResources("mobs/trainers", id -> id.getPath().endsWith(".json")).forEach((id, res) -> {
            if (!"rctmod".equals(id.getNamespace())) return;
            String path = id.getPath();
            String name = path.substring(path.lastIndexOf('/') + 1, path.length() - ".json".length());
            try (Reader reader = res.openAsReader()) {
                JsonElement series = JsonParser.parseReader(reader).getAsJsonObject().get("series");
                if (series == null || !series.isJsonArray() || series.getAsJsonArray().isEmpty()) return;
                String first = series.getAsJsonArray().get(0).getAsString();
                if (path.contains("/single/")) singles.put(name, first);
                else if (path.contains("/groups/")) groups.put(name, first);
            } catch (Exception ex) {
                BankopackTweaks.LOGGER.debug("Could not read RCT spawn data {}", id, ex);
            }
        });
        singleSeries = singles;
        groupSeries = groups;
        BankopackTweaks.LOGGER.info("Story trainer announcements: {} single and {} group series trainers", singles.size(), groups.size());
    }

    private static String seriesOf(String trainerId) {
        String series = singleSeries.get(trainerId);
        if (series != null) return series;
        String best = null;
        int bestLength = -1;
        for (Map.Entry<String, String> group : groupSeries.entrySet()) {
            String prefix = group.getKey();
            if (prefix.length() > bestLength && (trainerId.equals(prefix) || trainerId.startsWith(prefix + "_"))) {
                best = group.getValue();
                bestLength = prefix.length();
            }
        }
        return best;
    }

    private static void announce(ServerLevel level, Entity trainer) {
        if (trainer.isRemoved()) return;
        Object id = call(trainer, "getTrainerId");
        if (!(id instanceof String trainerId) || seriesOf(trainerId) == null) return;

        List<? extends Player> targets;
        Object origin = call(trainer, "getOriginPlayer");
        if (origin instanceof UUID uuid) origin = level.getServer().getPlayerList().getPlayer(uuid);
        if (origin instanceof ServerPlayer player && player.level() == level) {
            targets = List.of(player);
        } else {
            targets = level.getEntitiesOfClass(Player.class, trainer.getBoundingBox().inflate(FALLBACK_RADIUS));
        }
        for (Player player : targets) {
            double dx = trainer.getX() - player.getX(), dz = trainer.getZ() - player.getZ();
            int distance = (int) Math.round(Math.sqrt(dx * dx + dz * dz));
            player.sendSystemMessage(Component.literal("Story trainer nearby: ").withStyle(ChatFormatting.GOLD)
                .append(trainer.getDisplayName().copy().withStyle(ChatFormatting.YELLOW))
                .append(Component.literal(" (" + distance + " blocks " + direction(dx, dz)
                    + height(trainer.getY() - player.getY()) + ")").withStyle(ChatFormatting.GRAY)));
        }
    }

    /** Compass direction from a horizontal offset (Minecraft: -Z is north, +X is east). */
    private static String direction(double dx, double dz) {
        String[] names = {"S", "SW", "W", "NW", "N", "NE", "E", "SE"};
        double angle = Math.toDegrees(Math.atan2(-dx, dz));
        int index = (int) Math.round(((angle % 360) + 360) % 360 / 45.0) % 8;
        return names[index];
    }

    /** Trainers often spawn in caves below the player; say so, rounded to 5 blocks. Small differences are left out. */
    private static String height(double dy) {
        int blocks = (int) Math.round(Math.abs(dy) / 5) * 5;
        if (blocks < 5) return "";
        return ", ~" + blocks + (dy > 0 ? " above" : " below");
    }

    private static Object call(Object target, String method) {
        try {
            return target.getClass().getMethod(method).invoke(target);
        } catch (ReflectiveOperationException ex) {
            return null;
        }
    }
}
