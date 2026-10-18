package dev.bankopack.tweaks.world;

import com.mojang.serialization.Codec;
import com.mojang.serialization.MapCodec;
import com.mojang.serialization.codecs.RecordCodecBuilder;
import net.minecraft.core.Holder;
import net.minecraft.core.HolderSet;
import net.minecraft.world.level.biome.Biome;
import net.neoforged.neoforge.common.world.BiomeModifier;
import net.neoforged.neoforge.common.world.ModifiableBiomeInfo;

/**
 * Scales a biome's creature_spawn_probability: the chance per chunk, at world generation, of placing a group of
 * passive animals. Mod animals (Alex's Mobs etc.) crowd vanilla farm animals out of the same rolls, so more rolls
 * means more of everything. Used by data/bankopack/neoforge/biome_modifier/more_animal_groups.json.
 */
public record CreatureProbabilityModifier(HolderSet<Biome> biomes, float multiplier, float max) implements BiomeModifier {
    public static final MapCodec<CreatureProbabilityModifier> CODEC = RecordCodecBuilder.mapCodec(i -> i.group(
        Biome.LIST_CODEC.fieldOf("biomes").forGetter(CreatureProbabilityModifier::biomes),
        Codec.FLOAT.fieldOf("multiplier").forGetter(CreatureProbabilityModifier::multiplier),
        Codec.FLOAT.optionalFieldOf("max", 0.5F).forGetter(CreatureProbabilityModifier::max)
    ).apply(i, CreatureProbabilityModifier::new));

    @Override
    public void modify(Holder<Biome> biome, Phase phase, ModifiableBiomeInfo.BiomeInfo.Builder builder) {
        if (phase != Phase.MODIFY || !biomes.contains(biome)) return;
        var spawns = builder.getMobSpawnSettings();
        spawns.creatureGenerationProbability(Math.min(max, spawns.getProbability() * multiplier));
    }

    @Override
    public MapCodec<? extends BiomeModifier> codec() {
        return CODEC;
    }
}
