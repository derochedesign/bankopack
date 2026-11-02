package dev.bankopack.tweaks.world;

import net.minecraft.core.registries.BuiltInRegistries;
import net.minecraft.resources.ResourceLocation;
import net.minecraft.world.entity.ai.attributes.AttributeInstance;
import net.minecraft.world.entity.ai.attributes.Attributes;
import net.neoforged.neoforge.common.NeoForge;
import net.neoforged.neoforge.event.entity.EntityJoinLevelEvent;

/**
 * Lowers the Iron's Spells Ancient Knight (citadel_keeper) base attack damage from 10 to 8. With its 10-damage
 * flamberge and Hard difficulty it was two-shotting players in full netherite-tier armor. Applied on join rather
 * than as an attribute default so knights already saved in the world (citadels) are nerfed too.
 */
public final class AncientKnightNerf {
    private static final ResourceLocation KEEPER = ResourceLocation.fromNamespaceAndPath("irons_spellbooks", "citadel_keeper");
    private static final double ORIGINAL = 10.0;
    private static final double NERFED = 8.0;

    private AncientKnightNerf() {}

    public static void register() {
        NeoForge.EVENT_BUS.addListener(EntityJoinLevelEvent.class, e -> {
            if (e.getLevel().isClientSide()) return;
            if (!KEEPER.equals(BuiltInRegistries.ENTITY_TYPE.getKey(e.getEntity().getType()))) return;
            if (!(e.getEntity() instanceof net.minecraft.world.entity.LivingEntity living)) return;
            AttributeInstance damage = living.getAttribute(Attributes.ATTACK_DAMAGE);
            if (damage != null && damage.getBaseValue() == ORIGINAL) damage.setBaseValue(NERFED);
        });
    }
}
