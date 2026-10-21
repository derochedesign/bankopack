package dev.bankopack.tweaks.world;

import java.util.List;
import net.minecraft.nbt.CompoundTag;
import net.neoforged.neoforge.common.NeoForge;
import net.neoforged.neoforge.event.entity.player.PlayerEvent;

/**
 * Some mods store "already done this" flags in a player's persistent data, which NeoForge does not copy to the
 * respawned player on death (only its PlayerPersisted sub-tag survives). Mama's Herbs and Harvest stores
 * "herbsandharvest_book_given" there, so after every death the next login hands out another Homesteader's
 * Handbook. Carry these flags over on death.
 */
public final class KeepModFlagsOnDeath {
    private static final List<String> FLAGS = List.of("herbsandharvest_book_given");

    private KeepModFlagsOnDeath() {}

    public static void register() {
        NeoForge.EVENT_BUS.addListener(PlayerEvent.Clone.class, e -> {
            if (!e.isWasDeath()) return;
            CompoundTag from = e.getOriginal().getPersistentData();
            CompoundTag to = e.getEntity().getPersistentData();
            for (String flag : FLAGS) {
                if (from.contains(flag) && !to.contains(flag)) to.put(flag, from.get(flag).copy());
            }
        });
    }
}
