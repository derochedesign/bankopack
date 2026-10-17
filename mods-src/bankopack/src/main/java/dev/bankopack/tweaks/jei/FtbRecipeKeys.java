package dev.bankopack.tweaks.jei;

import com.mojang.blaze3d.platform.InputConstants;
import java.util.Optional;
import mezz.jei.api.recipe.RecipeIngredientRole;
import mezz.jei.api.runtime.IClickableIngredient;
import mezz.jei.api.runtime.IJeiRuntime;
import net.minecraft.client.KeyMapping;
import net.minecraft.client.Minecraft;
import net.minecraft.client.gui.screens.Screen;
import net.neoforged.neoforge.client.event.ScreenEvent;

/**
 * JEI's Show Recipe / Show Uses keys (R / U by default) do nothing in FTB screens such as the quest book,
 * even though FTB Library tells JEI which item is under the mouse there. Handle the keys ourselves: ask JEI
 * for the ingredient under the mouse and open its recipe screen.
 */
public final class FtbRecipeKeys {
    private static IJeiRuntime runtime;
    private static KeyMapping showRecipe;
    private static KeyMapping showUses;

    private FtbRecipeKeys() {}

    static void setRuntime(IJeiRuntime jeiRuntime) {
        runtime = jeiRuntime;
    }

    public static void onKeyPressed(ScreenEvent.KeyPressed.Pre event) {
        Screen screen = event.getScreen();
        if (runtime == null || !screen.getClass().getName().startsWith("dev.ftb.mods.")) return;
        if (showRecipe == null) {
            for (KeyMapping key : Minecraft.getInstance().options.keyMappings) {
                if (key.getName().equals("key.jei.showRecipe")) showRecipe = key;
                else if (key.getName().equals("key.jei.showUses")) showUses = key;
            }
        }
        InputConstants.Key pressed = InputConstants.getKey(event.getKeyCode(), event.getScanCode());
        RecipeIngredientRole role;
        if (showRecipe != null && showRecipe.isActiveAndMatches(pressed)) role = RecipeIngredientRole.OUTPUT;
        else if (showUses != null && showUses.isActiveAndMatches(pressed)) role = RecipeIngredientRole.INPUT;
        else return;

        Minecraft mc = Minecraft.getInstance();
        double mouseX = mc.mouseHandler.xpos() * mc.getWindow().getGuiScaledWidth() / mc.getWindow().getScreenWidth();
        double mouseY = mc.mouseHandler.ypos() * mc.getWindow().getGuiScaledHeight() / mc.getWindow().getScreenHeight();
        Optional<IClickableIngredient<?>> hovered =
            runtime.getScreenHelper().getClickableIngredientUnderMouse(screen, mouseX, mouseY).findFirst();
        if (hovered.isEmpty()) return;

        runtime.getRecipesGui().show(
            runtime.getJeiHelpers().getFocusFactory().createFocus(role, hovered.get().getTypedIngredient()));
        event.setCanceled(true);
    }
}
