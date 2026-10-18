package dev.bankopack.tweaks.world;

import java.util.HashMap;
import java.util.Map;
import java.util.UUID;
import net.minecraft.ChatFormatting;
import net.minecraft.network.chat.Component;
import net.minecraft.server.level.ServerPlayer;
import net.minecraft.world.phys.Vec3;
import net.neoforged.neoforge.common.NeoForge;
import net.neoforged.neoforge.event.entity.living.LivingIncomingDamageEvent;
import net.neoforged.neoforge.event.entity.player.PlayerEvent;
import net.neoforged.neoforge.event.entity.player.PlayerInteractEvent;
import net.neoforged.neoforge.event.tick.PlayerTickEvent;

/**
 * Players spawn into the world long before this pack finishes loading on their screen, and vanilla only gives
 * 3 seconds of spawn protection. Make players immune to damage after joining or changing dimension until they
 * first move or interact (the client can't do either while still loading), with a hard cap so it can't be abused.
 */
public final class JoinProtection {
    private static final int MAX_TICKS = 20 * 120;
    private static final double MOVE_DISTANCE_SQR = 0.5 * 0.5;

    private record Guard(Vec3 start, int ticks) {}

    private static final Map<UUID, Guard> GUARDED = new HashMap<>();
    /** Players who clicked Disconnect, with ticks left before protection lapses (in case they never leave). */
    private static final Map<UUID, Integer> LEAVING = new HashMap<>();
    private static final int LEAVING_MAX_TICKS = 20 * 30;

    private JoinProtection() {}

    public static void register() {
        NeoForge.EVENT_BUS.addListener(PlayerEvent.PlayerLoggedInEvent.class, e -> guard(e.getEntity()));
        NeoForge.EVENT_BUS.addListener(PlayerEvent.PlayerChangedDimensionEvent.class, e -> guard(e.getEntity()));
        NeoForge.EVENT_BUS.addListener(PlayerEvent.PlayerLoggedOutEvent.class, e -> {
            GUARDED.remove(e.getEntity().getUUID());
            LEAVING.remove(e.getEntity().getUUID());
        });
        NeoForge.EVENT_BUS.addListener(LivingIncomingDamageEvent.class, e -> {
            if (e.getEntity() instanceof ServerPlayer p && (GUARDED.containsKey(p.getUUID()) || LEAVING.containsKey(p.getUUID()))) {
                e.setCanceled(true);
            }
        });
        NeoForge.EVENT_BUS.addListener(PlayerTickEvent.Post.class, e -> {
            if (!(e.getEntity() instanceof ServerPlayer p)) return;
            LEAVING.computeIfPresent(p.getUUID(), (id, left) -> left > 1 ? left - 1 : null);
            Guard g = GUARDED.get(p.getUUID());
            if (g == null) return;
            if (p.position().distanceToSqr(g.start()) > MOVE_DISTANCE_SQR || g.ticks() >= MAX_TICKS) {
                release(p);
            } else {
                GUARDED.put(p.getUUID(), new Guard(g.start(), g.ticks() + 1));
            }
        });
        // The bus rejects listeners on abstract events, so register each concrete interaction.
        NeoForge.EVENT_BUS.addListener(PlayerInteractEvent.RightClickBlock.class, e -> releaseIfServer(e.getEntity()));
        NeoForge.EVENT_BUS.addListener(PlayerInteractEvent.RightClickItem.class, e -> releaseIfServer(e.getEntity()));
        NeoForge.EVENT_BUS.addListener(PlayerInteractEvent.LeftClickBlock.class, e -> releaseIfServer(e.getEntity()));
        NeoForge.EVENT_BUS.addListener(PlayerInteractEvent.EntityInteract.class, e -> releaseIfServer(e.getEntity()));
        NeoForge.EVENT_BUS.addListener(net.neoforged.neoforge.event.entity.player.AttackEntityEvent.class, e -> {
            releaseIfServer(e.getEntity());
        });
    }

    private static void releaseIfServer(net.minecraft.world.entity.player.Player player) {
        if (player instanceof ServerPlayer p) release(p);
    }

    /** Called when the client says it clicked Disconnect; lasts until logout or 30 seconds. */
    public static void guardLeaving(ServerPlayer p) {
        LEAVING.put(p.getUUID(), LEAVING_MAX_TICKS);
    }

    private static void guard(net.minecraft.world.entity.player.Player player) {
        if (player instanceof ServerPlayer p) GUARDED.put(p.getUUID(), new Guard(p.position(), 0));
    }

    private static void release(ServerPlayer p) {
        if (GUARDED.remove(p.getUUID()) != null) {
            p.displayClientMessage(Component.literal("Spawn protection off").withStyle(ChatFormatting.GRAY), true);
        }
    }
}
