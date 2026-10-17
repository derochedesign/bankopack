package dev.bankopack.tweaks.mixin.server;

import net.minecraft.core.registries.BuiltInRegistries;
import net.minecraft.resources.ResourceLocation;
import net.minecraft.world.entity.Entity;
import net.minecraft.world.entity.MobCategory;
import net.minecraft.world.level.NaturalSpawner;
import org.spongepowered.asm.mixin.Mixin;
import org.spongepowered.asm.mixin.Unique;
import org.spongepowered.asm.mixin.injection.At;
import org.spongepowered.asm.mixin.injection.Redirect;

/**
 * Cobblemon registers wild Pokemon as {@link MobCategory#CREATURE}, so they fill the vanilla passive-mob cap
 * and cows, sheep, pigs etc. stop spawning. Cobblemon has its own cap (pokemonPerChunk), so leave Pokemon out
 * of the vanilla count. Hostile mobs were never affected.
 */
@Mixin(NaturalSpawner.class)
public abstract class NaturalSpawnerMixin {
    @Unique private static final ResourceLocation BANKOPACK$POKEMON = ResourceLocation.fromNamespaceAndPath("cobblemon", "pokemon");

    @Redirect(method = "createState", at = @At(value = "INVOKE",
            target = "Lnet/minecraft/world/entity/Entity;getClassification(Z)Lnet/minecraft/world/entity/MobCategory;"))
    private static MobCategory bankopack$ignorePokemon(Entity entity, boolean forSpawnCount) {
        if (BANKOPACK$POKEMON.equals(BuiltInRegistries.ENTITY_TYPE.getKey(entity.getType()))) return MobCategory.MISC;
        return entity.getClassification(forSpawnCount);
    }
}
