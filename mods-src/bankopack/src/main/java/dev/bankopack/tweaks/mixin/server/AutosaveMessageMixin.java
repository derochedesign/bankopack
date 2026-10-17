package dev.bankopack.tweaks.mixin.server;

import net.minecraft.ChatFormatting;
import net.minecraft.network.chat.Component;
import net.minecraft.server.MinecraftServer;
import net.minecraft.server.players.PlayerList;
import org.spongepowered.asm.mixin.Mixin;
import org.spongepowered.asm.mixin.Shadow;
import org.spongepowered.asm.mixin.Unique;
import org.spongepowered.asm.mixin.injection.At;
import org.spongepowered.asm.mixin.injection.Inject;
import org.spongepowered.asm.mixin.injection.callback.CallbackInfo;

import java.util.function.BooleanSupplier;

/**
 * Tells players in chat when the periodic autosave runs (it causes a short lag spike), and how long it took.
 * Only the autosave in {@code tickServer} is hooked; /save-all and shutdown saves stay silent.
 */
@Mixin(MinecraftServer.class)
public abstract class AutosaveMessageMixin {
    @Unique private long bankopack$autosaveStart;

    @Shadow public abstract PlayerList getPlayerList();

    @Inject(method = "tickServer", at = @At(value = "INVOKE",
            target = "Lnet/minecraft/server/MinecraftServer;saveEverything(ZZZ)Z"))
    private void bankopack$beforeAutosave(BooleanSupplier hasTimeLeft, CallbackInfo ci) {
        bankopack$autosaveStart = System.nanoTime();
        bankopack$broadcast("Autosaving the world...");
    }

    @Inject(method = "tickServer", at = @At(value = "INVOKE",
            target = "Lnet/minecraft/server/MinecraftServer;saveEverything(ZZZ)Z", shift = At.Shift.AFTER))
    private void bankopack$afterAutosave(BooleanSupplier hasTimeLeft, CallbackInfo ci) {
        double seconds = (System.nanoTime() - bankopack$autosaveStart) / 1e9;
        bankopack$broadcast(String.format("Autosave complete (%.1fs)", seconds));
    }

    @Unique
    private void bankopack$broadcast(String text) {
        PlayerList players = getPlayerList();
        if (players == null || players.getPlayerCount() == 0) return;
        players.broadcastSystemMessage(Component.literal(text).withStyle(ChatFormatting.GRAY, ChatFormatting.ITALIC), false);
    }
}
