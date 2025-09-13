# Hyprland Dots by @JaKooLit

This repository contains a comprehensive set of configuration files for the [Hyprland](https://hyprland.org/) Wayland compositor. It offers a highly customizable and feature-rich experience, complete with a wide array of scripts and modular configuration options.

## Features

*   **Modular Configuration**: Settings are broken down into logical files (e.g., `Keybinds.conf`, `UserSettings.conf`), making customization straightforward.
*   **Extensive Script Library**: A wide range of scripts are included to manage everything from screen brightness and volume to wallpapers and system updates.
*   **User-Focused Customization**: The `UserConfigs` directory is dedicated to your personal settings, ensuring they are preserved when updating the main configuration.
*   **Dynamic Theming**: Scripts for `rofi` and other tools allow for dynamic theme changes.
*   **Pre-configured Keybindings**: A sensible set of default keybindings is provided, which can be easily viewed or overridden.

## Installation

1.  **Prerequisites**: Ensure you have Hyprland installed on your system.
2.  **Clone the Repository**:
    ```bash
    git clone https://github.com/JaKooLit/Hyprland-Dots ~/.config/hypr
    ```
3.  **Initial Setup**: The `initial-boot.sh` script will run once to set up initial wallpapers, themes, and other settings.

## Usage

After installation, Hyprland will automatically use the new configuration. For any personal customizations, it is highly recommended to use the files within the `UserConfigs` directory. This approach ensures that your modifications are not overwritten when the core configuration is updated.

### Keybindings

Default keybindings are defined in `configs/Keybinds.conf`. To add or override keybindings, use the `UserConfigs/UserKeybinds.conf` file.

To view all active keybindings, you can use the included `KeyBinds.sh` script, which displays them in a searchable `rofi` menu.

### Scripts

The `scripts` directory contains a variety of useful scripts to enhance your Hyprland experience:

*   `AirplaneMode.sh`: Toggles airplane mode.
*   `Brightness.sh`: Adjusts screen brightness.
*   `DarkLight.sh`: Switches between dark and light themes.
*   `GameMode.sh`: Toggles game mode for optimized performance.
*   `LockScreen.sh`: Locks the screen.
*   `ScreenShot.sh`: Takes screenshots.
*   `Volume.sh`: Controls the system volume.
*   ...and many more.

### Customization

The `UserConfigs` directory is the central hub for all your personal customizations. Here are some of the key files you can modify:

*   `01-UserDefaults.conf`: Set your default applications.
*   `ENVariables.conf`: Define environment variables.
*   `Startup_Apps.conf`: Specify applications to launch at startup.
*   `UserAnimations.conf`: Customize animations and effects.
*   `UserDecorations.conf`: Adjust window decorations.
*   `UserKeybinds.conf`: Define your custom keybindings.
*   `UserSettings.conf`: Override main Hyprland settings.
*   `WindowRules.conf`: Set rules for specific windows.

For more detailed guidance, refer to the `00-Readme` file in the `UserConfigs` directory.

## Contributing

Contributions are welcome! If you have any suggestions or improvements, please open an issue or submit a pull request.

## License

This project is licensed under the [MIT License](LICENSE).