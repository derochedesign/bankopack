package dev.bankopack.tweaks.debug;

import com.mojang.brigadier.arguments.IntegerArgumentType;
import com.mojang.brigadier.context.CommandContext;
import net.minecraft.commands.CommandSourceStack;
import net.minecraft.commands.Commands;
import net.minecraft.network.chat.Component;
import net.minecraft.server.level.ServerLevel;
import net.minecraft.world.level.chunk.ChunkGenerator;
import net.minecraft.world.level.levelgen.Heightmap;
import net.minecraft.world.level.levelgen.RandomState;
import net.neoforged.neoforge.event.RegisterCommandsEvent;

/**
 * {@code /bankopack terrainstats <radius> <step>}: samples terrain height on a grid straight from the
 * chunk generator's noise (no chunks are generated) and reports how much of the area is ocean, flat land,
 * hills, highlands and mountains, plus local relief between neighbouring samples. Used to tune Tectonic.
 */
public final class TerrainStatsCommand {
    private static final int[] BANDS = {0, 20, 60, 140, 250}; // metres above sea level: band lower bounds
    private static final String[] BAND_NAMES = {"flat (0-20)", "low hills (20-60)", "hills (60-140)",
                                                "highlands (140-250)", "mountains (250+)"};

    private TerrainStatsCommand() {}

    public static void register(RegisterCommandsEvent event) {
        event.getDispatcher().register(Commands.literal("bankopack")
            .requires(source -> source.hasPermission(2))
            .then(Commands.literal("terrainstats")
                .then(Commands.argument("radius", IntegerArgumentType.integer(256, 50_000))
                    .then(Commands.argument("step", IntegerArgumentType.integer(8, 4096))
                        .executes(TerrainStatsCommand::run)))));
    }

    private static int run(CommandContext<CommandSourceStack> ctx) {
        CommandSourceStack source = ctx.getSource();
        ServerLevel level = source.getLevel();
        int radius = IntegerArgumentType.getInteger(ctx, "radius");
        int step = IntegerArgumentType.getInteger(ctx, "step");
        ChunkGenerator generator = level.getChunkSource().getGenerator();
        RandomState randomState = level.getChunkSource().randomState();
        int sea = generator.getSeaLevel();
        int cx = (int) source.getPosition().x, cz = (int) source.getPosition().z;

        int n = radius * 2 / step + 1;
        int[][] h = new int[n][n];
        long ocean = 0, land = 0;
        long[] bands = new long[BANDS.length];
        int max = Integer.MIN_VALUE;
        for (int i = 0; i < n; i++) {
            for (int j = 0; j < n; j++) {
                int y = generator.getBaseHeight(cx - radius + i * step, cz - radius + j * step,
                    Heightmap.Types.OCEAN_FLOOR_WG, level, randomState);
                h[i][j] = y;
                max = Math.max(max, y);
                if (y <= sea) { ocean++; continue; }
                land++;
                int above = y - sea, band = 0;
                for (int b = 0; b < BANDS.length; b++) if (above >= BANDS[b]) band = b;
                bands[band]++;
            }
        }
        // Local relief: height change between neighbouring land samples (step blocks apart)
        long gentle = 0, moderate = 0, steep = 0, pairs = 0;
        for (int i = 0; i < n; i++) {
            for (int j = 0; j < n; j++) {
                if (h[i][j] <= sea) continue;
                for (int[] d : new int[][]{{1, 0}, {0, 1}}) {
                    int a = i + d[0], b = j + d[1];
                    if (a >= n || b >= n || h[a][b] <= sea) continue;
                    int diff = Math.abs(h[a][b] - h[i][j]);
                    pairs++;
                    if (diff < step / 8) gentle++; else if (diff < step / 2) moderate++; else steep++;
                }
            }
        }
        long total = ocean + land;
        StringBuilder out = new StringBuilder(String.format("terrainstats r=%d step=%d samples=%d sea=%d max=%d | ocean %.1f%%",
            radius, step, total, sea, max, 100.0 * ocean / total));
        for (int b = 0; b < BANDS.length; b++) {
            out.append(String.format(" | %s %.1f%%", BAND_NAMES[b], land == 0 ? 0 : 100.0 * bands[b] / land));
        }
        if (pairs > 0) {
            out.append(String.format(" | relief per %d blocks: gentle %.1f%% moderate %.1f%% steep %.1f%%",
                step, 100.0 * gentle / pairs, 100.0 * moderate / pairs, 100.0 * steep / pairs));
        }
        source.sendSuccess(() -> Component.literal(out.toString()), false);
        return (int) land;
    }
}
