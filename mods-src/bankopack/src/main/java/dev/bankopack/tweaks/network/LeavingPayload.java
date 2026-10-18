package dev.bankopack.tweaks.network;

import dev.bankopack.tweaks.BankopackTweaks;
import dev.bankopack.tweaks.world.JoinProtection;
import io.netty.buffer.ByteBuf;
import net.minecraft.network.codec.StreamCodec;
import net.minecraft.network.protocol.common.custom.CustomPacketPayload;
import net.minecraft.resources.ResourceLocation;
import net.minecraft.server.level.ServerPlayer;
import net.neoforged.neoforge.network.event.RegisterPayloadHandlersEvent;

/**
 * Sent by the client the moment the player clicks Disconnect. With this many mods, the client spends a few
 * seconds saving before the connection actually closes, and the player could be killed in that time. The
 * server makes them immune to damage until they are gone (see {@link JoinProtection#guardLeaving}).
 */
public record LeavingPayload() implements CustomPacketPayload {
    public static final LeavingPayload INSTANCE = new LeavingPayload();
    public static final Type<LeavingPayload> TYPE =
        new Type<>(ResourceLocation.fromNamespaceAndPath(BankopackTweaks.MODID, "leaving"));
    public static final StreamCodec<ByteBuf, LeavingPayload> CODEC = StreamCodec.unit(INSTANCE);

    @Override
    public Type<? extends CustomPacketPayload> type() {
        return TYPE;
    }

    public static void register(RegisterPayloadHandlersEvent event) {
        // Optional, so a client and server on different Bankopack Tweaks versions can still connect.
        event.registrar("1").optional().playToServer(TYPE, CODEC, (payload, context) -> {
            context.enqueueWork(() -> {
                if (context.player() instanceof ServerPlayer p) JoinProtection.guardLeaving(p);
            });
        });
    }
}
