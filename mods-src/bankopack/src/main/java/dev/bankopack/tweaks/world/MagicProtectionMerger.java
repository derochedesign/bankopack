package dev.bankopack.tweaks.world;

import java.util.Optional;
import net.minecraft.core.Holder;
import net.minecraft.core.Registry;
import net.minecraft.core.component.DataComponentType;
import net.minecraft.core.component.DataComponents;
import net.minecraft.core.registries.Registries;
import net.minecraft.resources.ResourceKey;
import net.minecraft.resources.ResourceLocation;
import net.minecraft.server.level.ServerPlayer;
import net.minecraft.world.Container;
import net.minecraft.world.inventory.Slot;
import net.minecraft.world.item.ItemStack;
import net.minecraft.world.item.enchantment.Enchantment;
import net.minecraft.world.item.enchantment.ItemEnchantments;
import net.neoforged.neoforge.common.NeoForge;
import net.neoforged.neoforge.event.entity.player.PlayerContainerEvent;
import net.neoforged.neoforge.event.tick.PlayerTickEvent;

/**
 * Spell Power and ReArm both add an armor enchantment called "Magic Protection". ReArm's covers every magic damage
 * type Spell Power's does and more, so Spell Power's is dropped from tables and loot (see the enchantment tag
 * removals in data/minecraft/tags/enchantment) and any copies already in the world are swapped for ReArm's at the same
 * level. Items are converted as they pass through a player's inventory, ender chest, or any container they open.
 */
public final class MagicProtectionMerger {
    private static final ResourceKey<Enchantment> SPELL_POWER = ResourceKey.create(Registries.ENCHANTMENT,
        ResourceLocation.fromNamespaceAndPath("spell_power", "magic_protection"));
    private static final ResourceKey<Enchantment> REARM = ResourceKey.create(Registries.ENCHANTMENT,
        ResourceLocation.fromNamespaceAndPath("rearm", "magic_protection"));
    private static final int SCAN_INTERVAL = 100;

    private MagicProtectionMerger() {}

    public static void register() {
        NeoForge.EVENT_BUS.addListener(PlayerTickEvent.Post.class, e -> {
            if (!(e.getEntity() instanceof ServerPlayer player) || player.tickCount % SCAN_INTERVAL != 0) return;
            convertAll(player, player.getInventory());
            convertAll(player, player.getEnderChestInventory());
        });
        NeoForge.EVENT_BUS.addListener(PlayerContainerEvent.Open.class, e -> {
            if (!(e.getEntity() instanceof ServerPlayer player)) return;
            for (Slot slot : e.getContainer().slots) {
                if (convert(player, slot.getItem())) slot.setChanged();
            }
        });
    }

    private static void convertAll(ServerPlayer player, Container container) {
        boolean changed = false;
        for (int i = 0; i < container.getContainerSize(); i++) changed |= convert(player, container.getItem(i));
        if (changed) container.setChanged();
    }

    private static boolean convert(ServerPlayer player, ItemStack stack) {
        if (stack.isEmpty()) return false;
        Registry<Enchantment> registry = player.registryAccess().registryOrThrow(Registries.ENCHANTMENT);
        Optional<Holder.Reference<Enchantment>> from = registry.getHolder(SPELL_POWER);
        Optional<Holder.Reference<Enchantment>> to = registry.getHolder(REARM);
        if (from.isEmpty() || to.isEmpty()) return false;
        return convert(stack, DataComponents.ENCHANTMENTS, from.get(), to.get())
            | convert(stack, DataComponents.STORED_ENCHANTMENTS, from.get(), to.get());
    }

    private static boolean convert(ItemStack stack, DataComponentType<ItemEnchantments> type,
                                   Holder<Enchantment> from, Holder<Enchantment> to) {
        ItemEnchantments enchantments = stack.get(type);
        if (enchantments == null) return false;
        int level = enchantments.getLevel(from);
        if (level <= 0) return false;
        ItemEnchantments.Mutable mutable = new ItemEnchantments.Mutable(enchantments);
        mutable.set(from, 0);
        mutable.set(to, Math.max(level, enchantments.getLevel(to)));
        stack.set(type, mutable.toImmutable());
        return true;
    }
}
