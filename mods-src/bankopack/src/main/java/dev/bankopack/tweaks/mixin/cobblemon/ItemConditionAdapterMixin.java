package dev.bankopack.tweaks.mixin.cobblemon;

import com.google.gson.JsonDeserializationContext;
import com.google.gson.JsonElement;
import com.google.gson.JsonObject;
import java.lang.reflect.Type;
import net.minecraft.advancements.critereon.ItemPredicate;
import org.spongepowered.asm.mixin.Mixin;
import org.spongepowered.asm.mixin.Shadow;
import org.spongepowered.asm.mixin.injection.At;
import org.spongepowered.asm.mixin.injection.Inject;
import org.spongepowered.asm.mixin.injection.callback.CallbackInfoReturnable;

/**
 * Cobblemon 1.8.1 sends interaction requirements (e.g. "owner holds #c:tools/brush" on 136 brushing interactions)
 * to the client as JSON, and the client decodes {"items": "#c:tools/brush"} with the vanilla ItemPredicate codec.
 * Without registry context (first join of a game session) that codec cannot read a tag or item id, decoding
 * throws, and the player is disconnected; the second join works because registry data is then cached.
 * Handle the simple {"items": "&lt;id or #tag&gt;"} shape the same way Cobblemon's own legacy string form does,
 * which needs no registry lookup.
 */
@Mixin(targets = "com.cobblemon.mod.common.pokemon.evolution.adapters.LegacyItemConditionWrapperAdapter", remap = false)
public abstract class ItemConditionAdapterMixin {
    @Shadow
    private ItemPredicate.Builder createBuilderForItem(String raw) {
        throw new AssertionError();
    }

    @Inject(method = "deserialize(Lcom/google/gson/JsonElement;Ljava/lang/reflect/Type;Lcom/google/gson/JsonDeserializationContext;)Lnet/minecraft/advancements/critereon/ItemPredicate;",
            at = @At("HEAD"), cancellable = true)
    private void bankopack$simpleItemsField(JsonElement json, Type type, JsonDeserializationContext context,
                                             CallbackInfoReturnable<ItemPredicate> cir) {
        if (!json.isJsonObject()) return;
        JsonObject obj = json.getAsJsonObject();
        if (obj.size() != 1 || !obj.has("items")) return;
        JsonElement items = obj.get("items");
        if (items.isJsonPrimitive() && items.getAsJsonPrimitive().isString()) {
            cir.setReturnValue(createBuilderForItem(items.getAsString()).build());
        }
    }
}
