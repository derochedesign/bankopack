package dev.bankopack.tweaks.mixin.client;

import dev.bankopack.tweaks.network.LeavingPayload;
import net.minecraft.client.Minecraft;
import net.minecraft.client.gui.screens.PauseScreen;
import net.minecraft.client.multiplayer.ClientPacketListener;
import org.spongepowered.asm.mixin.Mixin;
import org.spongepowered.asm.mixin.injection.At;
import org.spongepowered.asm.mixin.injection.Inject;
import org.spongepowered.asm.mixin.injection.callback.CallbackInfo;

/** Tell the server we are leaving before mods start their (slow) save-on-disconnect work. */
@Mixin(PauseScreen.class)
public abstract class PauseScreenMixin {
    @Inject(method = "onDisconnect", at = @At("HEAD"))
    private void bankopack$announceLeaving(CallbackInfo ci) {
        ClientPacketListener connection = Minecraft.getInstance().getConnection();
        if (connection != null && connection.hasChannel(LeavingPayload.TYPE)) {
            connection.send(LeavingPayload.INSTANCE);
        }
    }
}
