package dev.bankopack.tweaks.world;

import net.minecraft.core.registries.BuiltInRegistries;
import net.minecraft.resources.ResourceLocation;
import net.minecraft.server.level.ServerLevel;
import net.minecraft.world.item.ItemStack;
import net.minecraft.world.level.block.Block;
import net.neoforged.neoforge.common.NeoForge;
import net.neoforged.neoforge.event.level.BlockEvent;

/**
 * MTR (4.1.0-beta.2) node blocks never drop when broken, even though their loot tables say they drop themselves:
 * the node's own break code removes the block before vanilla's drop step. Give the node item back on survival breaks.
 */
public final class MtrNodeDrops {
    private MtrNodeDrops() {}

    public static void register() {
        NeoForge.EVENT_BUS.addListener(BlockEvent.BreakEvent.class, e -> {
            if (e.isCanceled() || e.getPlayer().isCreative() || !(e.getLevel() instanceof ServerLevel level)) return;
            Block block = e.getState().getBlock();
            ResourceLocation id = BuiltInRegistries.BLOCK.getKey(block);
            if (!"mtr".equals(id.getNamespace()) || !id.getPath().contains("node")) return;
            ItemStack drop = new ItemStack(block.asItem());
            if (!drop.isEmpty()) Block.popResource(level, e.getPos(), drop);
        });
    }
}
